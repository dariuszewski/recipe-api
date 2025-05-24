from django.conf import settings
from django.db import models
from django.forms import ValidationError
from django.core.validators import MinValueValidator


class Recipe(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    num_of_servings = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    cook_time = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    directions = models.TextField()
    is_publish = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to="recipes/", blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipes"
    )

    def __str__(self):
        return self.name
