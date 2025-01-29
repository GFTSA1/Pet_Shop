from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainSerializer,
    TokenObtainPairSerializer,
)

from Pet_Shop.pets.models import (
    Items,
    Users,
    Category,
    Orders,
    FavouriteItems,
    ItemsOrders,
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

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = Users.objects.create(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    class Meta:
        model = Users
        fields = ["id", "email", "created_at", "password"]


class FavouriteItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavouriteItems
        fields = "__all__"


class OrdersItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemsOrders
        fields = ["item_id", "quantity"]


class OrdersSerializer(serializers.ModelSerializer):
    items = OrdersItemSerializer(many=True, write_only=True)
    user_id = serializers.ReadOnlyField(source="user.id")
    delete_flag = serializers.ReadOnlyField(required=False)

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
                delete_flag = item_data.get("delete_flag")

                if item_id in existing_items:
                    if delete_flag:
                        existing_items[item_id].delete()
                    else:
                        existing_item = existing_items[item_id]
                        existing_item.quantity = item_data.get(
                            "quantity", existing_item.quantity
                        )
                        existing_item.save()
                else:
                    if not delete_flag:
                        ItemsOrders.objects.create(order_id=instance, **item_data)
            return instance

        except KeyError:
            instance.status = validated_data.get("status", instance.status)
            instance.save()
            return instance

    class Meta:
        model = Orders
        fields = "__all__"
