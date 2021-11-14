from django.db import models
from .enums import BillboardUserType, BillboardType, AdvertisementPackageType


# Create your models here.
class AReclamborProfileModel(models.Model):
    email: models.CharField(max_length=30)
    password: models.CharField(max_length=16)
    firstName: models.TextField()
    lastName: models.TextField()
    type: models.TextField(choices=BillboardUserType.choices(), default=BillboardUserType.CUSTOMER)


class DbProfileModel(models.Model):
    email: models.CharField(max_length=30)
    firstName: models.TextField()
    lastName: models.TextField()
    type: models.TextField(choices=BillboardUserType.choices(), default=BillboardUserType.CUSTOMER)


class LoginProfileModel(models.Model):
    email: models.CharField(max_length=30)
    password: models.CharField(max_length=16)


# inventory models
class BillboardVacancyModel(models.Model):
    vendorId: models.TextField()
    title: models.TextField()
    description: models.TextField()
    longitude: models.TextField()
    latitude: models.TextField()
    price: models.TextField()
    type: models.TextField(choices=BillboardType.choices(), default=BillboardType.SMALL)


# billboard models
class BillboardByVendorModel(models.Model):
    vendorId: models.CharField(max_length=30)
    width: models.CharField(max_length=16)
    height: models.CharField(max_length=16)
    location_lat: models.CharField(max_length=16)
    location_long: models.CharField(max_length=16)
    type: models.TextField(choices=BillboardType.choices(), default=BillboardType.SMALL)


class PurchaseBillboardModel(models.Model):
    billboardId: models.TextField()
    customerName: models.TextField()
    customerEmail: models.TextField()
    customerContactNo: models.TextField()
    designLink: models.TextField()
    packageType: models.TextField(choices=AdvertisementPackageType.choices(), default=AdvertisementPackageType.SILVER)
    customerId: models.TextField()


class ScheduledTasksModel(models.Model):
    purchaseId: models.TextField()
    task1Date: models.TextField()
    task2Date: models.TextField()
    task3Date: models.TextField()
    task4Date: models.TextField()
