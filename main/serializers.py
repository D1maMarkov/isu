from rest_framework import serializers

from main.models import Batch
from main.models import DefectiveProducts as Defect
from main.models import DocumentManagement as Document
from main.models import (
    DocumentResult,
    FinishedProducts,
    Materials,
    OveruseOfMaterials,
    Worker,
)
from utils.get_file_name import get_file_name


class FinishedProductsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = FinishedProducts
        fields = "__all__"

    def get_id(self, obj):
        return str(obj.id).zfill(3)


class MaterialsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = Materials
        fields = "__all__"

    def get_id(self, obj):
        return str(obj.id).zfill(4)


class ResultSerialzier(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return "/file/" + str(obj.file).replace("/", "-")

    def get_name(self, obj):
        return get_file_name(obj.file)

    class Meta:
        model = DocumentResult
        fields = ["id", "name", "url"]


class DocumentSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    request_name = serializers.SerializerMethodField()
    results = serializers.SerializerMethodField()
    request_url = serializers.SerializerMethodField()

    def get_request_url(self, obj):
        return "/file/" + str(obj.request).replace("/", "-")

    def get_request_name(self, obj):
        return get_file_name(obj.request)

    class Meta:
        model = Document
        fields = [
            "id",
            "batch",
            "status",
            "request",
            "category",
            "results",
            "updated_at",
            "created_at",
            "request_name",
            "request_url",
        ]

    def get_results(self, obj):
        return ResultSerialzier(obj.results.all(), many=True).data

    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")

    def get_updated_at(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M")

    def get_id(self, obj):
        return str(obj.id).zfill(3)


class OverSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    material = MaterialsSerializer()

    class Meta:
        model = OveruseOfMaterials
        fields = "__all__"

    def get_id(self, obj):
        return str(obj.id).zfill(3)


class WorkerSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    date_begin = serializers.SerializerMethodField()
    date_end = serializers.SerializerMethodField()
    fullname = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = Worker
        fields = "__all__"

    def get_fullname(self, obj):
        return obj.user.fullname

    def get_role(self, obj):
        return obj.user.role

    def get_id(self, obj):
        return str(obj.id).zfill(3)

    def get_date_begin(self, obj):
        return obj.date_begin.strftime("%Y-%m-%d")

    def get_date_end(self, obj):
        return obj.date_end.strftime("%Y-%m-%d")


class DefectSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    report_name = serializers.SerializerMethodField()

    def get_report_name(self, obj):
        return get_file_name(obj.report)

    class Meta:
        model = Defect
        fields = ["id", "batch", "quantity", "description", "report", "report_name"]

    def get_id(self, obj):
        return str(obj.id).zfill(3)


class BatchSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return str(obj)

    class Meta:
        model = Batch
        fields = ["id", "name"]
