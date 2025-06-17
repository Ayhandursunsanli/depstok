from django.db import models
from django.urls import reverse

# Create your models here.

class QuantityType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Miktar Türü")

    class Meta:
        verbose_name = "Miktar Türü"
        verbose_name_plural = "Miktar Türleri"

    def __str__(self):
        return self.name

class Shelf(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Raf Numarası")

    class Meta:
        verbose_name = "Raf"
        verbose_name_plural = "Raflar"

    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Departman Adı")

    class Meta:
        verbose_name = "Departman"
        verbose_name_plural = "Departmanlar"

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Ürün Adı")
    quantity_type = models.ForeignKey(QuantityType, on_delete=models.SET_NULL, null=True, verbose_name="Miktar Türü")
    minimum_quantity = models.IntegerField(default=0, verbose_name="Minimum Miktar")
    shelf = models.ForeignKey(Shelf, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Raf Numarası")

    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"pk": self.pk})

class EntryTransaction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Ürün")
    entry_date = models.DateTimeField(auto_now_add=True, verbose_name="Giriş Tarihi")
    quantity = models.IntegerField(verbose_name="Giriş Miktarı")

    class Meta:
        verbose_name = "Ürün Giriş Hareketi"
        verbose_name_plural = "Ürün Giriş Hareketleri"

    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.product.quantity_type} ({self.entry_date.strftime('%Y-%m-%d %H:%M')})"

class ExitTransaction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Ürün")
    exit_date = models.DateTimeField(auto_now_add=True, verbose_name="Çıkış Tarihi")
    quantity = models.IntegerField(verbose_name="Çıkış Miktarı")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Çıkış Departmanı")

    class Meta:
        verbose_name = "Ürün Çıkış Hareketi"
        verbose_name_plural = "Ürün Çıkış Hareketleri"

    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.product.quantity_type} ({self.exit_date.strftime('%Y-%m-%d %H:%M')})"
