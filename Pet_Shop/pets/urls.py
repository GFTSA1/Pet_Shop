from django.urls import path
from . import views

urlpatterns = [
    path("items/", views.ItemsList.as_view()),
    path("items/<int:pk>/", views.ItemDetail.as_view()),
    path("users/", views.UsersList.as_view()),
    path("users/<int:pk>/", views.UserDetail.as_view()),
    path("orders/", views.OrdersList.as_view()),
    path("orders/all/", views.AllOrdersList.as_view()),
    path("orders/<int:pk>/", views.OrderDetail.as_view()),
    path('users/<int:pk>/orders/', views.AllOrdersOfUser.as_view()),
]
