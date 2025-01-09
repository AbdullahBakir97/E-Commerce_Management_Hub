from rest_framework import serializers
from .models import Order, OrderItem, ShippingRate, Coupon
from inventory.serializers import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, source='get_total')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_details', 'quantity', 'price', 'total']
        read_only_fields = ['price']

    def validate(self, data):
        # Ensure product has sufficient inventory
        product = data['product']
        quantity = data['quantity']
        inventory = product.inventory_items.first()
        
        if not inventory or inventory.quantity < quantity:
            raise serializers.ValidationError(
                f"Insufficient inventory for {product.name}. Available: {inventory.quantity if inventory else 0}"
            )
        return data

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'user', 'status', 'status_display', 
                 'payment_status', 'payment_status_display', 'shipping_address', 
                 'billing_address', 'created_at', 'updated_at', 'items',
                 'subtotal', 'shipping_cost', 'tax', 'total', 'tracking_number', 'notes']
        read_only_fields = ['order_number', 'subtotal', 'tax', 'total']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            product = item_data['product']
            # Set price to current product price
            OrderItem.objects.create(
                order=order,
                price=product.price,
                **item_data
            )
            
            # Update inventory
            inventory = product.inventory_items.first()
            if inventory:
                inventory.quantity -= item_data['quantity']
                inventory.save()
        
        return order

class ShippingRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingRate
        fields = ['id', 'name', 'carrier', 'rate', 'estimated_days', 'is_active']

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount_type', 'discount_value', 
                 'minimum_order_value', 'valid_from', 'valid_until',
                 'max_uses', 'times_used', 'is_active']
        read_only_fields = ['times_used']

    def validate(self, data):
        if data['valid_from'] >= data['valid_until']:
            raise serializers.ValidationError(
                "End date must be after start date"
            )
        return data
