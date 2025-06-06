from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from src.apps.exchanges.application.services.exchange_service import ExchangeService
from src.apps.exchanges.application.dto.exchange import (
    CreateExchangeDTO,
    UpdateExchangeStatusDTO,
)
from src.apps.exchanges.domain.values.status import ExchangeStatus
from src.apps.ads.application.services.ad_service import AdService

exchange_service = ExchangeService()
ad_service = AdService()


class ExchangeListView(LoginRequiredMixin, View):
    def get(self, request):
        filter_type = request.GET.get("filter_type", "all")
        status_filter = request.GET.get("status", "")

        user_ads = ad_service.get_user_ads(request.user.id)
        user_ad_ids = [ad.id for ad in user_ads]

        exchanges = exchange_service.get_all_user_proposals_data(request.user.id)

        if status_filter:
            exchanges = [e for e in exchanges if e.status == status_filter]

        if filter_type == "sent":
            exchanges = [e for e in exchanges if e.ad_sender_id in user_ad_ids]
        elif filter_type == "received":
            exchanges = [e for e in exchanges if e.ad_receiver_id in user_ad_ids]

        statuses = ExchangeStatus.get_exchange_statuses()

        context = {
            "exchanges": exchanges,
            "user_ads_ids": user_ad_ids,
            "filter_type": filter_type,
            "status": status_filter,
            "statuses": statuses,
        }

        return render(request, "exchanges/exchange_list.html", context)


class ExchangeDetailView(LoginRequiredMixin, View):
    def get(self, request, exchange_id):
        exchange = exchange_service.get_exchange(exchange_id)

        sender_ad, receiver_ad = exchange_service.get_exchange_participants(
            exchange, request.user.id
        )

        context = {
            "exchange": exchange,
            "sender_ad": sender_ad,
            "receiver_ad": receiver_ad,
            "is_receiver": receiver_ad.user_id == request.user.id,
            "statuses": ExchangeStatus.get_exchange_statuses(),
        }

        return render(request, "exchanges/exchange_detail.html", context)


class ExchangeCreateView(LoginRequiredMixin, View):
    def get(self, request, ad_receiver_id):
        receiver_ad = ad_service.get_ad(ad_receiver_id)

        user_ads = ad_service.get_user_ads(request.user.id)

        context = {
            "receiver_ad": receiver_ad,
            "user_ads": user_ads,
            "post_autor": request.user.id,
        }

        return render(request, "exchanges/exchange_form.html", context)

    def post(self, request, ad_receiver_id):

        dto = CreateExchangeDTO.from_request(request, ad_receiver_id)

        exchange = exchange_service.create_proposal(dto)

        messages.success(request, "Exchange proposal sent successfully!")
        return redirect("exchange_detail", exchange_id=exchange.id)


class ExchangeUpdateView(LoginRequiredMixin, View):
    def post(self, request, exchange_id):
        dto = UpdateExchangeStatusDTO.from_request(request, exchange_id)
        exchange = exchange_service.update_proposal_status(dto)

        messages.success(request, f"Exchange status updated to {dto.status.value}!")
        return redirect("exchange_detail", exchange_id=exchange.id)


class ExchangeDeleteView(LoginRequiredMixin, View):
    def post(self, request, exchange_id):

        exchange_service.delete_exchange(exchange_id, request.user.id)

        messages.success(request, "Exchange proposal has been cancelled.")
        return redirect("exchange_list")
