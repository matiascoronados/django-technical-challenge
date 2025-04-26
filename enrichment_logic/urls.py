from django.urls import path,include
from rest_framework import routers
from enrichment_logic import views

router = routers.DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'merchant', views.MerchantViewSet)
router.register(r'keyword', views.KeywordViewSet)
router.register(r'transaction', views.TransactionViewSet)

urlpatterns = [
        path('', include(router.urls))
]