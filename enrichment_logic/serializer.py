from rest_framework import serializers
from .models import Category, Merchant, Keyword

# Serializer para la categoria.
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'type', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

# Serializer para el comercio.
class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ('id', 'merchant_name', 'merchant_logo', 'category', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

# Serializer para el keyword.
class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ('id', 'keyword', 'merchant', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

# Serializer para la entrada de la api de enriquecimiento.
class InputTransactionSerializer(serializers.Serializer):
    description = serializers.CharField(required=True)
    amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    date = serializers.DateField(required=True)

# Serializer para la transaccion enriquecida (salida).
class OutputTransactionSerializer(serializers.Serializer):
    description = serializers.CharField(read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    date = serializers.DateField(read_only=True)
    enriched_category = CategorySerializer(read_only=True, allow_null=True)
    enriched_merchant = MerchantSerializer(read_only=True, allow_null=True)

# Serializer para conformar la respuesta de la api de enriquecimiento.
class EnrichmentResponseSerializer(serializers.Serializer):
    transactions = OutputTransactionSerializer(many=True, read_only=True)
    metrics = serializers.DictField(read_only=True)
