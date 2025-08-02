from django.urls import path
from .views import (
    RegisterAPIView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    PasswordResetRequestAPIView,
    PasswordResetConfirmAPIView,
)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh-token/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/', PasswordResetRequestAPIView.as_view(), name='password_reset_request'),
    path('password-reset/<uidb64>/<token>/', PasswordResetConfirmAPIView.as_view(), name='password_reset_confirm'),
]
