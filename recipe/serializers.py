from rest_framework import serializers
from .models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    image = serializers.ImageField(required=False)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "description",
            "directions",
            "cook_time",
            "num_of_servings",
            "is_publish",
            "created_at",
            "updated_at",
            "image",
            "author",
        ]
        read_only_fields = ["id", "created_at", "author"]
