from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Value, F, CharField
from django.db.models.functions import Coalesce
from .models import Product, EntryTransaction, ExitTransaction, QuantityType, Shelf, Department
from .forms import ProductForm, EntryTransactionForm, ExitTransactionForm, QuantityTypeForm, ShelfForm, DepartmentForm
from .utils import calculate_product_stock, get_product_stock_details
import pandas as pd
from django.http import HttpResponse
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

class DashboardView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'depo/dashboard.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.annotate(
            total_entry=Coalesce(Sum('entrytransaction__quantity'), Value(0)),
            total_exit=Coalesce(Sum('exittransaction__quantity'), Value(0)),
            calculated_stock=F('total_entry') - F('total_exit')
        ).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = Product.objects.count()
        context['total_stock'] = sum(product.calculated_stock for product in self.get_queryset())
        context['entry_form'] = EntryTransactionForm()
        context['exit_form'] = ExitTransactionForm()
        context['product_form'] = ProductForm()
        context['quantity_types'] = QuantityType.objects.all()
        context['shelves'] = Shelf.objects.all()
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'depo/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Giriş işlemleri
        entry_transactions = EntryTransaction.objects.filter(product=product).annotate(
            transaction_type=Value('Giriş', output_field=CharField())
        ).values('entry_date', 'quantity', 'transaction_type')
        
        # Çıkış işlemleri
        exit_transactions = ExitTransaction.objects.filter(product=product).annotate(
            transaction_type=Value('Çıkış', output_field=CharField())
        ).values('exit_date', 'quantity', 'transaction_type')
        
        # Tüm işlemleri birleştir ve tarihe göre sırala
        all_transactions = []
        
        # Giriş işlemlerini ekle
        for entry in entry_transactions:
            all_transactions.append({
                'date': entry['entry_date'],
                'quantity': entry['quantity'],
                'transaction_type': entry['transaction_type']
            })
        
        # Çıkış işlemlerini ekle
        for exit in exit_transactions:
            all_transactions.append({
                'date': exit['exit_date'],
                'quantity': exit['quantity'],
                'transaction_type': exit['transaction_type']
            })
        
        # Tarihe göre sırala
        all_transactions.sort(key=lambda x: x['date'], reverse=True)
        
        context['transactions'] = all_transactions
        context['current_stock'] = calculate_product_stock(product)
        return context

def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ürün başarıyla oluşturuldu.')
            return redirect('dashboard')
    else:
        form = ProductForm()
    return render(request, 'depo/product_form.html', {'form': form})

@login_required
def product_entry(request):
    if request.method == 'POST':
        form = EntryTransactionForm(request.POST)
        if form.is_valid():
            product_name = form.cleaned_data.get('product_name')
            product_select = form.cleaned_data.get('product_select')
            
            if product_name:
                product = Product.objects.create(
                    name=product_name,
                    quantity_type=QuantityType.objects.first(),
                    minimum_quantity=0
                )
            else:
                product = product_select
            
            entry = EntryTransaction.objects.create(
                product=product,
                quantity=form.cleaned_data['quantity']
            )
            
            product.shelf = form.cleaned_data['shelf']
            product.save()
            
            messages.success(request, 'Ürün girişi başarıyla kaydedildi.')
            return redirect('dashboard')
    else:
        form = EntryTransactionForm()
    return render(request, 'depo/product_entry.html', {'form': form})

def product_exit(request):
    if request.method == 'POST':
        form = ExitTransactionForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            
            current_stock = calculate_product_stock(product)
            if quantity > current_stock:
                messages.error(request, 'Yetersiz stok!')
                return redirect('dashboard')
            
            exit = form.save()
            product.calculated_stock = calculate_product_stock(product)
            if product.calculated_stock == 0:
                product.shelf = None
            product.save()
            messages.success(request, 'Ürün çıkışı başarıyla kaydedildi.')
            return redirect('dashboard')
    else:
        form = ExitTransactionForm()
    return render(request, 'depo/exit_form.html', {'form': form})

