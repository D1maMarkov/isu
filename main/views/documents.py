import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from entities.user import UserRole
from main.views.base import BaseView
from main.serializers import DocumentSerializer, MaterialsSerializer
from main.models import Batch, DocumentManagement as Document
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q


@method_decorator(csrf_exempt, name="dispatch")
class CreateDoc(View):
    def post(self, request: HttpRequest):
        d=json.loads(request.body)
        try:
            batch = Batch.objects.get(id=d["batch"])
            d["batch"] = batch
        except Batch.DoesNotExist:
            return JsonResponse({'message': 'Партия с данным ID не найдена'}, status=404)
        doc = Document.objects.create(**d)
        return JsonResponse({"document": DocumentSerializer(doc).data}, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class DeleteDoc(View):
    def delete(self, request: HttpRequest, id: int):
        try:
            Document.objects.get(id=int(id)).delete()
        except Document.DoesNotExist:
            return HttpResponse(status=404)
        return HttpResponse(status=203)


class GetDocument(BaseView):
    enable_roles = [UserRole.Designer, UserRole.Sewer]

    def get(self, request: HttpRequest, id: str):
        id = int(id)
        material = get_object_or_404(Document, id=id)
        return JsonResponse({"document": DocumentSerializer(material).data})

@csrf_exempt
def edit_material(request: HttpRequest, id: str):
    id = int(id)
    material = get_object_or_404(Materials, id=id)
    d=json.loads(request.body)
    if "name" in d: 
        material.name = d["name"]
    if "quantity" in d:
        material.quantity = d["quantity"]
    if "features" in d:
        material.features=d["features"]
    if "price" in d:
        material.price=d["price"]
    if "supplier" in d:
        material.supplier=d["supplier"]

    material.save()

    return HttpResponse(status=202)


class FilterDocs(BaseView):
    enable_roles = [UserRole.Designer, UserRole.Sewer, UserRole.PatternDesigner, UserRole.PackerInspector, UserRole.Cutter]

    def get(self, request: HttpRequest):
        d = request.GET
        filters = Q()
        if request.user.role in [UserRole.Designer, UserRole.PatternDesigner]:
            filters &= Q(category="Задание")

        if request.user.role in [UserRole.Sewer, UserRole.PackerInspector]:
            filters &= Q(category="тех. Задание")

        if request.user.role in [UserRole.Cutter]:
            filters &= (Q(category="тех. Задание") | Q(category="Заказ"))

        print(d)
        if d["id"]:
            filters &= Q(id=d["id"])
        if d["batch"]:
            filters &= Q(batch_id=d["batch"])
        if d["category"]:
            filters &= Q(category=d["category"])

        docs = Document.objects.filter(filters).order_by("-id")

        return JsonResponse({"documents": DocumentSerializer(docs, many=True).data})