import json

from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from main.models import Batch, Materials
from main.models import OveruseOfMaterials as Overs
from main.serializers import OverSerializer
from main.views.base import BaseView


class OverusesPage(BaseView, TemplateView):
    template_name = "main/overuses.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["overs"] = OverSerializer(Overs.objects.order_by("-id"), many=True).data
        context["batches"] = Batch.objects.all()
        context["materials"] = Materials.objects.all()
        return context


@method_decorator(csrf_exempt, name="dispatch")
class CreateOver(View):
    def post(self, request: HttpRequest):
        d = json.loads(request.body)

        try:
            batch = Batch.objects.get(id=d["batch"])
        except Batch.DoesNotExist:
            return JsonResponse({"message": "Партия не найдена"}, status=404)

        try:
            material = Materials.objects.get(id=d["material"])
        except Materials.DoesNotExist:
            return JsonResponse({"message": "Материал не найден"}, status=404)

        over = Overs.objects.create(
            batch=batch,
            material=material,
            quantity=d["quantity"],
        )
        return JsonResponse(OverSerializer(over).data, status=201)


@csrf_exempt
def delete_over(request: HttpRequest, id: str):
    if request.method == "DELETE":
        id = int(id)
        try:
            Overs.objects.get(id=id).delete()
        except Overs.DoesNotExist:
            return HttpResponse(status=404)
        return HttpResponse(status=203)

    return HttpRequest(status=403)


def get_over(request: HttpRequest, id: str):
    id = int(id)
    over = get_object_or_404(Overs, id=id)
    return JsonResponse({"over": OverSerializer(over).data})


@csrf_exempt
def edit_over(request: HttpRequest, id: str):
    id = int(id)
    p = get_object_or_404(Overs, id=id)
    d = json.loads(request.body)
    if "batch" in d:
        p.batch_id = d["batch"]
    if "material" in d:
        p.material_id = d["material"]
    if "quantity" in d:
        p.quantity = d["quantity"]

    p.save()

    return HttpResponse(status=202)


def filter_overs(request: HttpRequest):
    d = request.GET
    filters = Q()
    order_by = []
    if d["batch"]:
        filters &= Q(batch_id=d["batch"])
    if d["material"]:
        filters &= Q(material_id=d["material"])

    overs = Overs.objects.filter(filters).order_by(*order_by, "-id")

    return JsonResponse({"overs": OverSerializer(overs, many=True).data})
