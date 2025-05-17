from rest_framework import generics, permissions
from django.db.models import Q

from .models import Recipe
from .serializers import RecipeSerializer
from .permissions import IsAuthorOrReadOnly


class RecipeList(generics.ListCreateAPIView):
    """
    API view to retrieve list of recipes or create a new recipe.
    """

    queryset = Recipe.objects.filter(is_publish=True).order_by(
        "-updated_at", "-created_at"
    )
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RecipeDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update or delete a recipe.
    """

    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Recipe.objects.filter(Q(is_publish=True) | Q(author=user))
        return Recipe.objects.filter(is_publish=True)

    def perform_destroy(self, instance):
        instance.is_publish = False
        instance.save()


class MyRecipeListView(generics.ListAPIView):
    """
    API view to retrieve a list of recipes created by the authenticated user.
    """

    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Recipe.objects.filter(author=self.request.user).order_by("-updated_at")
