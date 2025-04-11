# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import financial_report
# from .views import (
#     MenuItemViewSet, InventoryViewSet, EmployeeViewSet, LeasePaymentViewSet, OrderViewSet, create_order, UserViewSet
# )

# router = DefaultRouter()
# router.register(r'menu', MenuItemViewSet)
# router.register(r'inventory', InventoryViewSet)
# router.register(r'employees', EmployeeViewSet)
# router.register(r'leases', LeasePaymentViewSet)
# router.register(r'orders', OrderViewSet, basename='order')
# router.register(r'users', UserViewSet)

# urlpatterns = [
#     path('', include(router.urls)),
#     path('orders/', create_order, name="create_order"),
#     path('financial-report/', financial_report, name='financial-report'),
#     path('api/', include(router.urls)),
# ]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MenuItemViewSet, InventoryViewSet, EmployeeViewSet, LeasePaymentViewSet, 
    OrderViewSet, create_order, UserViewSet,
    financial_report, ExpenseViewSet
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
    path('', include(router.urls)),
    path('api/', include(router.urls)),

    # Custom API views
    path('orders/create/', create_order, name="create_order"),
    path('financial-reports/', financial_report, name='financial-reports'),
]