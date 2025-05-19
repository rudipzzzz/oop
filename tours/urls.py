from django.urls import path
from . import views

urlpatterns = [
    path('', views.tour_list, name='tour_list'),
    path('<slug:slug>/', views.tour_detail, name='tour_detail'),
    path('category/<int:category_id>/', views.category_tours, name='category_tours'),
    path('manage/', views.manage_tours, name='manage_tours'),
    path('create/', views.tour_create, name='tour_create'),
    path('edit/<slug:slug>/', views.tour_edit, name='tour_edit'),
    path('delete/<slug:slug>/', views.tour_delete, name='tour_delete'),
    path('dates/<int:tour_id>/', views.manage_tour_dates, name='manage_tour_dates'),
]