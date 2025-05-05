from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from networkx import reverse
from .forms import SignUpForm, ItemForm
from .models import Item, Category, User
from .backends import CustomAuthBackend 

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
            return redirect(f'{reverse("marketplace:login")}?next={reverse("marketplace:list")}')
       
        form = ItemForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.save()
            messages.success(request, "Your item has been submitted for approval!")
            return redirect('marketplace:home')
    else:
        form = ItemForm(user=request.user)
    
    return render(request, 'marketplace/list.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('marketplace:home')
    
    next_url = request.GET.get('next', '')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.POST.get('next') or request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            if user.is_staff:
                return redirect('marketplace:admin_dashboard')
            return redirect('marketplace:home')
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, 'marketplace/login.html', {
        'next': request.GET.get('next', '')
    })

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('marketplace:home')
        
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Explicitly specify which backend to use
            backend = CustomAuthBackend()
            login(request, user, backend='marketplace.backends.CustomAuthBackend')
            
            messages.success(request, "Account created successfully!")
            return redirect('marketplace:home')
    else:
        form = SignUpForm()
    
    return render(request, 'marketplace/signup.html', {'form': form})

# Category Views (keeping your original separate views)
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

# Admin Views
@staff_member_required
def admin_dashboard(request):
    stats = {
        'total_items': Item.objects.count(),
        'pending_items': Item.objects.filter(status='P').count(),
        'approved_items': Item.objects.filter(status='A').count(),
        'rejected_items': Item.objects.filter(status='R').count(),
        'total_users': User.objects.count(),
    }
    return render(request, 'marketplace/admin-dashboard.html', {'stats': stats})

@staff_member_required
def approve_items(request):
    pending_items = Item.objects.filter(status='P').order_by('created_at')
    
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        action = request.POST.get('action')
        item = get_object_or_404(Item, id=item_id)
        
        if action == 'approve':
            item.status = 'A'
            messages.success(request, f"Item '{item.title}' approved!")
        else:
            item.status = 'R'
            messages.warning(request, f"Item '{item.title}' rejected.")
        item.save()
        return redirect('marketplace:approve_items')
    
    return render(request, 'marketplace/approve_items.html', {'items': pending_items})