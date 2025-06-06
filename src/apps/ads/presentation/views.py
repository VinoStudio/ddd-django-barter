from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from src.apps.ads.application.dto.ad import AdFilterDTO, CreateAdDTO, UpdateAdDTO, AdDTO
from src.apps.ads.application.services.ad_service import AdService
from src.apps.ads.domain import ItemCondition, ItemStatus
from src.apps.ads.domain import ItemCategory
from src.core.application.exceptions import PermissionDeniedError
from src.core.infrastructure.database.models import User

ad_service = AdService()


class AdListView(View):
    def get(self, request, username=None):
        page = int(request.GET.get("page", 1))
        search = request.GET.get("search", "")
        category = request.GET.get("category", "")
        condition = request.GET.get("condition", "")
        status = request.GET.get("status", "active")

        user_profile = None
        is_owner = False

        if username:
            user_profile = User.objects.filter(username=username).first()
            if user_profile is not None:
                is_owner = (
                    request.user.id == user_profile.id
                    if request.user.is_authenticated
                    else False
                )

        filter_dto = AdFilterDTO(
            page=page,
            page_size=12,
            keyword=search if search else None,
            category=category,
            condition=condition,
            status=status if not is_owner else "",
            user_id=user_profile.id if user_profile else None,
        )

        result = ad_service.list_ads(filter_dto)

        ads = result["ads"]
        page_size = result["page_size"]
        total_items = result["total_items"]
        total_pages = result["total_pages"]

        has_previous = page > 1
        has_next = page < total_pages

        pagination_range = range(max(1, page - 2), min(total_pages + 1, page + 3))

        categories = ItemCategory.get_categories()
        conditions = ItemCondition.get_conditions()
        statuses = ItemStatus.get_statuses()

        return render(
            request,
            "ads/ad_list.html",
            {
                "ads": ads,
                "categories": categories,
                "conditions": conditions,
                "statuses": statuses,
                "search": search,
                "selected_category": category,
                "selected_condition": condition,
                "selected_status": status,
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_previous": has_previous,
                "has_next": has_next,
                "pagination_range": pagination_range,
                "user_profile": user_profile,
                "is_owner": is_owner,
                "is_user_filter": username is not None,
            },
        )


class AdDetailView(View):
    def get(self, request, ad_id):
        ad: AdDTO = ad_service.get_ad(ad_id)

        context = {"ad": ad, "is_owner": ad.user_id == request.user.id}

        return render(request, "ads/ad_detail.html", context)


class AdCreateView(LoginRequiredMixin, View):
    def get(self, request):

        categories = ItemCategory.get_categories()
        conditions = ItemCondition.get_conditions()

        context = {
            "categories": categories,
            "conditions": conditions,
        }

        return render(request, "ads/ad_form.html", context)

    def post(self, request):
        dto = CreateAdDTO.from_request(request)
        ad = ad_service.create_ad(dto)

        messages.success(request, "Ad created successfully!")
        return redirect("ad_detail", ad_id=ad.id)


class AdUpdateView(LoginRequiredMixin, View):
    def get(self, request, ad_id):
        ad: AdDTO = ad_service.get_ad(ad_id)

        if not ad.user_id == request.user.id:
            raise PermissionDeniedError("Only the author of the ad can update it")

        context = {
            "ad": ad,
            "categories": ItemCategory.get_categories(),
            "conditions": ItemCondition.get_conditions(),
        }

        return render(request, "ads/ad_form.html", context)

    def post(self, request, ad_id):
        dto = UpdateAdDTO.from_request(request, ad_id)

        updated_ad = ad_service.update_ad(dto)

        messages.success(request, "Ad updated successfully!")
        return redirect("ad_detail", ad_id=updated_ad.id)


class AdDeleteView(LoginRequiredMixin, View):
    def post(self, request, ad_id):
        ad_service.delete_ad(ad_id, request.user.id)

        messages.success(request, "Ad deleted successfully!")
        return redirect("ad_list")
