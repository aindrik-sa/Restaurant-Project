from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    Category=models.CharField(max_length=15)

    def __str__(self):
        return self.Category
    

class Items(models.Model):
    Item_name=models.CharField(max_length=15)
    Price=models.IntegerField()
    description=models.TextField(blank=False)
    Image=models.ImageField(upload_to='Items/')
    Category=models.ForeignKey(Category,related_name='Category_name',on_delete=models.CASCADE)

    def __str__(self):
        return self.Item_name
        
class AboutUs(models.Model):
    Description=models.TextField(blank=False)


        
class Feedback(models.Model):
    User_name=models.CharField( max_length=15)
    Description=models.TextField(blank=False)
    Rating=models.IntegerField()
    Image=models.ImageField(upload_to='Items/',blank=True)
    
    def __str__(self):
        return self.User_name

class BookTable(models.Model):
    TIME_SLOTS = [
        ('12:00', '12:00 PM'),
        ('13:00', '1:00 PM'),
        ('14:00', '2:00 PM'),
        ('18:00', '6:00 PM'),
        ('19:00', '7:00 PM'),
        ('20:00', '8:00 PM'),
        ('21:00', '9:00 PM'),
    ]
    MAX_TABLES_PER_SLOT = 10  # Maximum bookings per time slot
    
    Name=models.CharField( max_length=15)
    Phone_number=models.CharField(max_length=15)
    Email=models.EmailField()
    Total_person=models.IntegerField()
    Booking_date=models.DateField()
    Booking_time=models.CharField(max_length=10, choices=TIME_SLOTS, default='19:00')

    def __str__(self):
        return f"{self.Name} - {self.Booking_date} at {self.Booking_time}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user if self.user else 'Guest'}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.item.Price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.item.Item_name}"

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.Item_name} in Order {self.order.id}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Items, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.item.Item_name}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'item')

    def __str__(self):
        return f"{self.user.username} - {self.item.Item_name}"

# Coupon Model for Discounts
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.IntegerField(default=10)  # Percentage discount
    valid_from = models.DateField()
    valid_until = models.DateField()
    is_active = models.BooleanField(default=True)
    usage_limit = models.IntegerField(default=100)  # Max times coupon can be used
    times_used = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.code} - {self.discount_percent}% off"

    def is_valid(self):
        from datetime import date
        today = date.today()
        return (
            self.is_active and
            self.valid_from <= today <= self.valid_until and
            self.times_used < self.usage_limit
        )