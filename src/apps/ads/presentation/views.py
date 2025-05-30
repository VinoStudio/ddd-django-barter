from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from src.apps.ads.application.dto.ad import AdFilterDTO, CreateAdDTO, UpdateAdDTO
from src.apps.ads.application.services.ad_service import AdService
from src.apps.ads.domain import ItemCondition, ItemStatus
from src.apps.ads.domain import ItemCategory
from src.core.application.exceptions import PermissionDeniedError
from src.core.infrastructure.exceptions import NotFoundError

ad_service = AdService()

class AdListView(View):
    def get(self, request):
        page = int(request.GET.get('page', 1))
        search = request.GET.get('search', '')
        category = request.GET.get('category', "")
        condition = request.GET.get('condition', "")
        status = request.GET.get('status', "active")

        filter_dto = AdFilterDTO(
            page=page,
            page_size=12,
            keyword=search if search else None,
            category=category,
            condition=condition,
            status=status
        )

        ads = ad_service.list_ads(filter_dto)

        categories = ItemCategory.get_categories()
        conditions = ItemCondition.get_conditions()
        statuses = ItemStatus.get_statuses()

        return render(
            request,
            'ads/ad_list.html',
            {
            'ads': ads,
            'categories': categories,
            'conditions': conditions,
            'statuses': statuses,
            'search': search,
            'selected_category': category,
            'selected_condition': condition,
            'page': page
        })


class AdDetailView(View):
    def get(self, request, ad_id):
        ad = ad_service.get_ad(ad_id)

        if not ad:
            raise NotFoundError(f"Ad with {ad_id} not found")

        context = {
            'ad': ad.to_dict(),
            'is_owner': ad.is_owner(request.user.id) if request.user.is_authenticated else False,
        }

        return render(request, 'ads/ad_detail.html', context)


class AdCreateView(LoginRequiredMixin, View):
    def get(self, request):

        categories = ItemCategory.get_categories()
        conditions = ItemCondition.get_conditions()

        context = {
            'categories': categories,
            'conditions': conditions,
        }

        return render(request, 'ads/ad_form.html', context)

    def post(self, request):
        dto = CreateAdDTO.from_request(request)
        ad = ad_service.create_ad(dto)

        messages.success(request, "Ad created successfully!")
        return redirect('ad_detail', ad_id=ad.id)


class AdUpdateView(LoginRequiredMixin, View):
    def get(self, request, ad_id):
        ad = ad_service.get_ad(ad_id)

        if not ad:
            raise NotFoundError(str(ad_id))

        if not ad.is_owner(request.user.id):
            raise PermissionDeniedError("Only the author of the ad can update it")

        context = {
            'ad': ad.to_dict(),
            "categories": ItemCategory.get_categories(),
            "conditions": ItemCondition.get_conditions(),
        }

        return render(request, 'ads/ad_form.html', context)

    def post(self, request, ad_id):
        dto = UpdateAdDTO.from_request(request, ad_id)

        updated_ad = ad_service.update_ad(dto)

        messages.success(request, "Ad updated successfully!")
        return redirect('ad_detail', ad_id=updated_ad.id)


class AdDeleteView(LoginRequiredMixin, View):
    def post(self, request, ad_id):
        ad_service.delete_ad(ad_id, request.user.id)

        messages.success(request, "Ad deleted successfully!")
        return redirect('ad_list')