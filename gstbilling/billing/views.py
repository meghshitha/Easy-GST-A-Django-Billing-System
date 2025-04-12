from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Product, UserProfile, Bill, BillItem
from django.contrib.auth.decorators import login_required
from decimal import Decimal
import json
import random
import string
from django.http import HttpResponse
from django.template.loader import render_to_string
import pdfkit  # You'll need to install this: pip install pdfkit
from datetime import date, datetime
from django.utils import timezone

# Home Page
@login_required
def home(request):
    return render(request, 'home.html')

# View All Products
@login_required
def products(request):
    products = Product.objects.filter(user=request.user)
    return render(request, 'products.html', {'products': products})

# Add Product View
@login_required
def add_products(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            hsn = request.POST.get('hsn', '')  # Provide default empty string
            gst = request.POST.get('gst')
            price = request.POST.get('price')
            
            # Validate that all required fields are provided
            if not all([name, hsn, gst, price]):  # Check if any field is empty
                messages.error(request, 'All fields are required')
                return render(request, 'add_products.html')
            
            # Create the product
            Product.objects.create(
                user=request.user,
                name=name,
                hsn=hsn,
                gst=gst,
                price=price
            )
            messages.success(request, 'Product added successfully!')
            return redirect('products')
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
            return render(request, 'add_products.html')
            
    return render(request, 'add_products.html')

# Remove Product View
@login_required
def remove_products(request):
    products = Product.objects.filter(user=request.user)
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        Product.objects.filter(id=product_id, user=request.user).delete()
        return redirect('products')
    return render(request, 'remove_products.html', {'products': products})

# Signup View
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        business_name = request.POST.get('business_name')
        gstin = request.POST.get('gstin')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')

        try:
            # Create user
            user = User.objects.create_user(username=username, password=password)
            
            # Update UserProfile
            user.userprofile.business_name = business_name
            user.userprofile.gstin = gstin
            user.userprofile.phone_number = phone_number
            user.userprofile.address = address
            user.userprofile.save()

            # Log the user in
            login(request, user)
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    return render(request, 'signup.html')

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

# Placeholder views for missing functions
def index(request):
    return render(request, 'index.html')

@login_required
def calculation(request):
    products = Product.objects.filter(user=request.user)
    return render(request, 'calculation.html', {'products': products})

def generate_bill(request):
    return render(request, 'generate_bill.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')  # or return redirect('index') if you want to redirect to index page

def generate_bill_number():
    prefix = ''.join(random.choices(string.ascii_uppercase, k=3))
    number = ''.join(random.choices(string.digits, k=5))
    return f"{prefix}{number}"

@login_required
def bill_preview(request):
    if request.method == 'POST':
        try:
            # Get user profile
            user_profile = request.user.userprofile

            # Get form data
            customer_name = request.POST.get('customer_name')
            customer_address = request.POST.get('customer_address')
            customer_gst = request.POST.get('customer_gst')
            bill_date = request.POST.get('bill_date')
            
            # Generate bill number
            bill_no = f"BILL-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Create Bill instance
            bill = Bill.objects.create(
                user=request.user,
                bill_no=bill_no,
                date=bill_date,
                customer_name=customer_name,
                customer_address=customer_address,
                customer_gst=customer_gst,
                subtotal=Decimal(request.POST.get('total_amount', '0')),
                total_gst=Decimal(request.POST.get('total_gst', '0')),
                grand_total=Decimal(request.POST.get('grand_total', '0'))
            )

            # Get product details
            product_ids = request.POST.getlist('product_id[]')
            quantities = request.POST.getlist('quantity[]')
            
            # Create bill items
            items = []
            for i in range(len(product_ids)):
                product = Product.objects.get(id=product_ids[i])
                quantity = int(quantities[i])
                price = Decimal(str(product.price))
                gst_rate = Decimal(str(product.gst))
                gst_amount = (price * quantity * gst_rate) / Decimal('100')
                total = (price * quantity) + gst_amount

                # Create BillItem
                bill_item = BillItem.objects.create(
                    bill=bill,
                    product=product,
                    quantity=quantity,
                    price=price,
                    gst_rate=gst_rate,
                    gst_amount=gst_amount,
                    total=total
                )
                
                items.append({
                    'product': product,
                    'quantity': quantity,
                    'price': price,
                    'gst_rate': gst_rate,
                    'gst_amount': gst_amount,
                    'total': total
                })

            context = {
                'user_profile': user_profile,
                'bill': bill,
                'items': items,
                'customer_name': customer_name,
                'customer_address': customer_address,
                'customer_gst': customer_gst,
                'bill_date': bill_date,
                'bill_no': bill_no,
                'subtotal': bill.subtotal,
                'total_gst': bill.total_gst,
                'grand_total': bill.grand_total
            }

            return render(request, 'bill_preview.html', context)

        except Exception as e:
            messages.error(request, f'Error generating bill preview: {str(e)}')
            return redirect('calculation')

    return redirect('calculation')

@login_required
def bill_history(request):
    bills = Bill.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'bill_history.html', {'bills': bills})

@login_required
def view_bill(request, bill_id):
    try:
        bill = Bill.objects.get(id=bill_id, user=request.user)
        bill_items = bill.items.all()
        context = {
            'bill': bill,
            'bill_items': bill_items,
            'user_profile': request.user.userprofile
        }
        return render(request, 'view_bill.html', context)
    except Bill.DoesNotExist:
        messages.error(request, 'Bill not found!')
        return redirect('bill_history')

@login_required
def download_bill(request, bill_id):
    try:
        bill = Bill.objects.get(id=bill_id, user=request.user)
        bill_items = bill.items.all()
        
        # Prepare context for PDF
        context = {
            'bill': bill,
            'bill_items': bill_items,
            'user_profile': request.user.userprofile
        }
        
        # Generate HTML
        html = render_to_string('bill_pdf.html', context)
        
        # Convert HTML to PDF
        pdf = pdfkit.from_string(html, False)
        
        # Generate response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Bill_{bill.bill_no}.pdf"'
        
        return response
    except Bill.DoesNotExist:
        messages.error(request, 'Bill not found!')
        return redirect('bill_history')
