from rest_framework import generics, permissions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Items, Users, Orders, ItemsOrders
from .permissions import IsThisUser, IsOwner
from .serializers import ItemsSerializer, UsersSerializer, OrdersSerializer, AllOrdersOfUser


class ItemsList(generics.ListAPIView):
    queryset = Items.objects.all()
    serializer_class = ItemsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProductCreateView(generics.CreateAPIView):
    queryset = Items.objects.all()
    serializer_class = ItemsSerializer
    permission_classes = [permissions.IsAdminUser]


class ItemsCreate(generics.CreateAPIView):
    queryset = Items.objects.all()
    serializer_class = ItemsSerializer
    permission_classes = [permissions.IsAdminUser]

class ItemDetail(generics.RetrieveAPIView):
    queryset = Items.objects.all()
    serializer_class = ItemsSerializer



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
    permission_classes = [permissions.IsAuthenticated, IsThisUser]


class AllOrdersList(generics.ListAPIView):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [permissions.IsAdminUser]


class OrdersList(generics.CreateAPIView):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user, status='Pending')


class OrderDetail(generics.RetrieveDestroyAPIView):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]


class OrderUpdate(generics.RetrieveUpdateAPIView):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        serializer.save(user_id=self.request.user)


class AllOrdersOfUser(generics.ListAPIView):
    serializer_class = AllOrdersOfUser
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Orders.objects.filter(user_id=self.request.user)


class CustomAPIToken(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
