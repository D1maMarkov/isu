from datetime import datetime
import json
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from main.serializers import WorkerSerializer
from utils.security.password_hasher import PasswordHasher
from main.models import Batch, User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from slugify import slugify
import string
import random


class Login(View):
    password_hasher = PasswordHasher()
    
    def get(self, login: str, password: str):
        try:
            user = User.objects.get(login=login)
        except User.DoesNotExist:
            return JsonResponse({"message": "Нет пользователя с таким логином"}, status=404)
        
        hashed_password = self.password_hasher.hash_password(password)
        if user.hash_password == hashed_password:
            self.request.auth(user)
        
        return JsonResponse({"message": "Неверный пароль"}, status=400)


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

        login = self.generate_login(*d["fullname"].split())
        password = self.generate_random_string(length=11)

        batch = Batch.objects.get(id=d["batch"])
        worker = User.objects.create(
            fullname=d["fullname"],
            batch=batch,
            date_begin=datetime.strptime(d["date_begin"], "%Y-%m-%d"),
            date_end=datetime.strptime(d["date_end"], "%Y-%m-%d"),
            status=d["status"],

            login=login,
            hash_password=password,
            role=d["role"]
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

        workers = User.objects.filter(filters)

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