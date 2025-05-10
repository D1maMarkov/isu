from django.http import FileResponse
from django.views.generic import TemplateView


class Index(TemplateView):
    template_name = "main/login.html"


class GetFile(TemplateView):
    def get(self, request, path):
        return FileResponse(open(path.replace("-", "/"), "rb"))
