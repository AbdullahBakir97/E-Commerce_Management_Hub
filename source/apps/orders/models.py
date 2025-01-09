from django.db import models
from django.contrib.auth import get_user_model
from inventory.models import Product
from decimal import Decimal

User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    billing_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number
            last_order = Order.objects.order_by('-id').first()
            if last_order:
                last_number = int(last_order.order_number[3:])
                self.order_number = f'ORD{str(last_number + 1).zfill(8)}'
            else:
                self.order_number = 'ORD00000001'
        
        # Calculate totals
        self.subtotal = sum(item.get_total() for item in self.items.all())
        self.tax = self.subtotal * Decimal('0.15')  # 15% tax
        self.total = self.subtotal + self.shipping_cost + self.tax
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Order {self.order_number}'

    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    
    def get_total(self):
        return self.quantity * self.price

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

class ShippingRate(models.Model):
    name = models.CharField(max_length=100)
    carrier = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.carrier} - {self.name}'

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    max_uses = models.PositiveIntegerField(default=0)  # 0 means unlimited
    times_used = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def is_valid(self, order_value):
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if now < self.valid_from or now > self.valid_until:
            return False
            
        if self.max_uses > 0 and self.times_used >= self.max_uses:
            return False
            
        if order_value < self.minimum_order_value:
            return False
            
        return True

    def calculate_discount(self, order_value):
        if not self.is_valid(order_value):
            return Decimal('0')
            
        if self.discount_type == 'percentage':
            return order_value * (self.discount_value / Decimal('100'))
        else:
            return min(self.discount_value, order_value)  # Don't discount more than order value

    def __str__(self):
        return self.code
