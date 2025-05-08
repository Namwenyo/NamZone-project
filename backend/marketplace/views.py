from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import SignUpForm, ItemForm
from .models import Item, Category, SellerProfile, User
from .backends import CustomAuthBackend
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from .forms import SellerSignupForm
from django.contrib.auth.backends import ModelBackend
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.views import redirect_to_login
from .forms import EditProfileForm

def home(request):
    featured_items = Item.objects.filter(status='A').order_by('-created_at')[:8]
    return render(request, 'marketplace/index.html', {'featured_items': featured_items})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('marketplace:home')


def list_item(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.save()
            return redirect('marketplace:seller_dashboard')  # redirect to seller dashboard
    else:
        form = ItemForm()
    return render(request, 'marketplace/list.html', {'form': form})

@login_required
def seller_dashboard(request):
    user = request.user

    # Ensure only regular users access this dashboard
    if user.user_type != user.UserType.REGULAR:
        return redirect('marketplace:home')

    # Get seller profile and their listed items
    seller_profile = SellerProfile.objects.get(user=user)
    items = Item.objects.filter(seller=user)

    context = {
        'profile': seller_profile,
        'items': items,
    }

    return render(request, 'marketplace/seller_dashboard.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Only create profile for non-admin users
                if not user.is_superuser:
                    SellerProfile.objects.get_or_create(user=user)
                
                login(request, user)
                # Redirect based on user role
                if user.is_superuser:
                    return redirect('marketplace:admin_dashboard')
                else:
                    return redirect('marketplace:seller_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AuthenticationForm()
    
    return render(request, 'marketplace/login.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = SellerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Set backend and log in
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            messages.success(request, "Registration successful!")
            return redirect('marketplace:seller_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SellerSignupForm()
    
    return render(request, 'marketplace/signup.html', {'form': form})


def appliance(request):
    items = Item.objects.filter(category__name='Appliance', status='A').order_by('-created_at')
    return render(request, 'marketplace/appliance.html', {'items': items})

def laptops(request):
    items = Item.objects.filter(category__name='Laptops', status='A').order_by('-created_at')
    return render(request, 'marketplace/laptops.html', {'items': items})

def phones(request):
    items = Item.objects.filter(category__name='Phones', status='A').order_by('-created_at')
    return render(request, 'marketplace/phones.html', {'items': items})

def clothing(request):
    items = Item.objects.filter(category__name='Clothing', status='A').order_by('-created_at')
    return render(request, 'marketplace/clothing.html', {'items': items})

def home_goods(request):
    items = Item.objects.filter(category__name='Home Goods', status='A').order_by('-created_at')
    return render(request, 'marketplace/homegoods.html', {'items': items})

def vehicles(request):
    items = Item.objects.filter(category__name='Vehicles', status='A').order_by('-created_at')
    return render(request, 'marketplace/vehicles.html', {'items': items})

def beauty(request):
    items = Item.objects.filter(category__name='Beauty', status='A').order_by('-created_at')
    return render(request, 'marketplace/beauty.html', {'items': items})

def other(request):
    items = Item.objects.filter(category__name='Other', status='A').order_by('-created_at')
    return render(request, 'marketplace/other.html', {'items': items})

@staff_member_required
def admin_dashboard(request):
    return render(request, 'marketplace/admin-dashboard.html')

@staff_member_required
def approve_items(request):
    pending_items = Item.objects.filter(is_approved=False)
    return render(request, 'marketplace/approve_items.html', {'pending_items': pending_items})

@staff_member_required
@require_POST
def approve_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    item.is_approved = True
    item.status = 'A'
    item.save()
    return redirect('marketplace:approve_items')

@staff_member_required
@require_POST
def reject_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    item.delete()  # or use a is_rejected flag instead of deleting
    return redirect('marketplace:approve_items')

# Admin Views
# @staff_member_required
# def admin_dashboard(request):
#     stats = {
#         'total_items': Item.objects.count(),
#         'pending_items': Item.objects.filter(status='P').count(),
#         'approved_items': Item.objects.filter(status='A').count(),
#         'rejected_items': Item.objects.filter(status='R').count(),
#         'total_users': User.objects.count(),
#     }
#     return render(request, 'marketplace/admin-dashboard.html', {'stats': stats})

# @staff_member_required
# def approve_items(request):
#     pending_items = Item.objects.filter(status='P').order_by('created_at')
    
#     if request.method == 'POST':
#         item_id = request.POST.get('item_id')
#         action = request.POST.get('action')
#         item = get_object_or_404(Item, id=item_id)
        
#         if action == 'approve':
#             item.status = 'A'
#             messages.success(request, f"Item '{item.title}' approved!")
#         else:
#             item.status = 'R'
#             messages.warning(request, f"Item '{item.title}' rejected.")
#         item.save()
#         return redirect('marketplace:approve_items')
    
#     return render(request, 'marketplace/approve_items.html', {'items': pending_items})

@login_required
def edit_profile(request):
    user = request.user

    # Ensure only regular users can edit their profile
    if user.user_type != user.UserType.REGULAR:
        return redirect('marketplace:home')

    # Get the seller profile
    profile = SellerProfile.objects.get(user=user)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('marketplace:seller_dashboard')
    else:
        form = EditProfileForm(instance=profile)

    context = {
        'form': form
    }

    return render(request, 'marketplace/edit_profile.html', context)