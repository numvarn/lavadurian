from django.urls import path
from Members import views

urlpatterns = [
    path('members/register', views.registerTrader, name='member-regis'),
    path('members/login', views.userLogin, name='member-login'),
    path('members/logout', views.Logout, name='member-logout'),
    path('members/password-recover', views.passwordRecovery,
         name='member-pasword-recover'),
    path('customer/register', views.registerCustomer, name='customer-regis'),

    path('gi/list', views.listGIPage, name='gi-list'),

    path('import/registerGI', views.importRegisterGI),
]
