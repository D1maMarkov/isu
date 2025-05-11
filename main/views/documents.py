import json

from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from entities.user import UserRole
from main.models import Batch
from main.models import DocumentManagement as Document
from main.models import DocumentResult
from main.serializers import BatchSerializer, DocumentSerializer
from main.views.base import BaseView
from utils.get_file_name import get_file_name


@method_decorator(csrf_exempt, name="dispatch")
class CreateBatch(BaseView):
    enable_roles = [UserRole.GeneralManager, UserRole.ProductionManager]

    def post(self, request: HttpRequest):
        batch = Batch.objects.create()
        return JsonResponse({"batch": BatchSerializer(batch).data}, status=201)


class GetBatches(BaseView):
    enable_roles = [UserRole.GeneralManager, UserRole.ProductionManager]

    def get(self, request: HttpRequest):
        return JsonResponse({"batches": BatchSerializer(Batch.objects.order_by("-id"), many=True).data})


class DocsPage(BaseView, TemplateView):
    template_name = "main/documents.html"
    exclude_roles = [UserRole.WarehouseManager]

    @property
    def can_load_request(self):
        user = self.request.user
        if user.role in [UserRole.Sewer, UserRole.PackerInspector, UserRole.Designer, UserRole.PatternDesigner]:
            return False
        return True

    @property
    def can_edit(self):
        user = self.request.user
        if user.role in [UserRole.Sewer, UserRole.PatternDesigner, UserRole.Designer, UserRole.PackerInspector]:
            return False
        return True

    @property
    def can_load_result(self):
        user = self.request.user
        if user.role in [UserRole.Sewer]:
            return False
        return True


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role in [UserRole.Designer, UserRole.PatternDesigner]:
            docs = Document.objects.filter(category="Задание")

        elif self.request.user.role in [
            UserRole.Sewer,
            UserRole.PackerInspector,
        ]:
            docs = Document.objects.filter(category="тех. Задание")
        elif self.request.user.role in [UserRole.Cutter]:
            docs = Document.objects.filter(Q(category="тех. Задание") | Q(category="Заказ")).order_by("-id")
        else:
            docs = Document.objects.all().order_by("-id")

        context["docs"] = DocumentSerializer(docs, many=True).data
        context["batches"] = Batch.objects.order_by("-id")

        context["can_load_request"] = self.can_load_request
        context["can_load_result"] = self.can_load_result

        context["can_edit"] = self.can_edit

        return context


@method_decorator(csrf_exempt, name="dispatch")
class CreateDoc(View):
    def post(self, request: HttpRequest):
        d = json.loads(request.body)
        try:
            batch = Batch.objects.get(id=d["batch"])
            d["batch"] = batch
        except Batch.DoesNotExist:
            return JsonResponse({"message": "Партия с данным ID не найдена"}, status=404)
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
    def get(self, request: HttpRequest, id: str):
        id = int(id)
        material = get_object_or_404(Document, id=id)
        return JsonResponse({"document": DocumentSerializer(material).data})


@method_decorator(csrf_exempt, name="dispatch")
class AddDocumentResult(BaseView):
    enable_roles = [UserRole.PatternDesigner, UserRole.Designer, UserRole.Cutter, UserRole.PackerInspector]

    def post(self, request: HttpRequest, id: int):
        id = int(id)
        document = get_object_or_404(Document, id=id)
        files = request.FILES

        result = DocumentResult.objects.create(document=document, file=files["file"])

        return JsonResponse({"result_name": get_file_name(result.file)}, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class DeleteDocumentRequest(BaseView):
    def delete(self, request: HttpRequest, id: int):
        id = int(id)
        document = Document.objects.get(id=id)
        document.request = None
        document.save()

        return HttpResponse(status=204)


@method_decorator(csrf_exempt, name="dispatch")
class DeleteDocumentResult(BaseView):
    def delete(self, request: HttpRequest, id: int):
        id = int(id)
        DocumentResult.objects.get(id=id).delete()

        return HttpResponse(status=204)


@method_decorator(csrf_exempt, name="dispatch")
class EditDocument(BaseView):
    def post(self, request: HttpRequest, id: str):
        id = int(id)
        document = get_object_or_404(Document, id=id)
        files = request.FILES

        if files:
            if "file" in files:
                document.request = files["file"]

        else:
            d = json.loads(request.body)

            if "category" in d:
                document.category = d["category"]
            if "batch" in d:
                document.batch_id = d["batch"]

        document.save()

        return HttpResponse(status=202)


class FilterDocs(BaseView):
    enable_roles = [
        UserRole.Designer,
        UserRole.Sewer,
        UserRole.PatternDesigner,
        UserRole.PackerInspector,
        UserRole.Cutter,
    ]

    def get(self, request: HttpRequest):
        d = request.GET
        filters = Q()
        if request.user.role in [UserRole.Designer, UserRole.PatternDesigner]:
            filters &= Q(category="Задание")

        if request.user.role in [UserRole.Sewer, UserRole.PackerInspector]:
            filters &= Q(category="тех. Задание")

        if request.user.role in [UserRole.Cutter]:
            filters &= Q(category="тех. Задание") | Q(category="Заказ")

        print(d)
        if d["id"]:
            filters &= Q(id=d["id"])
        if d["batch"]:
            filters &= Q(batch_id=d["batch"])
        if d["category"]:
            filters &= Q(category=d["category"])

        docs = Document.objects.filter(filters).order_by("-id")

        return JsonResponse({"documents": DocumentSerializer(docs, many=True).data})
