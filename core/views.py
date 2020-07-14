import json

from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.timezone import now
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView as BaseTokenObtainPairView

from .tasks import bot_process, send_verification_mail_task
from core.models import Post, User, Like
from core.serializers import PostSerializer, DateFramesSerializer, UserCreateSerializer
from .utils import account_activation_token


class RegisterView(CreateAPIView):
    serializer_class = UserCreateSerializer

    def perform_create(self, serializer):
        user = serializer.save(user=self.request.user)
        # send_verification_mail_task.delay(user_id=user.id)


class EmailActivationView(APIView):

    def get_user(self):
        try:
            uidb64 = self.kwargs.get("uidb64")
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        return user

    def get_token(self):
        return self.kwargs.get("token")

    def get(self, request, uidb64, token):
        user = self.get_user()
        token = self.get_token()

        if user and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            refresh = RefreshToken.for_user(user)
            tokens = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
            return Response(
                tokens,
                status=status.HTTP_200_OK
            )

        elif user:
            return Response(
                {"error": "Link is not valid anymore"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        else:
            return Response(
                {"error": "There is no such user in system"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )


class TokenObtainPairView(BaseTokenObtainPairView):
    def post(self, request, *args, **kwargs):
        result = super().post(request, *args, **kwargs)
        user = User.objects.get(username=request.data['username'])
        user.last_login = now()
        user.save()
        return result


class CreatePostView(CreateAPIView):
    model = Post
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ListPostView(ListAPIView):
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer


class LikesAnalyticsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = DateFramesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        likes_number = Like.objects.filter(
            date_created__range=(serializer.data["date_from"], serializer.data["date_to"])
        ).count()

        return Response({"likes_number": likes_number}, status=status.HTTP_200_OK)


class UserActivityView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=request.data['user_id'])
            return Response(
                {"last_login": user.last_login, "last_request": user.last_request},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": "user does not exists"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )


class BotFileUploadView(APIView):
    # permission_classes = (IsAuthenticated,)
    parser_classes = (FileUploadParser,)

    def put(self, request, filename):
        file_obj = request.data['file']
        text_data = file_obj.read()
        data = json.loads(text_data)
        bot_process.delay(1, data)

        print(User.objects.all())

        return Response(status=200)


class ChatView(TemplateView):
    template_name = 'core/chat.html'



