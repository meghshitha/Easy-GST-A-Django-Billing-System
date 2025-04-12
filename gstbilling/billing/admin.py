# Register your models here if you have any
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Product, UserProfile, Bill, BillItem  # Add Bill and BillItem to imports

# First unregister all models if they're registered
for model in [UserProfile, Product, Bill, BillItem]:
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass

# Now register them with their admin classes
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'gstin', 'phone_number')
    search_fields = ('user__username', 'business_name', 'gstin')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'hsn', 'gst', 'price')
    search_fields = ('name', 'hsn')
    list_filter = ('user', 'gst')

class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 0

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('bill_no', 'user', 'customer_name', 'date', 'grand_total')
    search_fields = ('bill_no', 'customer_name', 'customer_phone')
    list_filter = ('user', 'date')
    inlines = [BillItemInline]

# User Profile Admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Unregister if already registered
from django.contrib.admin.sites import AlreadyRegistered
try:
    admin.site.unregister(UserProfile)
except (admin.sites.NotRegistered, AlreadyRegistered):
    pass

@admin.register(BillItem)
class BillItemAdmin(admin.ModelAdmin):
    list_display = ('bill', 'product', 'quantity', 'total')
    search_fields = ('bill__bill_no', 'product__name')
