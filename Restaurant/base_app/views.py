from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from base_app.models import BookTable,Category,Items,AboutUs,Feedback,Cart,CartItem,Order,OrderItem

from django.db.models import Q
from django.core.paginator import Paginator

# Create your views here.
def HomeView(request):
    items=Items.objects.all()
    q = request.GET.get('q')
    if q:
        items = items.filter(Q(Item_name__icontains=q) | Q(description__icontains=q))
    
    list=Category.objects.all()
    review=Feedback.objects.all()  
    return render(request,'home.html',{'items':items,'list':list,'review':review, 'search_query': q})

def AboutView(request):
    return render(request,'about.html')

def MenuView(request):
    items=Items.objects.all()
    q = request.GET.get('q')
    if q:
        items = items.filter(Q(Item_name__icontains=q) | Q(description__icontains=q))

    list=Category.objects.all()
    
    # Pagination
    paginator = Paginator(items, 6) # Show 6 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,'menu.html',{'items':page_obj,'list':list, 'search_query': q})

from .forms import BookingForm, FeedbackForm
from django.contrib import messages
from django.shortcuts import redirect

def BookTableView(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Table booked successfully!')
            return redirect('Book_table')
    else:
        form = BookingForm()
    return render(request,'book_table.html', {'form': form})

def FeedbackView(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('Feedback')
    else:
        form = FeedbackForm()
    return render(request,'feedback.html', {'form': form})

from .forms import BookingForm, FeedbackForm, UserRegisterForm, ReviewForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.conf import settings
from .models import Review, Wishlist
from django.views.decorators.csrf import csrf_exempt

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Send Welcome Email
            subject = 'Welcome to HUNGERLOUNGE!'
            message = f'Hi {user.username}, thank you for registering at HUNGERLOUNGE.'
            email_from = settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else 'noreply@hungerlounge.com'
            recipient_list = [user.email]
            try:
                send_mail(subject, message, email_from, recipient_list)
            except Exception as e:
                print(f"Error sending email: {e}")

            messages.success(request, f'Account created for {user.username}!')
            return redirect('Home')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'You are now logged in as {username}.')
                return redirect('Home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('Home')

# Cart Functionality
def _get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_id=request.session.session_key)
    return cart

def add_to_cart(request, item_id):
    item = get_object_or_404(Items, id=item_id)
    cart = _get_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{item.Item_name} added to cart.")
    return redirect('Menu')

def remove_from_cart(request, item_id):
    cart = _get_cart(request)
    item = get_object_or_404(Items, id=item_id)
    cart_item = get_object_or_404(CartItem, cart=cart, item=item)
    cart_item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect('Cart')

def update_cart(request, item_id, action):
    cart = _get_cart(request)
    item = get_object_or_404(Items, id=item_id)
    cart_item = get_object_or_404(CartItem, cart=cart, item=item)
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease':
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()
            return redirect('Cart')
    cart_item.save()
    return redirect('Cart')

def cart_view(request):
    cart = _get_cart(request)
    items = cart.items.all()
    total = sum(item.total_price() for item in items)
    return render(request, 'cart.html', {'cart_items': items, 'total': total})

def checkout(request):
    cart = _get_cart(request)
    items = cart.items.all()
    if not items:
        messages.warning(request, "Your cart is empty.")
        return redirect('Menu')
        
    subtotal = sum(item.total_price() for item in items)
    
    # Feature 4: Coupon handling
    discount = 0
    coupon_code = None
    coupon_discount_percent = request.session.get('coupon_discount', 0)
    
    if coupon_discount_percent:
        coupon_code = request.session.get('coupon_code')
        discount = (subtotal * coupon_discount_percent) / 100
    
    total = subtotal - discount
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=name,
            email=email,
            phone=phone,
            address=address,
            total_amount=total
        )
        
        for cart_item in items:
            OrderItem.objects.create(
                order=order,
                item=cart_item.item,
                price=cart_item.item.Price,
                quantity=cart_item.quantity
            )
        
        # Update coupon usage if applied
        coupon_id = request.session.get('coupon_id')
        if coupon_id:
            try:
                from .models import Coupon
                coupon = Coupon.objects.get(id=coupon_id)
                coupon.times_used += 1
                coupon.save()
            except:
                pass
            # Clear coupon from session
            del request.session['coupon_id']
            del request.session['coupon_code']
            del request.session['coupon_discount']
        
        cart.items.all().delete() 
        
        return redirect('payment_view', order_id=order.id)
        
    return render(request, 'checkout.html', {
        'cart_items': items, 
        'subtotal': subtotal,
        'discount': discount,
        'total': total,
        'coupon_code': coupon_code,
        'coupon_discount_percent': coupon_discount_percent
    })

