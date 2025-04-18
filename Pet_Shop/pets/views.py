from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics, permissions, mixins, filters, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view
from .filters import ItemsFilter

from .models import Items, Users, Orders, PasswordReset, Category
from .permissions import IsThisUser, IsOwner
from .serializers import (
    ItemsSerializer,
    UsersSerializer,
    OrdersSerializer,
    AllOrdersOfUser,
    ResetPasswordSerializer,
    ActuallyResetPasswordSerializer,
    FavouriteItemsSerializer,
    CustomTokenSerializer,
    CategorySerializer,
)

import os

from .. import settings


class ItemView(
    generics.GenericAPIView,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    queryset = Items.objects.all()
    serializer_class = ItemsSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ItemsFilter
    search_fields = ["title", "description"]
    ordering_fields = ["price"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def get(self, requset, *args, **kwargs):
        return self.list(requset, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)

        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class CategoryView(
    generics.GenericAPIView,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def get(self, requset, *args, **kwargs):
        return self.list(requset, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)

        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


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
        serializer.save(user_id=self.request.user, status="Pending")

        if serializer.is_valid():
            user = Users.objects.get(id=self.request.user.id)
            items = serializer.validated_data["items"]
            item_support_list = []
            for item in items:
                item_support_list.append(
                    f"Item: {item['item_id']}, Quantity: {item['quantity']}\n"
                )
            items_string = "".join(item_support_list)

            if user:
                send_mail(
                    subject=f"Order Confirmation {serializer.data['id']}",
                    message=f"Your Order Id is: {serializer.data['id']} \n\n\n"
                    f"The items are: {items_string}\n\n",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )


class OrderDetail(generics.RetrieveDestroyAPIView):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]


class OrderUpdate(generics.RetrieveUpdateAPIView):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [permissions.IsAdminUser]

    # TODO: It is a bug, because if admin updates order it will asign it to him.
    def perform_update(self, serializer):
        serializer.save(user_id=self.request.user)


class AllOrdersOfUser(generics.ListAPIView):
    serializer_class = AllOrdersOfUser
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Orders.objects.filter(user_id=self.request.user)


class CustomAPIToken(TokenObtainPairView):
    serializer_class = CustomTokenSerializer


@api_view(["POST"])
def check_user_email(request):
    email = request.data["email"]
    user = Users.objects.filter(email=email)

    if user.exists():
        return Response({"User with this email already exists!"})
    return Response({"Email is good to go"})


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data["email"]

        try:
            user = Users.objects.get(email=email)
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            reset = PasswordReset(user=email, reset_code=token)
            reset.save()

            reset_url = f"{os.environ.get('SITE_DOMAIN')}/{token}"

            send_mail(
                subject="Password Reset Request",
                message=f"here is your password reset link: {reset_url}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response({"Email sent"})
        except:
            return Response({"error": "User not found"}, status=400)


class ActuallyResetPassword(generics.CreateAPIView):
    serializer_class = ActuallyResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset done!"})


class FavouriteItems(generics.CreateAPIView):
    serializer_class = FavouriteItemsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)
