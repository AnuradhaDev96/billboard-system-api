from rest_framework import serializers
from .models import AReclamborProfileModel, DbProfileModel, LoginProfileModel, BillboardByVendorModel, \
    BillboardVacancyModel, PurchaseBillboardModel, ScheduledTasksModel


class AReclambordProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AReclamborProfileModel
        fields = '__all__'


class DbProfileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DbProfileModel
        fields = '__all__'


class LoginProfileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model: LoginProfileModel
        fields = '__all__'


# billboardserializers
class BillboardVacancyByVendorModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillboardVacancyModel
        fields = '__all__'


class PurchaseBillboardModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseBillboardModel
        fields = '__all__'


class ScheduledTasksModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledTasksModel
        fields = '__all__'
