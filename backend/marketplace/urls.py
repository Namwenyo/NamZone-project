from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

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
path('moderation/approve/', views.approve_items, name='approve_items'),
path('moderation/approve/<int:item_id>/', views.approve_item, name='approve_item'),
path('moderation/reject/<int:item_id>/', views.reject_item, name='reject_item'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)