from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import RegisterView, CustomTokenObtainView, LogoutView, UserViewSet

router = DefaultRouter()
router.register(r'api/users', UserViewSet, basename='users')

urlpatterns = [
    *router.urls,
    path('api/registration/', RegisterView.as_view(), name='register'),
    path('api/login/', CustomTokenObtainView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
]
