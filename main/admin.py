from django.contrib import admin

from main.admin_form import CustomAuthenticationAdminForm
from main.models import Batch, DefectiveProducts, FinishedProducts, Materials, OveruseOfMaterials, User, Worker



from django.contrib import admin
from django.contrib.admin import AdminSite


class MyAdminSite(AdminSite):
    login_form = CustomAuthenticationAdminForm


admin.site = MyAdminSite()


admin.site.register(OveruseOfMaterials)
admin.site.register(DefectiveProducts)
admin.site.register(FinishedProducts)
admin.site.register(Materials)
admin.site.register(Batch)
admin.site.register(User)
admin.site.register(Worker)