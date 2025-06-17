from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product_entry/', views.product_entry, name='product_entry'),
    path('product_exit/', views.product_exit, name='product_exit'),
    path('create_product/', views.create_product, name='create_product'),
    path('shelf_visualization/', views.shelf_visualization, name='shelf_visualization'),
    path('get_product_stock/', views.get_product_stock, name='get_product_stock'),
    path('parameters/', views.parameters_view, name='parameters'),
    path('export/products/', views.export_products_to_excel, name='export_products_to_excel'),
    path('export/transactions/', views.export_transactions_to_excel, name='export_transactions_to_excel'),
    path('export/parameters/', views.export_parameters_to_excel, name='export_parameters_to_excel'),
] 