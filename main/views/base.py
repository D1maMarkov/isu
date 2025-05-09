from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View

from entities.user import UserRole


class BaseView(View):
    def get_enable_roles(self):
        enable = getattr(self, "enable_roles", [])
        if enable:
            return enable
        
        exclude = getattr(self, "exclude_roles", [])
        if exclude:
            return set([i.value for i in UserRole]) - set(exclude)
        
        return [i.value for i in UserRole]

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return HttpResponseRedirect('/')
        print(user.login)
        print(user.__dict__)
        if user.role == UserRole.GeneralManager or user.role == UserRole.ProductionManager:
            return super().dispatch(request, *args, **kwargs)

        if user.role not in self.get_enable_roles():
            return render(request, "main/protect.html")

        return super().dispatch(request, *args, **kwargs)