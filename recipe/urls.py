from django.urls import path

from .views import RecipeList, RecipeDetail, MyRecipeListView


urlpatterns = [
    path("mine/", MyRecipeListView.as_view(), name="recipe-my-list"),
    path("<int:pk>/", RecipeDetail.as_view(), name="post_detail"),
    path("", RecipeList.as_view(), name="post_list"),
]
