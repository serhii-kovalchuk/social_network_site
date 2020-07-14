from django.utils.timezone import now
from rest_framework_simplejwt.authentication import JWTAuthentication as BaseJWTAuthentication


class JWTAuthentication(BaseJWTAuthentication):

    def authenticate(self, request):
        auth_credentials = super().authenticate(request)

        if not auth_credentials:
            return auth_credentials

        user, validated_token = auth_credentials
        user.last_request = now()
        user.save()

        return user, validated_token



