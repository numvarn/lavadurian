from django.urls import path, include
from rest_framework import routers

from DurianAPI.views import BookBankCreateAPI, BookBankDeleteAPI, BookBankUpdateAPI, GetOrderStatusAPI, GetStoreAllAPI, OrderShippingUpdateAPI, OrderStatusUpdateAPI, OrderWeightUpdateAPI, ProductImageAddAPI, ProductImageDeleteAPI, QRCodeAddAPI, QRCodeDeleteAPI, SetStoreStatusAPI, TransferCheckAPI, UpdateLocationAPI, UserViewSet, GetMyUserViewSet, LoginAPI, UserRegisAPI, CheckCitizenIDAPI, CheckEmailAPI
from DurianAPI.views import AddNewStoreAPI, UpdateStoreAPI, DeleteStoreAPI
from DurianAPI.views import ProductCreateAPI, ProductUpdateAPI, ProductDeleteAPI, GetStoreProfileAPI, StoreViewSet

router = routers.DefaultRouter()
router.register('api/user/get', UserViewSet)
router.register('api/stores/list', StoreViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/login', LoginAPI),
    path('api/regis', UserRegisAPI),

    path('api/product/add', ProductCreateAPI),
    path('api/product/edit', ProductUpdateAPI),
    path('api/product/delete', ProductDeleteAPI),

    path('api/product-img/add', ProductImageAddAPI),
    path('api/product-img/delete', ProductImageDeleteAPI),

    path('api/store/get', GetStoreProfileAPI),
    path('api/store/all', GetStoreAllAPI),
    path('api/order/status', GetOrderStatusAPI),

    path('api/order/update', OrderStatusUpdateAPI),
    path('api/order/weight', OrderWeightUpdateAPI),
    path('api/order/shipping', OrderShippingUpdateAPI),

    path('api/store/add', AddNewStoreAPI),
    path('api/store/edit', UpdateStoreAPI),
    path('api/store/delete', DeleteStoreAPI),
    path('api/store/status', SetStoreStatusAPI),
    path('api/store/checkin', UpdateLocationAPI),

    path('api/qrcode/delete', QRCodeDeleteAPI),
    path('api/qrcode/add', QRCodeAddAPI),

    path('api/bookbank/edit', BookBankUpdateAPI),
    path('api/bookbank/add', BookBankCreateAPI),
    path('api/bookbank/delete', BookBankDeleteAPI),

    path('api/check/id', CheckCitizenIDAPI),
    path('api/check/email', CheckEmailAPI),
    path('api/check/transfer', TransferCheckAPI),
    path('api/user/me', GetMyUserViewSet.as_view()),
]
