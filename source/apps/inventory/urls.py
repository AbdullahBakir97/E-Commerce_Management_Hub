from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'warehouses', views.WarehouseViewSet)
router.register(r'inventory-items', views.InventoryItemViewSet)
router.register(r'stock-alerts', views.StockAlertViewSet)
router.register(r'restock-orders', views.RestockOrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
