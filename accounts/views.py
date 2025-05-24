# accounts/views.py
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from djoser.utils import decode_uid
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view

User = get_user_model()


@extend_schema(
    responses={200: None, 400: None},
    description="Activate user account via UID and token.",
)
@api_view(["GET"])
def activate_user(request, uid, token):
    try:
        uid_decoded = decode_uid(uid)
        user = User.objects.get(pk=uid_decoded)
    except (User.DoesNotExist, ValueError, TypeError):
        return Response({"detail": "Invalid UID."}, status=status.HTTP_400_BAD_REQUEST)

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return Response(
            {"detail": "Account activated successfully."}, status=status.HTTP_200_OK
        )

    return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
