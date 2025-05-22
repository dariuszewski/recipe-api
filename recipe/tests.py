from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.test.utils import override_settings
from rest_framework.test import APIClient

from .models import Recipe


@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_PERMISSION_CLASSES": [
            "rest_framework.permissions.AllowAny",
        ],
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework_simplejwt.authentication.JWTAuthentication"
        ],
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
        "DEFAULT_THROTTLE_CLASSES": [],
        "DEFAULT_THROTTLE_RATES": {},
    },
)
class RecipeTests(TestCase):
    def setUp(self):
        # set up users
        cache.clear()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@email.com",
            password="secret",
            is_active=True,
        )

        self.other_user = get_user_model().objects.create_user(
            username="otheruser",
            email="other@email.com",
            password="secret",
        )

        # set up clients
        self.unauthenticated_client = APIClient()
        self.authenticated_client = APIClient()

        response = self.unauthenticated_client.post(
            "/auth/jwt/create/",
            {"username": "testuser", "password": "secret"},
        )
        self.authenticated_client.credentials(
            HTTP_AUTHORIZATION=f"JWT {response.data["access"]}"
        )

        # set up recipes
        # Published recipe by testuser
        self.recipe1 = Recipe.objects.create(
            author=self.user,
            name="Published Recipe",
            description="Nice body content",
            num_of_servings=2,
            cook_time=30,
            directions="Step 1: Do something. Step 2: Do something else.",
            is_publish=True,
        )

        # Unpublished recipe by testuser
        self.recipe2 = Recipe.objects.create(
            author=self.user,
            name="Unpublished Recipe by User",
            description="Private content",
            num_of_servings=1,
            cook_time=10,
            directions="Secret steps",
            is_publish=False,
        )

        # Published recipe by testuser
        self.recipe3 = Recipe.objects.create(
            author=self.other_user,
            name="Another Published",
            description="More content",
            num_of_servings=3,
            cook_time=25,
            directions="More steps",
            is_publish=True,
        )

        # Unpublished recipe by other_user
        self.recipe4 = Recipe.objects.create(
            author=self.other_user,
            name="Hidden by Other",
            description="Other user's private content",
            num_of_servings=4,
            cook_time=15,
            directions="Steps by other",
            is_publish=False,
        )

    def test_recipe_model(self):
        self.assertEqual(self.recipe1.author.username, "testuser")
        self.assertEqual(self.recipe1.name, "Published Recipe")
        self.assertEqual(self.recipe1.description, "Nice body content")
        self.assertEqual(str(self.recipe1), "Published Recipe")

    def test_recipe_list_view(self):
        # Test that the list view returns only published recipes
        response = self.unauthenticated_client.get("/recipes/")
        num_recipes = len(response.data)
        published_statuses = [recipe["is_publish"] for recipe in response.data]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(num_recipes, 2)
        self.assertTrue(all(published_statuses))

    def test_my_recipes_view(self):
        # Test that the authenticated user can see their own recipes
        response = self.authenticated_client.get("/recipes/mine/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_recipe_create_view_by_authenticated_client(self):
        # Test that an authenticated user can create a recipe
        data = {
            "name": "New Recipe",
            "description": "New content",
            "directions": "New steps",
            "cook_time": 30,
            "num_of_servings": 2,
            "is_publish": True,
        }
        response = self.authenticated_client.post("/recipes/", data=data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Recipe.objects.count(), 5)
        self.assertEqual(Recipe.objects.get(id=response.data["id"]).name, "New Recipe")

    def test_recipe_create_view_by_unauthenticated_client(self):
        # Test that an unauthenticated user cannot create a recipe
        data = {
            "name": "New Recipe",
            "description": "New content",
            "directions": "New steps",
            "cook_time": 30,
            "num_of_servings": 2,
            "is_publish": True,
        }
        response = self.unauthenticated_client.post(
            "/recipes/", data=data, format="json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertAlmostEqual(
            response.json()["detail"], "Authentication credentials were not provided."
        )
        self.assertEqual(Recipe.objects.count(), 4)

    def test_recipe_detail_view_authenticated(self):
        response = self.authenticated_client.get(f"/recipes/{self.recipe1.id}/")
        self.assertEqual(response.status_code, 200)

    def test_recipe_detail_view_unauthenticated(self):
        response = self.unauthenticated_client.get(f"/recipes/{self.recipe1.id}/")
        self.assertEqual(response.status_code, 200)

    def test_recipe_update_view_by_author(self):
        # Test that the author can update their own recipe
        data = {
            "name": "Updated Recipe",
            "description": "Updated content",
            "directions": "Updated steps",
            "cook_time": 35,
            "num_of_servings": 3,
            "is_publish": True,
        }
        response = self.authenticated_client.put(
            f"/recipes/{self.recipe1.pk}/", data=data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.recipe1.refresh_from_db()
        self.assertEqual(self.recipe1.name, "Updated Recipe")

    def test_recipe_update_view_by_other_user(self):
        # Test that another user cannot update the recipe
        data = {
            "name": "Updated Recipe",
            "description": "Updated content",
            "directions": "Updated steps",
            "cook_time": 35,
            "num_of_servings": 3,
            "is_publish": True,
        }
        response = self.authenticated_client.put(
            f"/recipes/{self.recipe4.pk}/", data=data, format="json"
        )
        self.assertEqual(response.status_code, 404)
        self.recipe4.refresh_from_db()
        self.assertEqual(self.recipe4.name, "Hidden by Other")

    def test_recipe_delete_view_by_author(self):
        # Test that the author can delete their own recipe
        response = self.authenticated_client.delete(f"/recipes/{self.recipe1.pk}/")
        recipe = Recipe.objects.filter(pk=self.recipe1.pk).first()
        self.assertEqual(response.status_code, 204)
        self.assertFalse(recipe.is_publish)

    def test_recipe_filters(self):
        # Test that the search filter works
        response = self.unauthenticated_client.get("/recipes/?search=Another Published")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        # Test that the max_cook_time filter works
        response = self.unauthenticated_client.get("/recipes/?max_cook_time=25")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_recipe_invalid_max_cook_time(self):
        # Test that an invalid max_cook_time raises a validation error
        response = self.unauthenticated_client.get("/recipes/?max_cook_time=invalid")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["max_cook_time"], "Must be a valid integer.")

    def test_recipe_valid_max_cook_time(self):
        # Test that a valid max_cook_time works
        response = self.unauthenticated_client.get("/recipes/?max_cook_time=25")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
