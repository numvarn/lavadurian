from django.urls import path
from Pages import views

urlpatterns = [
    path('', views.Home, name="home"),
    path('desc/', views.DescPage, name="desc"),
    path('desc/sales/', views.saleDesc, name="desc-sales")
]