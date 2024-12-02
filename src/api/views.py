from django.core.exceptions import ObjectDoesNotExist
from requests import Request
from rest_framework import generics, permissions
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    UserCreateSerializer,
    UserListSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer: UserCreateSerializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user: User = serializer.save()

            refresh = RefreshToken.for_user(user)

            refresh.payload.update({
                "user_id": user.id,
                "username": user.username,
            })

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)


class CustomTokenObtainView(APIView):
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs) -> Response:
        username = request.data["username"]
        password = request.data["password"]

        try:
            user = User.objects.get(username=username, password=password)
            refresh = RefreshToken.for_user(user)

            refresh.payload.update({
                "user_id": user.id,
                "username": user.username,
            })

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist:
            return Response({"msg": "The credentials provided are invalid."}, status=status.HTTP_401_UNAUTHORIZED)


class UserViewSet(ListModelMixin,
                  RetrieveModelMixin,
                  UpdateModelMixin,
                  GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    SERIALIZERS_BY_ACTION = {
        "list": UserListSerializer,
        "retrieve": UserDetailSerializer,
        "partial_update": UserUpdateSerializer,
    }

    def get_serializer_class(self) -> ModelSerializer:
        if self.action not in self.SERIALIZERS_BY_ACTION.keys():
            raise MethodNotAllowed(method=self.action)
        return self.SERIALIZERS_BY_ACTION[self.action]

    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        user = request.user
        target_user: User = self.get_object()
        if user != target_user:
            return Response({"detail": "У вас нет прав для редактирования этого пользователя."},
                            status=status.HTTP_403_FORBIDDEN)

        initial_data = request.data
        serializer: UserUpdateSerializer = self.get_serializer(target_user, data=initial_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserDetailSerializer(instance=target_user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request: Request) -> Response:
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"error": "Необходим Refresh token"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response({"error": "Неверный Refresh token"},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({"success": "Выход успешен"}, status=status.HTTP_200_OK)
