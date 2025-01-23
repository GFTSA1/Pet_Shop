from django.contrib.auth import authenticate
from django.http import HttpResponse, Http404
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins, generics, permissions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Items, Users, Orders, FavouriteItems
from .serializers import ItemsSerializer, UsersSerializer, FavouriteItemsSerializer, OrdersSerializer


class ItemsList(generics.ListCreateAPIView):
    queryset = Items.objects.all()
    serializer_class = ItemsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ItemDetail(generics.RetrieveAPIView):
    queryset = Items.objects.all()
    serializer_class = ItemsSerializer
    permission_classes = [permissions.IsAuthenticated]


class UsersList(generics.ListAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [permissions.IsAdminUser]

class UserListRegister(generics.CreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrdersList(generics.ListCreateAPIView):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [permissions.IsAuthenticated]


    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)

class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save(user_id=self.request.user.id)


class CustomAPIToken(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
