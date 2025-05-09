from datetime import datetime
import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login
from main.serializers import WorkerSerializer
from utils.security.password_hasher import PasswordHasher
from main.models import Batch, User, Worker
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from slugify import slugify
import string
import random
from django.contrib.auth import logout
from django.shortcuts import redirect


@method_decorator(csrf_exempt, name="dispatch")
class Login(View):
    def post(self, request: HttpRequest):
        d = json.loads(request.body)
        try:
            user = User.objects.get(login=d["login"])
        except User.DoesNotExist:
            return JsonResponse({"message": "Нет пользователя с таким логином"}, status=404)
        
        if user.password != d["password"]:
            return JsonResponse({"message": "Неверный пароль"}, status=400)
        
        user = authenticate(**d)
        login(request, user)
        
        return HttpResponse(status=200)


def logout_view(request: HttpRequest):
    logout(request)
    return redirect("/docs/")

@method_decorator(csrf_exempt, name="dispatch")
class CreateWorker(View):
    password_hasher = PasswordHasher()

    def generate_random_string(self, length=5) -> str:
        characters = string.ascii_letters + string.digits
        return ''.join(random.choices(characters, k=length))

    def generate_login(self, second_name: str, name: str, patronymic: str) -> str:
        return slugify(second_name) + name[0].upper() + patronymic[0].upper() + self.generate_random_string()
    
    def post(self, request: HttpRequest):
        d = json.loads(request.body)

        #login = self.generate_login(*d["fullname"].split())
        #password = self.generate_random_string(length=11)
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
            filters &= Q(fullname=d["fullname"])

        workers = User.objects.filter(filters).order_by("-id")

        return JsonResponse({"workers": WorkerSerializer(workers, many=True).data})
    

class GetWorker(View):
    def get(self, request: HttpRequest, id: int):
        worker = get_object_or_404(User, id=id)
        return JsonResponse({"worker": WorkerSerializer(worker).data})
    
@method_decorator(csrf_exempt, name="dispatch")
class EditWorker(View):
    def post(self, request: HttpRequest, id: int):
        d = json.loads(request.body)
        worker = get_object_or_404(User, id=id)

        worker.fullname = d["fullname"]

        worker.save()

        return JsonResponse({"worker": WorkerSerializer(worker).data}, status=202)