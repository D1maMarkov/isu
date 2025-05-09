from django.http import HttpResponse
from django.views import View

from main.serializers import FinishedProductsSerializer
from main.models import FinishedProducts as Products
import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name="dispatch")
class CreateFinishedProduct(View):
    def post(self, request: HttpRequest):
        d = json.loads(request.body)

        product = Products.objects.create(
            batch_id=d["batch"],
            product_name=d["name"],
            size=d["size"],
            quantity_product=d["quantity"] 
        )
        return JsonResponse(FinishedProductsSerializer(product).data, status=201)


@csrf_exempt
def delete_product(request: HttpRequest, id: str):
    if request.method == "DELETE":
        id = int(id)
        try:
            Products.objects.get(id=id).delete()
        except Products.DoesNotExist:
            return HttpResponse(status=404)
        return HttpResponse(status=203)
    
    return HttpRequest(status=403)


def get_product(request: HttpRequest, id: str):
    id = int(id)
    product = get_object_or_404(Products, id=id)
    return JsonResponse({"product": FinishedProductsSerializer(product).data})

@csrf_exempt
def edit_product(request: HttpRequest, id: str):
    id = int(id)
    print(id)
    p = get_object_or_404(Products, id=id)
    d=json.loads(request.body)
    if "batch" in d: 
        p.batch_id = d["batch"]
    if "name" in d:
        p.product_name=d["name"]
    if "size" in d:
        p.size=d["size"]
    if "quantity" in d:
        p.quantity_product=d["quantity"]

    p.save()

    return HttpResponse(status=202)


def filter_products(request: HttpRequest):
    d = request.GET
    filters = Q()
    order_by = []
    if d["batch"]:
        filters &= Q(batch_id=d["batch"])
    if d["name"]:
        filters &= Q(name=["name"])
    if d["quantity_order"]:
        if d["quantity_order"] == "asc":
            order_by.append("quantity_product")
        else:
            order_by.append("-quantity_product")
    if d["size"]:
        filters &= Q(size=d["size"])

    products = Products.objects.filter(filters).order_by(*order_by)

    return JsonResponse({"products": FinishedProductsSerializer(products, many=True).data})
