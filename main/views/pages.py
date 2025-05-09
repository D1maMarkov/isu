from django.views.generic import TemplateView

from entities.user import UserRole
from main.models import FinishedProducts, Materials, OveruseOfMaterials as Overs, User, DefectiveProducts as Defects, DocumentManagement as Docs
from main.serializers import DefectSerializer, DocumentSerializer, FinishedProductsSerializer, MaterialsSerializer, OverSerializer, WorkerSerializer


class Index(TemplateView):
    template_name = "main/index.html"


class FinishedProductsPage(TemplateView):
    template_name = "main/products.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = FinishedProductsSerializer(FinishedProducts.objects.all(), many=True).data

        return context
    

class OverusesPage(TemplateView):
    template_name = "main/overuses.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["overs"] = OverSerializer(Overs.objects.all(), many=True).data

        return context
    

class WorkersPage(TemplateView):
    template_name = "main/workers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["workers"] = WorkerSerializer(User.objects.filter(role__in=UserRole.workers_list), many=True).data

        return context


class DefectsPage(TemplateView):
    template_name = "main/defects.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["defects"] = DefectSerializer(Defects.objects.all(), many=True).data

        return context
    

class DocsPage(TemplateView):
    template_name = "main/documents.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["docs"] = DocumentSerializer(Docs.objects.all(), many=True).data

        return context

class MaterialsPage(TemplateView):
    template_name = "main/materials.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["materials"] = MaterialsSerializer(Materials.objects.all(), many=True).data

        return context