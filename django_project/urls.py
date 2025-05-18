from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenBlacklistView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("recipes/", include("recipe.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    re_path(r"^auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.jwt")),
    path("auth/jwt/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
