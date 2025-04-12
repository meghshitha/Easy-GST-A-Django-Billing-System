from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Bill, Product

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_business_name')
    
    def get_business_name(self, obj):
        return obj.userprofile.business_name if hasattr(obj, 'userprofile') else ''
    get_business_name.short_description = 'Business Name'

class BillAdmin(admin.ModelAdmin):
    list_display = ('invoice_no', 'user', 'date', 'total_amount')
    list_filter = ('date', 'user')
    search_fields = ('invoice_no', 'user__username')
    readonly_fields = ('date',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'gst', 'total_price')
    search_fields = ('name',)

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Bill, BillAdmin) 