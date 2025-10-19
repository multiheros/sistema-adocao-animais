from django.urls import path
from . import views

urlpatterns = [
    path('', views.animal_list, name='animal_list'),
    path('animal/<int:pk>/', views.animal_detail, name='animal_detail'),
    path('animal/new/', views.animal_create, name='animal_create'),
    path('animal/<int:pk>/edit/', views.animal_update, name='animal_edit'),
    path('animal/<int:pk>/delete/', views.animal_delete, name='animal_delete'),
]