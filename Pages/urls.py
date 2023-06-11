from django.urls import path
from Pages import views

urlpatterns = [
    path('', views.Home, name="home"),
    path('desc/', views.DescPage, name="desc"),
    path('desc/sales/', views.saleDesc, name="desc-sales"),
    path('register/cutter', views.registerCutter, name="regis-cutter"),
    path('register/packing-house', views.registerPackingHouse,
         name="regis-packing-house"),

]
