from django.test import TestCase

from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Recipe


class RecipeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@email.com",
            password="secret",
        )
        cls.recipe = Recipe.objects.create(
            author=cls.user,
            name="A good title",
            description="Nice body content",
            num_of_servings=2,
            cook_time=30,
            directions="Step 1: Do something. Step 2: Do something else.",
            is_publish=True,
        )

    def test_recipe_model(self):
        self.assertEqual(self.recipe.author.username, "testuser")
        self.assertEqual(self.recipe.name, "A good title")
        self.assertEqual(self.recipe.description, "Nice body content")
        self.assertEqual(str(self.recipe), "A good title")
