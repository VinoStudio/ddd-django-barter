
from .forms import CustomUserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from src.apps.ads.application.services.ad_service import AdService
from src.apps.exchanges.application.services.exchange_service import ExchangeService


class UserCreationFormWithBootstrap(CustomUserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class RegisterView(View):
    def get(self, request):
        form = UserCreationFormWithBootstrap()
        return render(request, 'auth/register.html', {'form': form})

    def post(self, request):
        form = UserCreationFormWithBootstrap(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
        return render(request, 'auth/register.html', {'form': form})


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        ad_service = AdService()
        user_ads = ad_service.get_user_ads(request.user.id)

        user_ad_ids = [ad.id for ad in user_ads]

        exchange_service = ExchangeService()
        exchanges = exchange_service.get_user_proposals(request.user.id)

        for exchange in exchanges:
            sender_ad = ad_service.get_ad(exchange.ad_sender_id)
            receiver_ad = ad_service.get_ad(exchange.ad_receiver_id)

            exchange.is_user_sender = exchange.ad_sender_id in user_ad_ids

            exchange.user_item = sender_ad.title if exchange.is_user_sender else receiver_ad.title
            exchange.other_item = receiver_ad.title if exchange.is_user_sender else sender_ad.title

        pending_exchanges = [ex for ex in exchanges if ex.status.value == 'PENDING']
        completed_exchanges = [ex for ex in exchanges if ex.status.value != 'PENDING']

        context = {
            'user': request.user,
            'user_ads': user_ads,
            'pending_exchanges': pending_exchanges,
            'completed_exchanges': completed_exchanges,
        }
        return render(request, 'auth/profile.html', context)
