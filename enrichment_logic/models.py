from django.db import models
import uuid

# Modelo de la Categoria
class Category(models.Model):
    # Tipos de movimiento (ingreso o gasto).
    MOVEMENT_TYPES = [
        ('expense', 'Expense'),
        ('income', 'Income'),
    ]
    # Campos principales del modelo.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name="Name")
    type = models.CharField(max_length=10, choices=MOVEMENT_TYPES, verbose_name="Type")
    # Campos de auditoria.
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"{self.name} - {self.type}"

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

# Modelo del Comercio
class Merchant(models.Model):
    # Campos principales del modelo.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant_name = models.CharField(max_length=100, unique=True, verbose_name="Merchant Name")
    merchant_logo = models.URLField(max_length=500, null=True, blank=True, verbose_name="URL Merchant Logo")
    # Llave foranea a la Categoria.
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="merchants",
        verbose_name="Category"
    )
    # Campos de auditoria.
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return self.merchant_name

    class Meta:
        verbose_name = "Merchant"
        verbose_name_plural = "Merchants"

# Modelo del Keyword
class Keyword(models.Model):
    # Campos principales del modelo.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    keyword = models.CharField(max_length=100, unique=True, verbose_name="Keyword")
    # Llave foranea al Comercio.
    merchant = models.ForeignKey(
        Merchant,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="keywords",
        verbose_name="Merchant"
    )
    # Campos de auditoria.
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"{self.keyword} - {self.merchant}"

    class Meta:
        verbose_name = "Keyword"
        verbose_name_plural = "Keywords"


# Modelo de la Transacción
class Transaction(models.Model):
    # Campos principales del modelo.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField(verbose_name="Description")
    amount = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2, verbose_name="Amount")
    date = models.DateField(verbose_name="Date", null=True, blank=True)
    # Llave foranea a la Categoria.
    enriched_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="categorized_transactions",
        verbose_name="Enriched Category"
    )
    # Llave foranea al Comercio.
    enriched_merchant = models.ForeignKey(
        Merchant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="merchant_transactions",
        verbose_name="Enriched Merchant"
    )

    def __str__(self):
        return f"{self.description} - {self.amount} - {self.date}"

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"