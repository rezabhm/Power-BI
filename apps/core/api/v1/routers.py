from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.core.api.v1.users.views import UserAPIView

router = DefaultRouter()

router.register('user', UserAPIView, basename='user')

urlpatterns = [
    path('accounts/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('accounts/refresh-token/', TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += router.urls
