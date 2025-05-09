import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from main.serializers import DefectSerializer
from main.models import DefectiveProducts as Defects, Batch
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q


@method_decorator(csrf_exempt, name="dispatch")
class CreateDefect(View):
    def post(self, request: HttpRequest):
        d=json.loads(request.body)
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


def filter_defects(request: HttpRequest):
    d = request.GET
    filters = Q()
    order_by = []
    if d["id"]:
        filters &= Q(id=d["id"])
    if d["quantity"]:
        filters &= Q(quantity=d["quantity"])
    if d["description"]:
        filters &= Q(description=d["description"])
    
    defects = Defects.objects.filter(filters)

    return JsonResponse({"defects": DefectSerializer(defects, many=True).data})