def parameters_view(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'quantity_type':
            form = QuantityTypeForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Miktar türü başarıyla oluşturuldu.')
        elif form_type == 'shelf':
            form = ShelfForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Raf başarıyla oluşturuldu.')
        elif form_type == 'department':
            form = DepartmentForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Departman başarıyla oluşturuldu.')
        
        return redirect('parameters')
    
    quantity_types = QuantityType.objects.all()
    shelves = Shelf.objects.all()
    departments = Department.objects.all()
    
    context = {
        'quantity_types': quantity_types,
        'shelves': shelves,
        'departments': departments,
        'quantity_type_form': QuantityTypeForm(),
        'shelf_form': ShelfForm(),
        'department_form': DepartmentForm(),
    }
    return render(request, 'depo/parameters.html', context)

def create_quantity_type(request):
    if request.method == 'POST':
        form = QuantityTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Miktar türü başarıyla oluşturuldu.')
    return redirect('parameters')

def create_shelf(request):
    if request.method == 'POST':
        form = ShelfForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Raf başarıyla oluşturuldu.')
    return redirect('parameters')

def create_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Departman başarıyla oluşturuldu.')
    return redirect('parameters')

def export_products_to_excel(request):
    products = Product.objects.all()
    data = []
    
    for product in products:
        data.append({
            'Ürün Adı': product.name,
            'Miktar Türü': product.quantity_type.name if product.quantity_type else '',
            'Raf Numarası': product.shelf.name if product.shelf else '',
            'Minimum Miktar': product.minimum_quantity,
            'Mevcut Stok': product.calculated_stock
        })
    
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename=products_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    df.to_excel(response, index=False)
    return response

def export_transactions_to_excel(request):
    entries = EntryTransaction.objects.all()
    exits = ExitTransaction.objects.all()
    data = []
    
    for entry in entries:
        data.append({
            'Ürün': entry.product.name,
            'İşlem Türü': 'Giriş',
            'Miktar': entry.quantity,
            'Departman': 'Depo',
            'Tarih': entry.entry_date.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    for exit in exits:
        data.append({
            'Ürün': exit.product.name,
            'İşlem Türü': 'Çıkış',
            'Miktar': exit.quantity,
            'Departman': exit.department.name if exit.department else '',
            'Tarih': exit.exit_date.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename=transactions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    df.to_excel(response, index=False)
    return response

def export_parameters_to_excel(request):
    quantity_types = QuantityType.objects.all()
    shelves = Shelf.objects.all()
    departments = Department.objects.all()
    
    data = {
        'Miktar Türleri': pd.DataFrame([{'Miktar Türü': qt.name} for qt in quantity_types]),
        'Raflar': pd.DataFrame([{'Raf Numarası': shelf.name} for shelf in shelves]),
        'Departmanlar': pd.DataFrame([{'Departman Adı': dept.name} for dept in departments])
    }
    
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename=parameters_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        for sheet_name, df in data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    return response

def get_product_stock(request):
    product_id = request.GET.get('product_id')
    if product_id:
        product = get_object_or_404(Product, id=product_id)
        current_stock = calculate_product_stock(product)
        return JsonResponse({
            'current_stock': current_stock,
            'quantity_type': product.quantity_type.name if product.quantity_type else ''
        })
    return JsonResponse({'error': 'Product ID is required'}, status=400)

def shelf_visualization(request):
    shelves = Shelf.objects.all().order_by('name')
    shelf_data = []
    
    for shelf in shelves:
        products = Product.objects.filter(shelf=shelf)
        product_data = []
        
        for product in products:
            total_entry = EntryTransaction.objects.filter(product=product).aggregate(total=Coalesce(Sum('quantity'), Value(0)))['total']
            total_exit = ExitTransaction.objects.filter(product=product).aggregate(total=Coalesce(Sum('quantity'), Value(0)))['total']
            current_stock = max(0, total_entry - total_exit)
            
            if current_stock > 0:
                product_data.append({
                    'id': product.id,
                    'name': product.name,
                    'quantity': current_stock,
                    'quantity_type': product.quantity_type.name if product.quantity_type else ''
                })
        
        shelf_data.append({
            'name': shelf.name,
            'products': product_data
        })
    
    return render(request, 'depo/shelf_visualization.html', {'shelf_data': shelf_data})
