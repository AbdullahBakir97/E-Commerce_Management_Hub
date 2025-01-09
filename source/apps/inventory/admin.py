from django.contrib import admin
from .models import Product, Category, Warehouse, InventoryItem, StockAlert, RestockOrder

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    list_filter = ('parent',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'price', 'active')
    search_fields = ('name', 'sku')
    list_filter = ('category', 'active')
    ordering = ('name',)

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity')
    search_fields = ('name', 'location')

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'quantity')
    search_fields = ('product__name', 'warehouse__name')
    list_filter = ('warehouse',)

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'threshold', 'alert_sent')
    search_fields = ('product__name', 'warehouse__name')
    list_filter = ('alert_sent', 'warehouse')

@admin.register(RestockOrder)
class RestockOrderAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'quantity', 'order_date', 'completed')
    search_fields = ('product__name', 'warehouse__name')
    list_filter = ('completed', 'warehouse', 'order_date')
    ordering = ('-order_date',)
