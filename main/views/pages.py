from django.views.generic import TemplateView
from django.db.models import Q
from entities.user import UserRole
from main.views.base import BaseView
from main.models import FinishedProducts, Materials, OveruseOfMaterials as Overs, User, DefectiveProducts as Defects, DocumentManagement as Docs, Worker
from main.serializers import DefectSerializer, DocumentSerializer, FinishedProductsSerializer, MaterialsSerializer, OverSerializer, WorkerSerializer


class Index(TemplateView):
    template_name = "main/login.html"


class FinishedProductsPage(BaseView, TemplateView):
    template_name = "main/products.html"
    enable_roles = [UserRole.WarehouseManager, UserRole.Cutter]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = FinishedProductsSerializer(FinishedProducts.objects.all(), many=True).data

        return context


class OverusesPage(BaseView, TemplateView):
    template_name = "main/overuses.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["overs"] = OverSerializer(Overs.objects.all(), many=True).data

        return context


class WorkersPage(BaseView, TemplateView):
    template_name = "main/workers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["workers"] = WorkerSerializer(Worker.objects.all(), many=True).data

        context["users"] = User.objects.filter(role__in=[
            "Раскройщик",
            "Швея"
        ])

        return context


class DefectsPage(BaseView, TemplateView):
    template_name = "main/defects.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["defects"] = DefectSerializer(Defects.objects.all(), many=True).data

        return context


class DocsPage(BaseView, TemplateView):
    template_name = "main/documents.html"
    exclude_roles = [UserRole.WarehouseManager]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role in [
            UserRole.PackerInspector, 
            UserRole.Designer, 
            UserRole.PatternDesigner
        ]:
            docs = Docs.objects.filter(category="Задание")

        elif self.request.user.role in [
            UserRole.Sewer,
            UserRole.PackerInspector,
        ]:
            docs = Docs.objects.filter(category="тех. Задание")
        elif self.request.user.role in [UserRole.Cutter]:
            docs = Docs.objects.filter(Q(category="тех. Задание") | Q("Заказ")).order_by("-id")
        else:
            docs = Docs.objects.all().order_by("-id")

        context["docs"] = DocumentSerializer(docs, many=True).data
        return context


class MaterialsPage(BaseView, TemplateView):
    template_name = "main/materials.html"
    enable_roles = [UserRole.Cutter, UserRole.WarehouseManager, UserRole.PatternDesigner]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["materials"] = MaterialsSerializer(Materials.objects.all().order_by("-id"), many=True).data

        return context