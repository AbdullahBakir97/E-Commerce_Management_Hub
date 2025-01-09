from rest_framework import serializers
from .models import Product, Category, Warehouse, InventoryItem, StockAlert, RestockOrder

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'description', 'category', 'category_name', 'price', 'active']

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class InventoryItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = ['id', 'product', 'product_name', 'warehouse', 'warehouse_name', 'quantity']

class StockAlertSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = StockAlert
        fields = ['id', 'product', 'product_name', 'warehouse', 'warehouse_name', 'threshold', 'alert_sent']

class RestockOrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = RestockOrder
        fields = ['id', 'product', 'product_name', 'warehouse', 'warehouse_name', 
                 'quantity', 'order_date', 'completed']
