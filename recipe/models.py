from django.conf import settings
from django.db import models


class Recipe(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    num_of_servings = models.IntegerField()
    cook_time = models.IntegerField()  # in minutes
    directions = models.TextField()
    is_publish = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipes"
    )

    def __str__(self):
        return self.name
