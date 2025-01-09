from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Order, OrderItem, ShippingRate, Coupon
from .serializers import (
    OrderSerializer, 
    OrderItemSerializer,
    ShippingRateSerializer,
    CouponSerializer
)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status not in ['pending', 'processing']:
            return Response(
                {'error': 'Cannot cancel order in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Restore inventory
        for item in order.items.all():
            inventory = item.product.inventory_items.first()
            if inventory:
                inventory.quantity += item.quantity
                inventory.save()

        order.status = 'cancelled'
        order.save()
        
        return Response({'status': 'Order cancelled successfully'})

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()
        
        return Response({'status': f'Order status updated to {new_status}'})

    @action(detail=True, methods=['post'])
    def add_tracking(self, request, pk=None):
        order = self.get_object()
        tracking_number = request.data.get('tracking_number')
        
        if not tracking_number:
            return Response(
                {'error': 'Tracking number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.tracking_number = tracking_number
        order.status = 'shipped'
        order.save()
        
        return Response({'status': 'Tracking information added successfully'})

class ShippingRateViewSet(viewsets.ModelViewSet):
    queryset = ShippingRate.objects.filter(is_active=True)
    serializer_class = ShippingRateSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        return super().get_permissions()

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def validate_coupon(self, request, pk=None):
        coupon = self.get_object()
        order_value = request.data.get('order_value')
        
        if not order_value:
            return Response(
                {'error': 'Order value is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if coupon.is_valid(order_value):
            discount = coupon.calculate_discount(order_value)
            return Response({
                'valid': True,
                'discount': discount,
                'final_value': order_value - discount
            })
        
        return Response({'valid': False, 'message': 'Coupon is not valid'})
