from django.urls import path,include
from rest_framework import routers
from enrichment_logic import views

router = routers.DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'merchant', views.MerchantViewSet)
router.register(r'keyword', views.KeywordViewSet)

urlpatterns = [
        path('', include(router.urls)),
        path('transactions/enrich/', views.EnrichTransactionsAPIView.as_view(), name='enrich-transactions'),
]