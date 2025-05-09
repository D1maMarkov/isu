import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from entities.user import UserRole
from main.views.base import BaseView
from main.serializers import MaterialsSerializer
from main.models import Materials
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q


@method_decorator(csrf_exempt, name="dispatch")
class CreateMaterial(BaseView):
    enable_roles = [UserRole.WarehouseManager]

    def post(self, request: HttpRequest):
        d=json.loads(request.body)
        material = Materials.objects.create(**d)
        return JsonResponse({"materials": MaterialsSerializer(material).data}, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class DeleteMaterial(BaseView):
    enable_roles = [UserRole.WarehouseManager]

    def delete(self, request: HttpRequest):
        id = request.GET.get("id")
        try:
            Materials.objects.get(id=int(id)).delete()
        except Materials.DoesNotExist:
            return HttpResponse(status=404)
        return HttpResponse(status=203)
    

class GetMaterial(BaseView):
    enable_roles = [UserRole.WarehouseManager]

    def get(self, request: HttpRequest, id: str):
        id = int(id)
        material = get_object_or_404(Materials, id=id)
        return JsonResponse({"material": MaterialsSerializer(material).data})


@method_decorator(csrf_exempt, name="dispatch")
class EditMaterial(BaseView):
    enable_roles = [UserRole.WarehouseManager]

    def post(self, request: HttpRequest, id: str):
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


class FilterMaterials(BaseView):
    enable_roles = [UserRole.WarehouseManager, UserRole.PatternDesigner]

    def get(self, request: HttpRequest):
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
        
        materials = Materials.objects.filter(filters).order_by(*order_by, "-id")

        return JsonResponse({"materials": MaterialsSerializer(materials, many=True).data})