from django.urls import path
from News import views

urlpatterns = [
    path('news/', views.newsPage, name='news-page'),
    path('news/<int:id>', views.newsDetail, name='news-detail'),
]