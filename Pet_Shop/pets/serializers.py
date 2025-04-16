import re

from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)

from Pet_Shop.pets.models import (
    Items,
    Users,
    Category,
    Orders,
    FavouriteItems,
    ItemsOrders,
    PasswordReset,
)

email_pattern = (
    r"^(?!.*\.\.)[a-zA-Z0-9._-]{1,63}[a-zA-Z0-9]@[a-zA-Z0-9.-]{1,255}\.[a-zA-Z]{2,63}$"
)
password_pattern = (
    r"^(?=.*[A-Z])(?=.*[a-z])[A-Za-z\d!@#$%^&*]{8,100}$"
)


class ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Items
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class UsersSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False)

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")
        if email:
            if not re.fullmatch(email_pattern, email):
                raise serializers.ValidationError({"email_error": "Invalid email"})
        if password:
            if password != password_confirm:
                raise serializers.ValidationError(
                    {"password_error": "Passwords do not match"}
                )
            if not re.fullmatch(password_pattern, password):
                raise serializers.ValidationError(
                    {
                        "password_error": "Password must be at least 8 characters long, have one special character, one upper case letter, one number, and one lower case letter"
                    }
                )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = Users.objects.create(**validated_data)
        if validated_data.get("first_name") is None:
            user.first_name = user.email.split("@")[0]
        user.set_password(validated_data.get("password"))
        user.save()
        return user

    class Meta:
        model = Users
        fields = [
            "id",
            "email",
            "created_at",
            "password",
            "password_confirm",
            "first_name",
        ]


class OrdersItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemsOrders
        fields = ["item_id", "quantity"]


class OrdersSerializer(serializers.ModelSerializer):
    items = OrdersItemSerializer(many=True, write_only=True)
    user_id = serializers.ReadOnlyField(source="user.id")
    status = serializers.ChoiceField(
        choices=Orders.choices_for_order, default="Pending"
    )

    def validate(self, attrs):
        post_departament = attrs["post_departament"]
        post_city = attrs["post_city"]
        user_number = attrs["user_number"]

        if user_number == 0 or user_number is None:
            raise serializers.ValidationError(
                {"user_number_error": "Invalid user_number"}
            )
        if post_city is None or post_city.strip() == "" or post_city == "N/A":
            raise serializers.ValidationError({"post_city_error": "Invalid post_city"})
        if (
            post_departament is None
            or post_departament.strip() == ""
            or post_departament == "N/A"
        ):
            raise serializers.ValidationError(
                {"post_departament_error": "Invalid post_departament"}
            )
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Orders.objects.create(**validated_data)
        for item_data in items_data:
            ItemsOrders.objects.create(order_id=order, **item_data)
        return order

    def update(self, instance, validated_data):
        try:
            items_data = validated_data.pop("items")
            instance.status = validated_data.get("status", instance.status)
            instance.save()

            existing_items = {
                item.item_id: item
                for item in ItemsOrders.objects.filter(order_id_id=instance.id).all()
            }

            for item_data in items_data:
                item_id = item_data.get("item_id")

                if item_id in existing_items:
                    if item_data.get("quantity") == 0:
                        existing_items[item_id].delete()
                    else:
                        existing_item = existing_items[item_id]
                        existing_item.quantity = item_data.get(
                            "quantity", existing_item.quantity
                        )
                        existing_item.save()
                else:
                    if not (item_data.get("quantity") == 0):
                        ItemsOrders.objects.create(order_id=instance, **item_data)
            return instance

        except KeyError:
            instance.status = validated_data.get("status", instance.status)
            instance.save()
            return instance

    class Meta:
        model = Orders
        fields = "__all__"


class ItemForUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Items
        fields = ["id", "title"]


class HelperUserOrderSerializer(serializers.ModelSerializer):
    item = ItemForUserSerializer(read_only=True, source="item_id")

    class Meta:
        model = ItemsOrders
        fields = ["item", "quantity"]


class AllOrdersOfUser(serializers.ModelSerializer):
    item_id = HelperUserOrderSerializer(
        many=True, read_only=True, source="itemsorders_set"
    )

    class Meta:
        model = Orders
        fields = ["id", "status", "created_at", "item_id"]


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    class Meta:
        fields = ["email"]


class ActuallyResetPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.RegexField(
        regex=r"^(?=.*[A-Z])(?=.*[a-z])[A-Za-z\d!@#$%^&*]{8,100}$",
        write_only=True,
        error_messages={
            "invalid": (
                "Password must be at least 8 characters long with at least one capital letter and symbol"
            )
        },
    )
    confirm_password = serializers.CharField(write_only=True, required=True)
    token = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return attrs

    def create(self, validated_data):
        try:
            found_token_obj = PasswordReset.objects.filter(
                reset_code=validated_data["token"]
            ).first()
            user = Users.objects.get(email=found_token_obj.user)
            if user:
                user.set_password(validated_data["new_password"])
                user.save()

                found_token_obj.delete()
            else:
                raise serializers.ValidationError({"error": "No User found"})
        except PasswordReset.DoesNotExist:
            raise serializers.ValidationError(
                {"error": "Password reset token is invalid"}
            )
        return {"message": "Password reset done!"}

    class Meta:
        model = PasswordReset
        fields = ["new_password", "confirm_password", "token"]


class FavouriteItemsSerializer(serializers.ModelSerializer):
    user = UsersSerializer(read_only=True)
    item = ItemForUserSerializer(read_only=True, source="item_id")
    direction_of_like = serializers.ChoiceField(choices=FavouriteItems.Like, default=1)

    def create(self, validated_data):
        user_has_liked_item = FavouriteItems.objects.filter(
            user_id=validated_data["user_id"]
        ).filter(item_id=validated_data["item_id"])
        if user_has_liked_item:
            raise serializers.ValidationError(
                {"error": "You have already liked this item"}
            )
        item = FavouriteItems.objects.create(**validated_data)
        return item

    class Meta:
        model = FavouriteItems
        fields = ["user", "item", "direction_of_like"]


class CustomTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data["first_name"] = self.user.first_name
        return data
