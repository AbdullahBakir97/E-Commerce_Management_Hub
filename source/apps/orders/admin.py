from django.contrib import admin
from .models import Order, OrderItem, ShippingRate, Coupon

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('get_total',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'payment_status', 'created_at', 'total')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__email', 'shipping_address')
    readonly_fields = ('order_number', 'subtotal', 'tax', 'total')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Addresses', {
            'fields': ('shipping_address', 'billing_address')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'shipping_cost', 'tax', 'total')
        }),
        ('Shipping Details', {
            'fields': ('tracking_number', 'notes')
        }),
    )

@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    list_display = ('name', 'carrier', 'rate', 'estimated_days', 'is_active')
    list_filter = ('carrier', 'is_active')
    search_fields = ('name', 'carrier')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'valid_from', 
                   'valid_until', 'times_used', 'is_active')
    list_filter = ('discount_type', 'is_active', 'valid_from', 'valid_until')
    search_fields = ('code',)
    readonly_fields = ('times_used',)
    fieldsets = (
        ('Coupon Information', {
            'fields': ('code', 'discount_type', 'discount_value')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until', 'is_active')
        }),
        ('Usage', {
            'fields': ('minimum_order_value', 'max_uses', 'times_used')
        }),
    )
