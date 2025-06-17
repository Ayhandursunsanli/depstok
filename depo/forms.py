from django import forms
from .models import Product, EntryTransaction, ExitTransaction, QuantityType, Shelf, Department
from .utils import calculate_product_stock

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'quantity_type', 'minimum_quantity']
        labels = {
            'name': 'Ürün Adı',
            'quantity_type': 'Miktar Türü',
            'minimum_quantity': 'Minimum Miktar',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'quantity_type': forms.Select(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'minimum_quantity': forms.NumberInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        }

class EntryTransactionForm(forms.ModelForm):
    product_name = forms.CharField(max_length=200, label="Ürün Adı", required=False, 
                                   widget=forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline', 'placeholder': 'Ürün Adını Girin veya Seçin'}))
    product_select = forms.ModelChoiceField(queryset=Product.objects.all(), label="Mevcut Ürün Seç", required=False, 
                                            widget=forms.Select(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}))
    shelf = forms.ModelChoiceField(queryset=Shelf.objects.all(), label="Raf Numarası", required=True,
                                   widget=forms.Select(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}))
    
    class Meta:
        model = EntryTransaction
        fields = ['quantity']
        labels = {
            'quantity': 'Giriş Miktarı',
        }
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        product_name = cleaned_data.get('product_name')
        product_select = cleaned_data.get('product_select')

        if not product_name and not product_select:
            raise forms.ValidationError("Lütfen bir ürün adı girin veya mevcut bir ürün seçin.")
        
        if product_name and product_select:
            raise forms.ValidationError("Hem ürün adı hem de mevcut ürün seçimi yapılamaz. Lütfen sadece birini kullanın.")

        return cleaned_data

class ExitTransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ürün seçim listesini kalan stok miktarlarıyla birlikte göster
        self.fields['product'].queryset = Product.objects.all()
        self.fields['product'].label_from_instance = lambda obj: f"{obj.name} (Kalan: {calculate_product_stock(obj)} {obj.quantity_type})"

    class Meta:
        model = ExitTransaction
        fields = ['product', 'quantity', 'department']
        labels = {
            'product': 'Ürün',
            'quantity': 'Çıkış Miktarı',
            'department': 'Çıkış Departmanı',
        }
        widgets = {
            'product': forms.Select(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'quantity': forms.NumberInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'department': forms.Select(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        product = self.cleaned_data['product']
        current_stock = calculate_product_stock(product)
        if quantity <= 0:
            raise forms.ValidationError("Çıkış miktarı pozitif bir değer olmalıdır.")
        if quantity > current_stock:
            raise forms.ValidationError(f"Stokta yeterli ürün yok. Mevcut stok: {current_stock} {product.quantity_type}")
        return quantity

class QuantityTypeForm(forms.ModelForm):
    class Meta:
        model = QuantityType
        fields = ['name']
        labels = {
            'name': 'Miktar Türü Adı',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        }

class ShelfForm(forms.ModelForm):
    class Meta:
        model = Shelf
        fields = ['name']
        labels = {
            'name': 'Raf Numarası',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
        labels = {
            'name': 'Departman Adı',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        } 