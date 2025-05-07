from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Main Pages
    path('', views.home, name='home'),
    path('list/', views.list_item, name='list'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('seller-dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('edit-profile/', views.edit_profile, name='edit_profile'), 
    # Category Pages
    path('appliance/', views.appliance, name='appliance'),
    path('laptops/', views.laptops, name='laptops'),
    path('phones/', views.phones, name='phones'),
    path('clothing/', views.clothing, name='clothing'),
    path('home-goods/', views.home_goods, name='homegoods'),
    path('vehicles/', views.vehicles, name='vehicles'),
    path('beauty/', views.beauty, name='beauty'),
    path('other/', views.other, name='other'),
    
    # Admin/Moderation
    path('approve-items/', views.approve_items, name='approve_items'),
]