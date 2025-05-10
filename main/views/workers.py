import json
from datetime import datetime

from django.db.models import Q
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from main.models import Batch, User, Worker
from main.serializers import WorkerSerializer
from main.views.base import BaseView


class WorkersPage(BaseView, TemplateView):
    template_name = "main/workers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["workers"] = WorkerSerializer(Worker.objects.order_by("-id"), many=True).data

        context["users"] = User.objects.filter(role__in=["Раскройщик", "Швея"])

        context["batches"] = Batch.objects.all()

        return context


@method_decorator(csrf_exempt, name="dispatch")
class CreateWorker(View):
    def post(self, request: HttpRequest):
        d = json.loads(request.body)

        try:
            batch = Batch.objects.get(id=d["batch"])
        except Batch.DoesNotExist:
            return JsonResponse({"message": "Нет партии с таким ID"}, status=404)

        worker = Worker.objects.create(
            user_id=d["user"],
            batch=batch,
            date_begin=datetime.strptime(d["date_begin"], "%Y-%m-%d"),
            date_end=datetime.strptime(d["date_end"], "%Y-%m-%d"),
            status=d["status"],
        )

        return JsonResponse({"worker": WorkerSerializer(worker).data}, status=201)


class FilterWorkers(View):
    def get(self, request: HttpRequest):
        d = request.GET
        filters = Q()

        if d["status"]:
            filters &= Q(status=d["status"])
        if d["id"]:
            filters &= Q(id=d["id"])
        if d["fullname"]:
            filters &= Q(user__fullname=d["fullname"])
        if d["batch"]:
            filters &= Q(batch_id=d["batch"])

        workers = Worker.objects.filter(filters).order_by("-id")

        return JsonResponse({"workers": WorkerSerializer(workers, many=True).data})


class GetWorker(View):
    def get(self, request: HttpRequest, id: int):
        worker = get_object_or_404(Worker, id=id)
        return JsonResponse({"worker": WorkerSerializer(worker).data})


@method_decorator(csrf_exempt, name="dispatch")
class EditWorker(View):
    def post(self, request: HttpRequest, id: int):
        d = json.loads(request.body)
        worker = get_object_or_404(Worker, id=id)

        worker.status = d["status"]
        worker.batch_id = int(d["batch"])
        worker.date_begin = datetime.strptime(d["date_begin"], "%Y-%m-%d")
        worker.date_end = datetime.strptime(d["date_end"], "%Y-%m-%d")

        worker.save()

        return JsonResponse({"worker": WorkerSerializer(worker).data}, status=202)
