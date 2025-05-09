import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
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


@csrf_exempt
def delete_document(request: HttpRequest, id: int):
    if request.method == "DELETE":
        try:
            Document.objects.get(id=int(id)).delete()
        except Document.DoesNotExist:
            return HttpResponse(status=404)
        return HttpResponse(status=203)
    
    return HttpRequest(status=403)


def get_document(request: HttpRequest, id: str):
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


def filter_materials(request: HttpRequest):
    d = request.GET
    filters = Q()
    order_by = []
    if d["id"]:
        filters &= Q(id=d["id"])
    if d["name"]:
        filters &= Q(name=["name"])
    if d["quantity_order"]:
        if d["quantity_order"] == "asc":
            order_by.append("quantity_material")
        else:
            order_by.append("-quantity_material")
    if d["price_order"]:
        if d["price_order"] == "asc":
            order_by.append("price")
        else:
            order_by.append("-price")
    if d["features"]:
        filters &= Q(features=d["features"])
    if d["supplier"]:
        filters &= Q(supplier=d["supplier"])
    
    materials = Materials.objects.filter(filters).order_by(*order_by)

    return JsonResponse({"materials": MaterialsSerializer(materials, many=True).data})