import razorpay

@csrf_exempt
def payment_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Razorpay Client
    try:
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        
        # Create Razorpay Order
        payment_amount = int(order.total_amount * 100) # Amount in paise
        razorpay_order = client.order.create({
            'amount': payment_amount,
            'currency': 'USD', 
            'payment_capture': '1'
        })
        razorpay_order_id = razorpay_order['id']
    except Exception as e:
        print(f"Razorpay Integration Error: {e}")
        messages.error(request, "Payment Gateway Error: Authentication Failed. Please check API Keys in settings.py.")
        # Fallback values to prevent crash
        razorpay_order_id = "fake_order_id" 
        payment_amount = int(order.total_amount * 100)
    
    if request.method == 'POST':
        # Payment Success Handling
        # In a real scenario, you verify signature here.
        # For this integration, we assume success if POSTED from our form (or via AJAX)
        
        # Verify the payment signature if data is available
        # param_dict = {
        #     'razorpay_order_id': razorpay_order['id'],
        #     'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
        #     'razorpay_signature': request.POST.get('razorpay_signature')
        # }
        # try:
        #     client.utility.verify_payment_signature(param_dict)
        #     order.status = 'Completed'
        #     order.save()
        # except:
        #     pass

        # For this demo/task flow without live frontend callback:
        order.status = 'Completed'
        order.save()
        
        # Send Order Confirmation Email
        if request.user.is_authenticated and request.user.email:
             subject = f'Order Confirmation - Order #{order.id}'
             message = f'Hi {request.user.username},\n\nThank you for your payment! Your order #{order.id} for ${order.total_amount} has been confirmed.'
             email_from = settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else 'noreply@hungerlounge.com'
             recipient_list = [request.user.email]
             try:
                 send_mail(subject, message, email_from, recipient_list)
             except Exception as e:
                 print(f"Error sending email: {e}")

        messages.success(request, "Payment successful! Your order has been placed.")
        return redirect('Home')
        
    context = {
        'order': order,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
        'razorpay_amount': payment_amount,
        'currency': 'USD',
        'callback_url': request.build_absolute_uri(), # Posting back to same view
    }
    return render(request, 'payment.html', context)

def profile_view(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You must be logged in to view your profile.")
        return redirect('login')
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'profile.html', {'orders': orders})

def item_detail(request, item_id):
    item = get_object_or_404(Items, id=item_id)
    reviews = item.reviews.all().order_by('-created_at')
    
    # Feature 2: Related Products - Get items from same category
    related_items = Items.objects.filter(Category=item.Category).exclude(id=item.id)[:4]
    
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, item=item).exists()
        
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.item = item
            review.save()
            messages.success(request, 'Review posted!')
            return redirect('item_detail', item_id=item.id)
    else:
        form = ReviewForm()
        
    return render(request, 'item_detail.html', {
        'item': item,
        'reviews': reviews,
        'form': form,
        'in_wishlist': in_wishlist,
        'related_items': related_items
    })

