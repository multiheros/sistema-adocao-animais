from django.urls import path
from . import views

urlpatterns = [
    path('', views.adoption_list, name='adoption_list'),
    path('adoption/<int:pk>/', views.adoption_detail, name='adoption_detail'),
    path('adoption/new/', views.adoption_create, name='adoption_create'),
    path('adoption/<int:pk>/edit/', views.adoption_update, name='adoption_edit'),
    path('adoption/<int:pk>/delete/', views.adoption_delete, name='adoption_delete'),
]