from rest_framework import generics

from .models import Recipe
from .serializers import RecipeSerializer


class RecipeList(generics.ListCreateAPIView):
    """
    API view to retrieve list of recipes or create a new recipe.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class RecipeDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update or delete a recipe.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    lookup_field = "pk"