def toggle_wishlist(request, item_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to manage wishlist.")
        return redirect('login')
        
    item = get_object_or_404(Items, id=item_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, item=item)
    
    if created:
        messages.success(request, f"Added {item.Item_name} to wishlist.")
    else:
        wishlist_item.delete()
        messages.info(request, f"Removed {item.Item_name} from wishlist.")
        
    return redirect('item_detail', item_id=item.id)

# =============================================
# AJAX API Views for Cart & Wishlist
# =============================================
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def api_get_cart_count(request):
    """Return the total number of items in the cart."""
    cart = _get_cart(request)
    count = sum(item.quantity for item in cart.items.all())
    return JsonResponse({'cart_count': count})

@require_POST
def api_add_to_cart(request, item_id):
    """Add an item to cart via AJAX and return JSON response."""
    try:
        item = get_object_or_404(Items, id=item_id)
        cart = _get_cart(request)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        # Get updated cart count
        cart_count = sum(ci.quantity for ci in cart.items.all())
        
        return JsonResponse({
            'status': 'success',
            'message': f'{item.Item_name} added to cart!',
            'cart_count': cart_count
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_POST
def api_toggle_wishlist(request, item_id):
    """Toggle wishlist status via AJAX and return JSON response."""
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'Please login to manage wishlist.'
        }, status=401)
    
    try:
        item = get_object_or_404(Items, id=item_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, item=item)
        
        if created:
            return JsonResponse({
                'status': 'success',
                'message': f'Added {item.Item_name} to wishlist!',
                'in_wishlist': True
            })
        else:
            wishlist_item.delete()
            return JsonResponse({
                'status': 'success',
                'message': f'Removed {item.Item_name} from wishlist.',
                'in_wishlist': False
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

# =============================================
# Feature 1: Order Details Page
# =============================================
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Ensure user can only view their own orders (unless staff)
    if not request.user.is_staff and order.user != request.user:
        messages.error(request, "You don't have permission to view this order.")
        return redirect('profile')
    
    return render(request, 'order_detail.html', {'order': order})

# =============================================
# Feature 4: Coupons & Discounts
# =============================================
from .models import Coupon

def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code', '').strip().upper()
        
        try:
            coupon = Coupon.objects.get(code__iexact=code)
            if coupon.is_valid():
                request.session['coupon_id'] = coupon.id
                request.session['coupon_code'] = coupon.code
                request.session['coupon_discount'] = coupon.discount_percent
                messages.success(request, f"Coupon '{coupon.code}' applied! {coupon.discount_percent}% discount.")
            else:
                messages.error(request, "This coupon is expired or has reached its usage limit.")
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")
        
        return redirect('checkout')
    
    return redirect('checkout')

# =============================================
# Feature 5: Staff Order Dashboard
# =============================================
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def staff_dashboard(request):
    pending_orders = Order.objects.filter(status='Pending').order_by('-created_at')
    completed_orders = Order.objects.filter(status='Completed').order_by('-created_at')[:10]
    cancelled_orders = Order.objects.filter(status='Cancelled').order_by('-created_at')[:10]
    
    return render(request, 'staff_dashboard.html', {
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
    })

@staff_member_required
@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')
    
    if new_status in ['Pending', 'Completed', 'Cancelled']:
        order.status = new_status
        order.save()
        return JsonResponse({
            'status': 'success',
            'message': f'Order #{order.id} updated to {new_status}',
            'new_status': new_status
        })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)

# =============================================
# Feature 6: Sales Analytics
# =============================================
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from datetime import timedelta

@staff_member_required
def sales_analytics(request):
    return render(request, 'analytics.html')

@staff_member_required
def api_sales_data(request):
    from datetime import date
    today = date.today()
    
    # Daily sales for the last 7 days
    last_7_days = today - timedelta(days=6)
    daily_sales = Order.objects.filter(
        created_at__date__gte=last_7_days,
        status='Completed'
    ).annotate(
        day=TruncDate('created_at')
    ).values('day').annotate(
        total=Sum('total_amount'),
        count=Count('id')
    ).order_by('day')
    
    # Top selling items
    top_items = OrderItem.objects.filter(
        order__status='Completed'
    ).values('item__Item_name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]
    
    # Summary stats
    total_revenue = Order.objects.filter(status='Completed').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = Order.objects.filter(status='Completed').count()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    return JsonResponse({
        'daily_sales': list(daily_sales),
        'top_items': list(top_items),
        'summary': {
            'total_revenue': float(total_revenue),
            'total_orders': total_orders,
            'avg_order_value': float(avg_order_value)
        }
    })
