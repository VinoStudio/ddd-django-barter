from django.urls import path
from .views import AdListView, AdDetailView, AdCreateView, AdUpdateView, AdDeleteView

urlpatterns = [
    path('', AdListView.as_view(), name='ad_list'),
    path('<uuid:ad_id>/', AdDetailView.as_view(), name='ad_detail'),
    path('create/', AdCreateView.as_view(), name='ad_create'),
    path('<uuid:ad_id>/update/', AdUpdateView.as_view(), name='ad_update'),
    path('<uuid:ad_id>/delete/', AdDeleteView.as_view(), name='ad_delete'),
]