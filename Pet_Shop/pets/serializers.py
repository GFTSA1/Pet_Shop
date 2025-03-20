from rest_framework import serializers
from Pet_Shop.pets.models import (
    Items,
    Users,
    Category,
    Orders,
    FavouriteItems,
    ItemsOrders,
    PasswordReset,
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

    def create(self, validated_data):
        password = validated_data.pop("password")
        second_password = validated_data.pop("password_confirm")
        user = Users.objects.create(**validated_data)
        if validated_data.get("first_name") is None:
            user.first_name = user.email.split("@")[0]

        if password:
            if password != second_password:
                raise serializers.ValidationError("Passwords do not match")
            user.set_password(password)
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
        regex=r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
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
