from django.contrib import admin
from .models import Product, EntryTransaction, ExitTransaction, Shelf, Department, QuantityType

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity_type', 'shelf', 'minimum_quantity')
    list_filter = ('quantity_type', 'shelf')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(EntryTransaction)
class EntryTransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'entry_date')
    list_filter = ('entry_date', 'product')
    search_fields = ('product__name',)
    ordering = ('-entry_date',)

@admin.register(ExitTransaction)
class ExitTransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'department', 'exit_date')
    list_filter = ('exit_date', 'product', 'department')
    search_fields = ('product__name', 'department__name')
    ordering = ('-exit_date',)

@admin.register(Shelf)
class ShelfAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(QuantityType)
class QuantityTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

# Admin site başlıklarını Türkçeleştir
admin.site.site_header = 'Depo Stok Takip Sistemi'
admin.site.site_title = 'Depo Stok Takip'
admin.site.index_title = 'Yönetim Paneli'
