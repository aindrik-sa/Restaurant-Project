"""
URL configuration for Restaurant project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from base_app.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',HomeView,name="Home"),
    path('about',AboutView,name="About"),
    path('menu/',MenuView,name="Menu"),
    path('book_table',BookTableView,name="Book_table"),
    path('feedback/',FeedbackView,name="Feedback"),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('add_to_cart/<int:item_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart_view, name='Cart'),
    path('remove_from_cart/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('update_cart/<int:item_id>/<str:action>/', update_cart, name='update_cart'),
    path('checkout/', checkout, name='checkout'),
    path('payment/<int:order_id>/', payment_view, name='payment_view'),
    path('profile/', profile_view, name='profile'),
    path('item/<int:item_id>/', item_detail, name='item_detail'),
    path('wishlist/<int:item_id>/', toggle_wishlist, name='toggle_wishlist'),
    path('logout/', logout_view, name='logout'),
    
    # API endpoints for AJAX
    path('api/cart/count/', api_get_cart_count, name='api_cart_count'),
    path('api/cart/add/<int:item_id>/', api_add_to_cart, name='api_add_to_cart'),
    path('api/wishlist/toggle/<int:item_id>/', api_toggle_wishlist, name='api_toggle_wishlist'),
    
    # Feature 1: Order Details
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    
    # Feature 4: Coupons
    path('apply-coupon/', apply_coupon, name='apply_coupon'),
    
    # Feature 5: Staff Dashboard
    path('staff/dashboard/', staff_dashboard, name='staff_dashboard'),
    path('staff/order/<int:order_id>/status/', update_order_status, name='update_order_status'),
    
    # Feature 6: Analytics
    path('staff/analytics/', sales_analytics, name='sales_analytics'),
    path('api/sales-data/', api_sales_data, name='api_sales_data'),

] 
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)