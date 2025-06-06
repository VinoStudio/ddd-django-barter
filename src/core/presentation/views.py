from .forms import CustomUserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from src.core.infrastructure.database.models import User
from src.apps.ads.application.services.ad_service import AdService
from src.apps.exchanges.application.services.exchange_service import ExchangeService


class UserCreationFormWithBootstrap(CustomUserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class RegisterView(View):
    def get(self, request):
        form = UserCreationFormWithBootstrap()
        return render(request, "auth/register.html", {"form": form})

    def post(self, request):
        form = UserCreationFormWithBootstrap(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request, f"Account created for {username}! You can now log in."
            )
            return redirect("login")
        return render(request, "auth/register.html", {"form": form})


class ProfileView(LoginRequiredMixin, View):
    def get(self, request, username):
        user = User.objects.filter(username=username).first()

        ad_service = AdService()

        user_ads = ad_service.get_user_ads(user.id)

        exchange_service = ExchangeService()
        exchanges = exchange_service.get_all_user_proposals_data(user.id)

        pending_exchanges = [ex for ex in exchanges if ex.status == "pending"]
        completed_exchanges = [ex for ex in exchanges if ex.status != "pending"]

        context = {
            "user_profile": user,
            "is_owner": user.id == request.user.id,
            "user_ads": user_ads[:6],
            "total_ads": len(user_ads),
            "pending_exchanges": pending_exchanges,
            "completed_exchanges": completed_exchanges,
        }
        return render(request, "auth/profile.html", context)
