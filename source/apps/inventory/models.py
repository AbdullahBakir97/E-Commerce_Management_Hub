from django.db import models



class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['name']

class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="subcategories")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField(help_text="Maximum number of items the warehouse can hold.")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Warehouse"
        verbose_name_plural = "Warehouses"
        ordering = ['name']

class InventoryItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventory_items")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="inventory_items")
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'warehouse')

    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.active = self.quantity > 0
        self.product.save()

class StockAlert(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_alerts")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stock_alerts")
    threshold = models.PositiveIntegerField(help_text="Alert when quantity falls below this value.")
    alert_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Alert for {self.product.name} in {self.warehouse.name}"

    class Meta:
        unique_together = ('product', 'warehouse')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.quantity < self.threshold and not self.alert_sent:
            self.alert_sent = True
            self.save()

class RestockOrder(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="restock_orders")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="restock_orders")
    quantity = models.PositiveIntegerField()
    order_date = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Restock Order: {self.product.name} ({self.quantity})"

    class Meta:
        verbose_name = "Restock Order"
        verbose_name_plural = "Restock Orders"
        ordering = ['-order_date']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.active = self.quantity > 0
        self.product.save()