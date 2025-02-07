from django.urls import path

from . import views
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView
from .views import ProductListView

urlpatterns = [
    path("items/", views.ItemsList.as_view()),
    path("items/<int:pk>/", views.ItemDetail.as_view()),
    path("users/", views.UsersList.as_view()),
    path("users/<int:pk>/", views.UserDetail.as_view()),
    path("orders/", views.OrdersList.as_view()),
    path("orders/all/", views.AllOrdersList.as_view()),
    path("orders/<int:pk>/", views.OrderDetail.as_view()),
    path("orders/<int:pk>/", views.OrderUpdate.as_view()),
    path('users/<int:pk>/orders/', views.AllOrdersOfUser.as_view()),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('products/', ProductListView.as_view(), name='product-list'),

]
