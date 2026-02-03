from django.contrib import admin

from base_app.models import*


admin.site.register(Category)
admin.site.register(Items)
admin.site.register(AboutUs)
admin.site.register(Feedback)
admin.site.register(BookTable)
admin.site.register(Cart)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('item', 'price', 'quantity')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'phone', 'email')
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)
admin.site.register(Review)
admin.site.register(Wishlist)

# Coupon Admin
from base_app.models import Coupon

class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'valid_from', 'valid_until', 'is_active', 'times_used', 'usage_limit')
    list_filter = ('is_active', 'valid_from', 'valid_until')
    search_fields = ('code',)
    list_editable = ('is_active',)

admin.site.register(Coupon, CouponAdmin)
