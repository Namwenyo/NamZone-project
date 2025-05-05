from django.contrib import admin
from .models import User, Category, Item

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone_number')
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'price', 'status')
    list_filter = ('status', 'category')