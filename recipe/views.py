from django.db.models import Q
from django.core.cache import cache
from rest_framework import generics, permissions, filters, response
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Recipe
from .serializers import RecipeSerializer
from .permissions import IsAuthorOrReadOnly
from .pagination import RecipeLimitOffsetPagination


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="search",
            description="Search term.",
            required=False,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="max_cook_time",
            description="Maximum cook time in minutes",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="ordering",
            location=OpenApiParameter.QUERY,
            required=False,
            description='Order by updated_at (use "updated_at" or "-updated_at")',
            type=str,
        ),
    ]
)
class RecipeList(generics.ListCreateAPIView):
    """
    API view to retrieve list of recipes or create a new recipe.
    """

    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["updated_at"]
    ordering = ["-updated_at"]
    pagination_class = RecipeLimitOffsetPagination

    def get_queryset(self):
        search = self.request.query_params.get("search", None)
        max_cook_time = self.request.query_params.get("max_cook_time", None)

        queryset = Recipe.objects.filter(is_publish=True)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(description__icontains=search)
            )

        if max_cook_time:
            if not max_cook_time.isdigit():
                raise ValidationError({"max_cook_time": "Must be a valid integer."})
            queryset = queryset.filter(cook_time__lte=max_cook_time)

        return queryset

    def list(self, request, *args, **kwargs):
        cache_key = "recipe_list"
        data = cache.get(cache_key)

        if data is None:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            cache.set(cache_key, data, timeout=300)

        return response.Response(data)

    def perform_create(self, serializer):
        instance = serializer.save(author=self.request.user)
        cache.delete("recipe_list")
        return instance


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

    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete("recipe_list")
        return instance

    def perform_destroy(self, instance):
        instance.is_publish = False
        cache.delete("recipe_list")
        instance.save()


class MyRecipeListView(generics.ListAPIView):
    """
    API view to retrieve a list of recipes created by the authenticated user.
    """

    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Recipe.objects.filter(author=self.request.user).order_by("-updated_at")
