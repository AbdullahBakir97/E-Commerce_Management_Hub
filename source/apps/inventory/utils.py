from .models import InventoryItem, StockAlert, RestockOrder

def update_stock(product, warehouse, quantity_change):
    item, created = InventoryItem.objects.get_or_create(product=product, warehouse=warehouse)
    item.quantity += quantity_change
    item.save()
    return item


def check_stock_alerts(product, warehouse):
    inventory_item = InventoryItem.objects.get(product=product, warehouse=warehouse)
    stock_alerts = StockAlert.objects.filter(product=product, warehouse=warehouse, alert_sent=False)
    for alert in stock_alerts:
        if inventory_item.quantity < alert.threshold:
            # Send alert logic here
            alert.alert_sent = True
            alert.save()


def create_restock_order(product, warehouse, quantity):
    return RestockOrder.objects.create(product=product, warehouse=warehouse, quantity=quantity)


