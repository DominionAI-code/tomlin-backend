from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import (
    MenuItemViewSet, InventoryViewSet, EmployeeViewSet, LeasePaymentViewSet, 
    OrderViewSet, create_order, UserViewSet,
    financial_report, ExpenseViewSet, serve_media
)

router = DefaultRouter()
router.register(r'menu', MenuItemViewSet)
router.register(r'inventory', InventoryViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'leases', LeasePaymentViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'reports/expenses', ExpenseViewSet, basename='expenses')
router.register(r'users', UserViewSet)

urlpatterns = [
    # path('api/', include(router.urls)),
    path('', include(router.urls)),

    # Custom API views under /api/
    path('api/orders/create/', create_order, name="create_order"),
    path('api/financial-reports/', financial_report, name='financial-reports'),

    # Serving media (temporary workaround)
    re_path(r'^media/(?P<path>.*)$', serve_media),
]
