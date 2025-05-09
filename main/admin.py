from django.contrib import admin

from main.models import Batch, DefectiveProducts, FinishedProducts, Materials, OveruseOfMaterials, User


admin.site.register(OveruseOfMaterials)
admin.site.register(DefectiveProducts)
admin.site.register(FinishedProducts)
admin.site.register(Materials)
admin.site.register(Batch)
admin.site.register(User)