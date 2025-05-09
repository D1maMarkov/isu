from rest_framework import serializers

from main.models import FinishedProducts, Materials, OveruseOfMaterials, User, DefectiveProducts as Defect, DocumentManagement as Document, Worker


class FinishedProductsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = FinishedProducts
        fields = '__all__'

    def get_id(self, obj):
        if obj.id < 100:
            return str(obj.id).zfill(3)
        return str(obj.id)
    

class MaterialsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = Materials
        fields = '__all__'

    def get_id(self, obj):
        if obj.id < 100:
            return str(obj.id).zfill(3)
        return str(obj.id)
    

class DocumentSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = '__all__'

    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    
    def get_updated_at(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M")

    def get_id(self, obj):
        if obj.id < 100:
            return str(obj.id).zfill(3)
        return str(obj.id)
    

class OverSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = OveruseOfMaterials
        fields = '__all__'

    def get_id(self, obj):
        if obj.id < 100:
            return str(obj.id).zfill(3)
        return str(obj.id)


class WorkerSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    date_begin = serializers.SerializerMethodField()
    date_end = serializers.SerializerMethodField()
    fullname = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = Worker
        fields = '__all__'

    def get_fullname(self, obj):
        return obj.user.fullname

    def get_role(self, obj):
        return obj.user.role

    def get_id(self, obj):
        if obj.id < 100:
            return str(obj.id).zfill(3)
        return str(obj.id)
    
    def get_date_begin(self, obj):
        return obj.date_begin.strftime("%Y-%m.%d")
    
    def get_date_end(self, obj):
        return obj.date_end.strftime("%Y-%m.%d")
    

class DefectSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = Defect
        fields = '__all__'

    def get_id(self, obj):
        if obj.id < 100:
            return str(obj.id).zfill(3)
        return str(obj.id)