from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F
from .models import Product, Category, Warehouse, InventoryItem, StockAlert, RestockOrder
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    WarehouseSerializer,
    InventoryItemSerializer,
    StockAlertSerializer,
    RestockOrderSerializer
)
from .utils import update_stock, check_stock_alerts, create_restock_order

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    @action(detail=True, methods=['post'])
    def update_inventory(self, request, pk=None):
        product = self.get_object()
        warehouse_id = request.data.get('warehouse')
        quantity_change = request.data.get('quantity_change')
        
        try:
            warehouse = Warehouse.objects.get(id=warehouse_id)
            inventory_item = update_stock(product, warehouse, quantity_change)
            return Response({
                'status': 'success',
                'current_quantity': inventory_item.quantity
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    @action(detail=True)
    def products(self, request, pk=None):
        category = self.get_object()
        products = Product.objects.filter(category=category)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    
    @action(detail=True)
    def inventory(self, request, pk=None):
        warehouse = self.get_object()
        inventory = InventoryItem.objects.filter(warehouse=warehouse)
        serializer = InventoryItemSerializer(inventory, many=True)
        return Response(serializer.data)

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    
    def perform_create(self, serializer):
        inventory_item = serializer.save()
        check_stock_alerts(inventory_item.product, inventory_item.warehouse)

class StockAlertViewSet(viewsets.ModelViewSet):
    queryset = StockAlert.objects.all()
    serializer_class = StockAlertSerializer
    
    @action(detail=True, methods=['post'])
    def reset_alert(self, request, pk=None):
        alert = self.get_object()
        alert.alert_sent = False
        alert.save()
        return Response({'status': 'alert reset'})

class RestockOrderViewSet(viewsets.ModelViewSet):
    queryset = RestockOrder.objects.all()
    serializer_class = RestockOrderSerializer
    
    @action(detail=True, methods=['post'])
    def complete_order(self, request, pk=None):
        order = self.get_object()
        if not order.completed:
            order.completed = True
            order.save()
            update_stock(order.product, order.warehouse, order.quantity)
            return Response({'status': 'order completed'})
        return Response({
            'status': 'error',
            'message': 'Order already completed'
        }, status=status.HTTP_400_BAD_REQUEST)
