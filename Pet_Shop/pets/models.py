from django.contrib.auth.models import AbstractUser
from .manager import CustomUserManager
from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title


class Items(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    image = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    category_id = models.ForeignKey("Category", on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["title"])]


class Users(AbstractUser):
    email = models.EmailField(unique=True)
    username = None
    logo = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.first_name

    class Meta:
        indexes = [models.Index(fields=["email"])]


class Orders(models.Model):
    choices_for_order = {
        "Pending": "Pending",
        "Awaiting": "Awaiting",
        "Shipped": "Shipped",
        "Completed": "Completed",
        "Canceled": "Canceled",
    }
    status = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey("pets.Users", on_delete=models.DO_NOTHING)
    post_city = models.CharField(max_length=255, default="N/A")
    post_departament = models.CharField(max_length=255, default="N/A")
    user_number = models.IntegerField(default=0)


class FavouriteItems(models.Model):
    Like = (
        0,
        1,
    )

    user_id = models.ForeignKey("pets.Users", on_delete=models.CASCADE)
    item_id = models.ForeignKey("pets.Items", on_delete=models.CASCADE)
    direction_of_like = models.IntegerField(default=0)

    class Meta:
        unique_together = ("user_id", "item_id")


class ItemsOrders(models.Model):
    item_id = models.ForeignKey("pets.Items", on_delete=models.CASCADE)
    order_id = models.ForeignKey("pets.Orders", on_delete=models.CASCADE)
    quantity = models.IntegerField()


class PasswordReset(models.Model):
    user = models.EmailField()
    reset_code = models.CharField(max_length=255, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
