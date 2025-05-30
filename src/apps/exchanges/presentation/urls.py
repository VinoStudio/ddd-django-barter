from django.urls import path
from .views import ExchangeListView, ExchangeDetailView, ExchangeCreateView, ExchangeUpdateView, ExchangeDeleteView

urlpatterns = [
    path('', ExchangeListView.as_view(), name='exchange_list'),
    path('<uuid:exchange_id>/', ExchangeDetailView.as_view(), name='exchange_detail'),
    path('create/<uuid:ad_receiver_id>/', ExchangeCreateView.as_view(), name='exchange_create'),
    path('<uuid:exchange_id>/update/', ExchangeUpdateView.as_view(), name='exchange_update'),
    path('exchanges/<uuid:exchange_id>/delete/', ExchangeDeleteView.as_view(), name='exchange_delete'),
]