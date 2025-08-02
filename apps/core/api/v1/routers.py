from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.core.api.v1.users.views import UserAPIView

router = DefaultRouter()

router.register('user', UserAPIView, basename='user')

urlpatterns = [
    path('accounts/', include('apps.core.api.v1.accounts.urls')),
]
urlpatterns += router.urls
