import json

from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from entities.user import UserRole
from main.models import Batch
from main.models import DefectiveProducts as Defects
from main.serializers import DefectSerializer
from main.views.base import BaseView


class DefectsPage(BaseView, TemplateView):
    template_name = "main/defects.html"
    exclude_roles = [UserRole.WarehouseManager, UserRole.PatternDesigner]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["defects"] = DefectSerializer(Defects.objects.order_by("-id"), many=True).data
        context["batches"] = Batch.objects.order_by("-id")

        return context


@method_decorator(csrf_exempt, name="dispatch")
class CreateDefect(BaseView):
    def post(self, request: HttpRequest):
        d = json.loads(request.body)
        try:
            batch = Batch.objects.get(id=d["batch"])
            d["batch"] = batch
        except Batch.DoesNotExist:
            return JsonResponse({"message": "Партия с таким ID не найдена"}, status=404)

        defect = Defects.objects.create(**d)
        return JsonResponse({"defect": DefectSerializer(defect).data}, status=201)


@csrf_exempt
def delete_defect(request: HttpRequest, id: int):
    if request.method == "DELETE":
        try:
            Defects.objects.get(id=int(id)).delete()
        except Defects.DoesNotExist:
            return HttpResponse(status=404)
        return HttpResponse(status=203)

    return HttpResponse(status=403)


def get_defect(request: HttpRequest, id: str):
    id = int(id)
    defect = get_object_or_404(Defects, id=id)
    return JsonResponse({"defect": DefectSerializer(defect).data})


@method_decorator(csrf_exempt, name="dispatch")
class EditDefect(BaseView):
    def post(self, request: HttpRequest, id: str):
        id = int(id)
        defect = get_object_or_404(Defects, id=id)
        files = request.FILES
        if files:
            defect.report = request.FILES["file"]

        else:
            d = json.loads(request.body)
            defect.batch_id = d["batch"]
            defect.quantity = d["quantity"]
            defect.description = d["description"]

        defect.save()

        return HttpResponse(status=202)


def filter_defects(request: HttpRequest):
    d = request.GET

    filters = Q()
    order_by = []
    if d["batch"]:
        filters &= Q(batch_id=d["batch"])
    if d["quantity"]:
        order_by.append(d["quantity"])
    if d["description"]:
        filters &= Q(description=d["description"])

    defects = Defects.objects.filter(filters).order_by(*order_by, "-id")

    return JsonResponse({"defects": DefectSerializer(defects, many=True).data})


@method_decorator(csrf_exempt, name="dispatch")
class DeleteDefectReport(BaseView):
    def delete(self, request: HttpRequest, id: int):
        id = int(id)
        document = Defects.objects.get(id=id)
        document.report = None
        document.save()

        return HttpResponse(status=204)