from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'shipping-rates', views.ShippingRateViewSet)
router.register(r'coupons', views.CouponViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
