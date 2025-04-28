from rest_framework import serializers
from .models import Category, Merchant, Keyword

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'type', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
        
class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ('id', 'merchant_name', 'merchant_logo', 'category', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
        
class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ('id', 'keyword', 'merchant', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class InputTransactionSerializer(serializers.Serializer):
    description = serializers.CharField(required=True)
    amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    date = serializers.DateField(required=True)
    
class OutputTransactionSerializer(serializers.Serializer):
    description = serializers.CharField(read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    date = serializers.DateField(read_only=True)
    enriched_category = CategorySerializer(read_only=True, allow_null=True)
    enriched_merchant = MerchantSerializer(read_only=True, allow_null=True)

class EnrichmentResponseSerializer(serializers.Serializer):
    transactions = OutputTransactionSerializer(many=True, read_only=True)
    metrics = serializers.DictField(read_only=True)
