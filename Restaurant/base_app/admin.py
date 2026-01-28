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

