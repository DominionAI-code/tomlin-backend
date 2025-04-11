from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.timezone import now

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

# Menu Management
class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/', null=True, blank=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ('FOOD', 'Food'),  # The first value is stored in DB, second is displayed
            ('DRINKS', 'Drinks'),
            ('DESSERT', 'Dessert'),
        ]
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # created_at = models.DateTimeField(default=timezone.now)
    # updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

# Inventory Management
class Inventory(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, null=True, blank=True)  # Allow NULL values
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.menu_item.name if self.menu_item else self.item_name} - {self.quantity} left"


# Employee Management
class Employee(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)  # Make user optional
    first_name = models.CharField(max_length=25, default="Unknown")
    last_name = models.CharField(max_length=20, default="Unknown")
    email = models.EmailField(default="admin@example.com")
    position = models.CharField(max_length=25, default="admin")
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    hire_date = models.DateField()

# Lease Payment Tracking
class LeasePayment(models.Model):
    restaurant_name = models.CharField(max_length=100)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.restaurant_name} - {self.amount_due} due on {self.due_date}"

# Order Management
class Order(models.Model):
    customer_id = models.CharField(max_length=100, default="N/A")
    customer_name = models.CharField(max_length=255, default="Unknown")  # Set a reasonable default
    date = models.DateField(default=now)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
    max_length=50,
    choices=[('pending', 'Pending'), ('completed', 'Completed')],
    default='pending'  # Set 'pending' as the default value
)


    def save(self, *args, **kwargs):
        if self.pk:  # Ensure the order exists before summing prices
            self.amount = sum(item.menu_item.price * item.quantity for item in self.order_items.all())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} - {self.customer_name}"

# Order Item (For multiple items in an order)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    menu_item = models.ForeignKey("MenuItem", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ("Utilities", "Utilities"),
        ("Rent", "Rent"),
        ("Salaries", "Salaries"),
        ("Supplies", "Supplies"),
        ("Maintenance", "Maintenance"),
        ("Marketing", "Marketing"),
        ("Insurance", "Insurance"),
        ("Other", "Other"),
    ]

    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="Other")

    def __str__(self):
        return f"{self.description} - ${self.amount}"
