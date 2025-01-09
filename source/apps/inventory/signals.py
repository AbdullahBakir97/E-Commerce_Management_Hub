from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import InventoryItem, StockAlert
from .utils import check_stock_alerts

@receiver(post_save, sender=InventoryItem)
def handle_low_stock(sender, instance, **kwargs):
    check_stock_alerts(instance.product, instance.warehouse)
