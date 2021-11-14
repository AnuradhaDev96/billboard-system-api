from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from areclambord_api.pyrebase_settings import db, auth
from .enums import BillboardUserType, BillboardType, AdvertisementPackageType

import schedule
import time
import sched
import json
from datetime import timedelta, date
import numpy as np
import pandas as pd
from tensorflow import keras
from ast import literal_eval as make_tuple
from geopy.distance import geodesic

# Create your views here.


from UserManagement.serializers import AReclambordProfileSerializer, DbProfileModelSerializer, \
    LoginProfileModelSerializer, BillboardVacancyByVendorModelSerializer, PurchaseBillboardModelSerializer, \
    ScheduledTasksModelSerializer
from UserManagement.models import DbProfileModel, AReclamborProfileModel


@api_view(['POST'])
def signup_user(request):
    user_data = JSONParser().parse(request)
    user_type = user_data.get('type')
    if user_type == BillboardUserType.CUSTOMER.value or user_type == BillboardUserType.VENDOR.value or user_type == BillboardUserType.ADMIN.value:
        user_data["type"] = user_type
    else:
        user_data["type"] = BillboardUserType.CUSTOMER.value

    user_serializer = AReclambordProfileSerializer(data=user_data)
    if user_serializer.is_valid():
        db_user_serializer = {
            'email': user_data.get('email'),
            'firstName': user_data.get('firstName'),
            'lastName': user_data.get('lastName'),
            'type': user_data.get('type')
        }
    else:
        return JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = auth.create_user_with_email_and_password(user_data.get('email'), user_data.get('password'))
        db.child("System_Users").child(user['localId']).set(db_user_serializer)
        return JsonResponse({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        # exception_message = traceback.format_exc()
        return JsonResponse({'message': 'Email id invalid or already exists.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def signin_user(request):
    login_data = JSONParser().parse(request)
    try:
        user = auth.sign_in_with_email_and_password(login_data.get('email'), login_data.get('password'))
        signed_in_user = db.child("System_Users").order_by_key().equal_to(user['localId']).limit_to_first(1).get()
        return JsonResponse({
            'message': 'Logged in successfully.',
            'localId': user['localId'],
            'email': list(signed_in_user.val().values())[0].get('email'),
            'firstName': list(signed_in_user.val().values())[0].get('firstName'),
            'lastName': list(signed_in_user.val().values())[0].get('lastName'),
            'type': list(signed_in_user.val().values())[0].get('type')
        }, status=status.HTTP_200_OK)
    except Exception as e:
        # exception_message = traceback.format_exc()
        return Response({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def create_billboard_vacancy_by_vendor(request):
    billboard_data = JSONParser().parse(request)
    billboard_type = billboard_data.get('type')
    if billboard_type == BillboardType.LARGE.value or billboard_type == BillboardType.MEDIUM.value or billboard_type == BillboardType.SMALL.value:
        billboard_data["type"] = billboard_type
    else:
        billboard_data["type"] = BillboardType.SMALL.value

    billboard_serializer = BillboardVacancyByVendorModelSerializer(data=billboard_data)
    if billboard_serializer.is_valid():
        db_billboard_serializer = {
            'vendorId': billboard_data.get('vendorId'),
            'title': billboard_data.get('title'),
            'description': billboard_data.get('description'),
            'latitude': billboard_data.get('latitude'),
            'longitude': billboard_data.get('longitude'),
            'price': billboard_data.get('price'),
            'type': billboard_data.get('type')  # editz
        }
    else:
        return JsonResponse(billboard_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        db.child("Billboard_Vacancy").push(db_billboard_serializer)
        return JsonResponse({'message': 'Billboard vacancy created successfully'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        # exception_message = traceback.format_exc()
        return JsonResponse({'message': 'An error occurred'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def purchase_billboard_by_customer(request):
    vacancy_data = JSONParser().parse(request)
    billboardId = vacancy_data.get('billboardId')
    purchase_serializer = PurchaseBillboardModelSerializer(data=vacancy_data)
    if purchase_serializer.is_valid():
        db_purchase_serializer = {
            'billboardId': vacancy_data.get('billboardId'),
            'customerName': vacancy_data.get('customerName'),
            'customerEmail': vacancy_data.get('customerEmail'),
            'customerContactNo': vacancy_data.get('customerContactNo'),
            'designLink': vacancy_data.get('designLink'),
            'packageType': vacancy_data.get('packageType'),
            'customerId': vacancy_data.get('customerId')
        }
    else:
        return JsonResponse(purchase_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        selected_billboard = db.child("Billboard_Vacancy").order_by_key().equal_to(billboardId).limit_to_first(1).get()
        if selected_billboard.val() is None:
            return JsonResponse({'message': 'Billboard does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            sd = db.child("Billboard_Purchases").push(db_purchase_serializer)
            print(sd['name'])
            events = schedule_tasks(selected_billboard)
            return JsonResponse(
                {'message': 'Advertisement created and Schedule generated successfully', 'schedule': events,
                 'purchaseId': sd['name']}, status=status.HTTP_201_CREATED)
    except Exception as e:
        # exception_message = traceback.format_exc()
        return JsonResponse({'message': 'An error occurred'}, status=status.HTTP_400_BAD_REQUEST)


def schedule_tasks(selected_billboard):
    schedule_list = []
    df = pd.read_csv('UserManagement/neighbouringboards.csv')
    sheduling_model = keras.models.load_model('UserManagement/SchedulingANN.h5')

    # selected_billboard = db.child("Billboard_Vacancy").order_by_key().equal_to(billboardId).limit_to_first(1).get()
    if selected_billboard.val() is None:
        return schedule_list
    else:
        category = list(selected_billboard.val().values())[0].get('type')
        cent_latitude = list(selected_billboard.val().values())[0].get('latitude')
        cent_longitude = list(selected_billboard.val().values())[0].get('longitude')
        print(category)
        print(cent_latitude)
        print(cent_longitude)

        if category == "Digital":
            category = "Old"
        elif category == "Large":
            category = "Mature"
        elif category == "Medium":
            category = "Middle"
        else:
            category = "Young or Teen"

        # print(category)
        # return JsonResponse(selected_billboard.val(), status=status.HTTP_200_OK)
        selected = df[df["Category"] == category].reset_index()
        selected['Location'] = selected['Location'].apply(lambda x: make_tuple(x))
        selected['distance'] = selected['Location'].apply(lambda x: geodesic(x, (cent_latitude, cent_longitude)).m)

        closest5 = selected.nsmallest(5, ['distance'])
        avgdistance = np.mean(closest5[['distance']])[0]
        closest5['EndDate'] = pd.to_datetime(closest5['EndDate'])
        closest5['Today'] = pd.to_datetime(date.today())
        days = np.mean(closest5['Today'] - closest5['EndDate'])
        days = days.days

        inputs = np.array([days, avgdistance])
        inputs = inputs.reshape(1, -1)
        prediction = sheduling_model.predict(inputs)
        arg = np.argmax(prediction[0])
        _today = date.today()
        print(arg)
        if arg == 0:  # 30
            schedule_list.extend(
                [_today + timedelta(days=2), _today + timedelta(days=4), _today + timedelta(days=25),
                 _today + timedelta(days=30)])
            return schedule_list
        elif arg == 1:  # 45
            schedule_list.extend(
                [_today + timedelta(days=3), _today + timedelta(days=4), _today + timedelta(days=40),
                 _today + timedelta(days=45)])
            return schedule_list
        else:  # 60
            schedule_list.extend(
                [_today + timedelta(days=4), _today + timedelta(days=5), _today + timedelta(days=50),
                 _today + timedelta(days=60)])
            return schedule_list


@api_view(['GET'])
def get_billboard_vacancies(request, *args, **kwargs):
    try:
        vacancies = db.child("Billboard_Vacancy").get()
        return JsonResponse(vacancies.val(), status=status.HTTP_200_OK)
    except Exception as e:
        # exception_message = traceback.format_exc()
        return JsonResponse({'message': e}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def eval_progress(request):
    evaluate_data = JSONParser().parse(request)
    # records = pd.read_csv("inferenceset.csv")
    suggestion = inputprepare(evaluate_data.get("billboardCategory"), evaluate_data.get("latitude"),
                              evaluate_data.get("longitude"))
    return JsonResponse({'message': suggestion}, status=status.HTTP_200_OK)


def inputprepare(billboardcat, billat, billong):
    df = pd.read_csv("UserManagement/inferenceset.csv")
    inputdata = pd.DataFrame()
    inputdata['Mature'] = df['IDNo'].apply(lambda x: 1 if 85 < int(str(x)[:2]) < 95 else 0)
    inputdata['Middle'] = df['IDNo'].apply(lambda x: 1 if 61 < int(str(x)[:2]) < 85 else 0)
    inputdata['Old'] = df['IDNo'].apply(lambda x: 1 if 41 < int(str(x)[:2]) < 61 else 0)
    inputdata['Young or Teen'] = df['IDNo'].apply(
        lambda x: 1 if not (85 < int(str(x)[:2]) < 95 or 61 < int(str(x)[:2]) < 85 or 41 < int(str(x)[:2]) < 61) else 0)
    inputdata['startlat'] = df['Start'].apply(lambda x: make_tuple(x)[0])
    inputdata['startlong'] = df['Start'].apply(lambda x: make_tuple(x)[1])
    inputdata['point1_lat'] = df['RandomPoint1'].apply(lambda x: make_tuple(x)[0])
    inputdata['point1_long'] = df['RandomPoint1'].apply(lambda x: make_tuple(x)[1])
    inputdata['point2_lat'] = df['RandomPoint2'].apply(lambda x: make_tuple(x)[0])
    inputdata['point2_long'] = df['RandomPoint2'].apply(lambda x: make_tuple(x)[1])
    inputdata['endlat'] = df['End'].apply(lambda x: make_tuple(x)[0])
    inputdata['endlong'] = df['End'].apply(lambda x: make_tuple(x)[1])
    inputdata['billlat'] = billat
    inputdata['billlong'] = billong
    inputdata['billMature'] = 1 if billboardcat == BillboardType.MEDIUM.value else 0
    inputdata['billMiddle'] = 1 if billboardcat == BillboardType.LARGE.value else 0
    inputdata['billOld'] = 1 if billboardcat == BillboardType.DIGITAL.value else 0
    inputdata['billYoung or teen'] = 1 if billboardcat == BillboardType.SMALL.value else 0
    inputdata = inputdata.round(
        {"startlat": 4, "startlong": 4, "point1_lat": 4, "point1_long": 4, "point2_lat": 4, "point2_long": 4,
         "endlat": 4, "endlong": 4, "billlat": 4, "billlong": 4})
    ANNmodel = keras.models.load_model('UserManagement/ANN.h5')
    predictions = ANNmodel.predict(inputdata)
    predictions = (predictions > 0.5).astype(np.float32)
    predictions = predictions.reshape(-1, )
    targetscovered = predictions.shape[0] - np.count_nonzero(predictions == 0)
    print(targetscovered)
    if targetscovered <= 1000:
        # remove the billboard
        return "REMOVE"

    elif 1000 < targetscovered <= 3000:
        # Buy Silver Subscription
        return "CHANGE_SUBSCRIPTION"

    else:
        # Buy Gold Subscription
        return "MAINTAIN"


# @api_view(['GET'])
def get_purchased_billboard_by_bilboardId(request, billboardId=None):
    try:
        selected_billboard = db.child("Billboard_Vacancy").order_by_key().equal_to(billboardId).limit_to_first(1).get()
        # print(selected_billboard.val())
        if selected_billboard.val() == None:
            return JsonResponse({"message": "Billboard does not exist"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return JsonResponse(selected_billboard.val(), status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': e}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def save_scheduled_tasks(request):
    scheduled_tasks_data = JSONParser().parse(request)

    task_serializer = ScheduledTasksModelSerializer(data=scheduled_tasks_data)
    if task_serializer.is_valid():
        db_task_serializer = {
            'purchaseId': scheduled_tasks_data.get('purchaseId'),
            'task1Date': scheduled_tasks_data.get('task1Date'),
            'task2Date': scheduled_tasks_data.get('task2Date'),
            'task3Date': scheduled_tasks_data.get('task3Date'),
            'task4Date': scheduled_tasks_data.get('task4Date')
        }
    else:
        return JsonResponse(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        db.child("ScheduledCampaignTasks").push(db_task_serializer)
        return JsonResponse({'message': 'Scheduled campaign tasks saved successfully'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        # exception_message = traceback.format_exc()
        return JsonResponse({'message': 'An error occurred'}, status=status.HTTP_400_BAD_REQUEST)


def get_published_billboards_byVendorId(request, vendorId=None):
    try:
        billboards_of_vendor = db.child("Billboard_Vacancy").order_by_child("vendorId").equal_to(vendorId).get()
        return JsonResponse(billboards_of_vendor.val(), status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': e}, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])

def get_purchased_billboards_bycustomerId(request, customerId=None):
    try:
        purchased_billboards = db.child("Billboard_Purchases").order_by_child("customerId").equal_to(customerId).get()
        # print(purchased_billboards.val())
        return JsonResponse(purchased_billboards.val(), status=status.HTTP_200_OK)
    except Exception as e:
        # exception_message = traceback.format_exc()
        return JsonResponse({'message': e}, status=status.HTTP_400_BAD_REQUEST)


def delete_purchase(request, purchaseId=None):
    try:
        db.child("Billboard_Purchases").child(purchaseId).remove()
        # print(purchased_billboards.val())
        return JsonResponse({'message': "Purchase deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        # exception_message = traceback.format_exc()
        return JsonResponse({'message': e}, status=status.HTTP_400_BAD_REQUEST)


def delete_billboard(request, billboardId=None):
    try:
        db.child("Billboard_Vacancy").child(billboardId).remove()
        # print(purchased_billboards.val())
        return JsonResponse({'message': "Billboard deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        # exception_message = traceback.format_exc()
        return JsonResponse({'message': e}, status=status.HTTP_400_BAD_REQUEST)


def get_published_billboards_by_type(request, type=None):
    try:
        billboards_of_vendor = db.child("Billboard_Vacancy").order_by_child("type").equal_to(type).get()
        # if billboards_of_vendor
        return JsonResponse(billboards_of_vendor.val(), status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': e}, status=status.HTTP_400_BAD_REQUEST)
