from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from src.apps.ads.presentation import views as ad_views
from src.core.presentation.views import RegisterView, ProfileView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ad_views.AdListView.as_view(), name='index'),
    path('ads/', include('src.apps.ads.presentation.urls')),
    path('exchanges/', include('src.apps.exchanges.presentation.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)