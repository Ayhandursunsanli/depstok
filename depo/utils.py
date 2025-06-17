from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from .models import EntryTransaction, ExitTransaction

def calculate_product_stock(product):
    """Ürünün güncel stok miktarını hesaplar"""
    total_entry = EntryTransaction.objects.filter(product=product).aggregate(total=Coalesce(Sum('quantity'), Value(0)))['total']
    total_exit = ExitTransaction.objects.filter(product=product).aggregate(total=Coalesce(Sum('quantity'), Value(0)))['total']
    return max(0, total_entry - total_exit)

def get_product_stock_details(product):
    """Ürünün stok detaylarını hesaplar"""
    total_entry = EntryTransaction.objects.filter(product=product).aggregate(
        total=Coalesce(Sum('quantity'), Value(0))
    )['total'] or 0
    
    total_exit = ExitTransaction.objects.filter(product=product).aggregate(
        total=Coalesce(Sum('quantity'), Value(0))
    )['total'] or 0
    
    current_stock = max(0, total_entry - total_exit)
    
    return {
        'total_entry': total_entry,
        'total_exit': total_exit,
        'current_stock': current_stock
    } 