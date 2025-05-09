from django.urls import path
from main.views.documents import CreateDoc, delete_document, get_document
from main.views.defects import CreateDefect, delete_defect, filter_defects, get_defect
from main.views.users import CreateWorker, EditWorker, FilterWorkers, GetWorker
from main.views.overuses import CreateOver, delete_over, edit_over, filter_overs, get_over
from main.views.products import CreateFinishedProduct, delete_product, edit_product, filter_products, get_product
from main.views.materials import CreateMaterial, delete_material, edit_material, filter_materials, get_material
from main.views.pages import DefectsPage, DocsPage, FinishedProductsPage, Index, MaterialsPage, OverusesPage, WorkersPage


urlpatterns = [
    path("", Index.as_view()),
    path("warehouse/products/", FinishedProductsPage.as_view()),
    path("warehouse/materials/", MaterialsPage.as_view()),
    path("warehouse/overuse/", OverusesPage.as_view()),

    path("materials/add", CreateMaterial.as_view()),
    path("materials/delete/", delete_material),
    path("materials/get/<id>", get_material),
    path("materials/edit/<id>", edit_material),
    path("materials/filter/", filter_materials),

    path("products/add/", CreateFinishedProduct.as_view()),
    path("products/delete/<id>", delete_product),
    path("products/get/<id>", get_product),
    path("products/edit/<id>/", edit_product),
    path("products/filter/", filter_products),

    path("overs/add/", CreateOver.as_view()),
    path("overs/delete/<id>", delete_over),
    path("overs/get/<id>", get_over),
    path("overs/edit/<id>/", edit_over),
    path("overs/filter/", filter_overs),

    path("ceh/workers/", WorkersPage.as_view()),
    path("ceh/workers/get/<id>", GetWorker.as_view()),
    path("ceh/workers/edit/<id>", EditWorker.as_view()),
    path("ceh/worker/add/", CreateWorker.as_view()),
    path("ceh/workers/filter/", FilterWorkers.as_view()),

    path("ceh/defects/", DefectsPage.as_view()),
    path("ceh/defects/add/", CreateDefect.as_view()),
    path("ceh/defects/filter/", filter_defects),
    path("ceh/defects/delete/<id>/", delete_defect),
    path("ceh/defects/get/<id>/", get_defect),

    path("docs/", DocsPage.as_view()),
    path("docs/add/", CreateDoc.as_view()),
    path("docs/get/<id>/", get_document),
    path("docs/delete/<id>/", delete_document),
]
