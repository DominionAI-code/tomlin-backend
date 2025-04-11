from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Sum, F
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from datetime import date
from .models import CustomUser
from .models import MenuItem, Inventory, Employee, LeasePayment, Order, Expense
from .serializers import (
    MenuItemSerializer, InventorySerializer, EmployeeSerializer, LeasePaymentSerializer, OrderCreateSerializer, 
    OrderSerializer, UserSerializer, ExpenseSerializer
)

@api_view(['POST'])
def create_order(request):
    """
    Process an order: Deduct inventory and record sales
    """
    order_items = request.data.get('order_items', [])

    for item in order_items:
        try:
            menu_item = MenuItem.objects.get(id=item["item_id"])
            inventory_item = Inventory.objects.get(menu_item=menu_item)
            
            if inventory_item.stock >= item["quantity"]:
                inventory_item.stock -= item["quantity"]
                inventory_item.save()
            else:
                return Response({"error": f"Not enough stock for {menu_item.name}"}, status=400)
        except (MenuItem.DoesNotExist, Inventory.DoesNotExist):
            return Response({"error": "Invalid menu item or inventory missing"}, status=400)

        Order.objects.create(
            menu_item=menu_item,
            quantity=item["quantity"],
            total_price=menu_item.price * item["quantity"]
        )
    
    return Response({"message": "Order placed successfully!"}, status=201)

@api_view(['GET'])
def get_sales_report(request):
    total_sales = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('total_price'))['total'] or 0
    
    return Response({
        "total_sales": total_sales,
        "total_revenue": total_revenue
    })

# views.py

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    parser_classes = [MultiPartParser, FormParser]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

@api_view(['GET'])
def financial_report(request):
    today = date.today()

    # === SALES ===
    total_sales = Order.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0

    # === EXPENSES ===
    inventory_expense = Inventory.objects.aggregate(total=Sum(F('purchase_price') * F('quantity')))['total'] or 0
    lease_expense = LeasePayment.objects.filter(is_paid=True).aggregate(total=Sum('amount_due'))['total'] or 0
    total_expense = inventory_expense + lease_expense

    # === PROFIT ===
    profit = total_sales - total_expense

    # === SALES TRENDS ===
    daily_sales = Order.objects.filter(status='completed')\
        .annotate(day=TruncDay('date'))\
        .values('day')\
        .annotate(total=Sum('amount'))\
        .order_by('day')

    weekly_sales = Order.objects.filter(status='completed')\
        .annotate(week=TruncWeek('date'))\
        .values('week')\
        .annotate(total=Sum('amount'))\
        .order_by('week')

    monthly_sales = Order.objects.filter(status='completed')\
        .annotate(month=TruncMonth('date'))\
        .values('month')\
        .annotate(total=Sum('amount'))\
        .order_by('month')

    yearly_sales = Order.objects.filter(status='completed')\
        .annotate(year=TruncYear('date'))\
        .values('year')\
        .annotate(total=Sum('amount'))\
        .order_by('year')

    return Response({
        'summary': {
            'total_sales': total_sales,
            'inventory_expense': inventory_expense,
            'lease_expense': lease_expense,
            'total_expense': total_expense,
            'profit': profit,
        },
        'daily_sales': daily_sales,
        'weekly_sales': weekly_sales,
        'monthly_sales': monthly_sales,
        'yearly_sales': yearly_sales,
    })

class LeasePaymentViewSet(viewsets.ModelViewSet):
    queryset = LeasePayment.objects.all()
    serializer_class = LeasePaymentSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by('-date')
    serializer_class = ExpenseSerializer
