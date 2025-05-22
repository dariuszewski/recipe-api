# urls.py
from django.urls import path
from .views import activate_user

urlpatterns = [
    path("users/activate/<uid>/<token>/", activate_user, name="activate-user"),
]
