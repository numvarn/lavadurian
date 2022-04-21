from django.urls import path
from Store import views

urlpatterns = [
    path('store/manage/', views.storePage, name='store-front'),
    path('store/manage/<int:id>', views.storeManage, name='store-setting'),
    path('store/manage/<int:id>/add/', views.storeAddProduct, name='store-add'),
    path('store/manage/<int:id>/edit/', views.storeEdit, name='store-edit'),
    path('store/manage/<int:id>/sales/',
         views.stroeSalesCheck, name='store-sales'),
    path('store/product/<int:id>', views.storeProductDetail, name='store-product'),
    path('store/product/<int:id>/edit/',
         views.storeProductEdit, name='store-product-edit'),
    path('store/product/<int:id>/delete/',
         views.deleteProduct, name='store-product-delete'),
    path('store/certificate/<int:id>',
         views.showCertificate, name='store-certificate'),
    path('store/location/<int:id>', views.storeLocation, name='store-location'),
    path('store/list/', views.storeListView, name='store-list-view'),
    path('image/<int:id>/delete/', views.deleteProductImage, name='image-delete'),
    path('shopping/', views.shoppingPage, name='shopping'),
    path('shopping-font-ajax/', views.shoppingPageAjax),
    path('shopping/product/<int:id>', views.shoppingProductView,
         name='shopping-product-view'),
    path('bookbank/save/', views.storeAddBookBank),
    path('bookbank/<int:id>/delte/',
         views.storeDeleteBookBank, name="bookbank-delete"),
    path('sendmail/', views.sendMail)
]
