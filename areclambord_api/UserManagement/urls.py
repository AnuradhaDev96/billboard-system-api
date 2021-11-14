from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_user),
    path('signin/', views.signin_user),
    path('create-bill-vacancy/', views.create_billboard_vacancy_by_vendor),
    path('purchase-billboard/', views.purchase_billboard_by_customer),
    path('get-vacancies/', views.get_billboard_vacancies),
    path('evaluate-progress/', views.eval_progress),
    path('get-purchased-billboards/<str:customerId>/', views.get_purchased_billboards_bycustomerId),
    path('getbyid/<str:billboardId>/', views.get_purchased_billboard_by_bilboardId),
    path('save-schedule/', views.save_scheduled_tasks),
    path('get-vacancies-byvendorid/<str:vendorId>/', views.get_published_billboards_byVendorId),
    path('delete-purchase/<str:purchaseId>/', views.delete_purchase),
    path('delete-billboard/<str:billboardId>/', views.delete_billboard),
    path('vacancy/get-by-type/<str:type>/', views.get_published_billboards_by_type),
]

