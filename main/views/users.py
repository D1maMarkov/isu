import json

from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from main.models import User


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
