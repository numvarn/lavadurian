from django.urls import path
from Cart import views

urlpatterns = [
    path('cart/show/', views.cartShow, name='cart-show'),
    path('cart/clear/', views.cartClear, name='cart-clear'),
    path('cart/checkout/', views.cartCheckout, name='cart-checkout'),
    path('cart/login/', views.cartLogin, name='cart-login'),
    path('cart/regis/', views.cartRegisterCustomer, name='cart-regis'),
    path('cart/add-address/', views.cartReceiverAddress, name='add-address'),
    path('cart/add/<int:id>', views.cartAdd, name='cart-add'),
    path('cart/completed/', views.cartProcessOrder, name='cart-completed'),
    path('item/delete/<int:id>', views.cartDelete, name='item-delete'),
    path('item/update/', views.itemUpdate, name="item-update"),
    path('order/my/', views.orderMy, name="order-my"),
    path('order/delete/<int:id>', views.orderDelete, name='order-delete'),
    path('order/detail/<int:id>', views.orderDetail, name="order-detail"),
    path('order/items/<int:id>/edit/',
         views.orderEditWeight, name='order-edit-weight'),
    path('message/save/', views.orderMessageSave),
    path('notif/save/', views.transferNotifSave),
    path('notif/delete/', views.notifDelete, name="notif-delete"),
    path('review/add/', views.reviewAdd),
    path('tracking/save/', views.trackingSave),
    path('api/get/shipping-status/', views.getShippingStatus),

    # สำหรับ export ข้อมูล
    path('export/receiveaddress', views.exportReceiveAddress),
]
