from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.core.api.v1.accounts.views import RegisterAPIView, CustomTokenObtainPairView, CustomTokenRefreshView, \
    PasswordResetRequestAPIView, PasswordResetConfirmAPIView
from apps.core.api.v1.users.views import UserAPIView

router = DefaultRouter()

router.register('user', UserAPIView, basename='user')

urlpatterns = [
    path('accounts/register/', RegisterAPIView.as_view(), name='register'),
    path('accounts/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('accounts/refresh-token/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/password-reset/', PasswordResetRequestAPIView.as_view(), name='password_reset_request'),
    path('accounts/password-reset/<uidb64>/<token>/', PasswordResetConfirmAPIView.as_view(), name='password_reset_confirm'),
]
urlpatterns += router.urls
