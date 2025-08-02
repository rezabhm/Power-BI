from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer


from .serializers import RegisterSerializer, PasswordResetRequestSerializer, PasswordResetSerializer


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        operation_summary="Register a new user",
        operation_description="Creates a new user account.",
        responses={201: RegisterSerializer()}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PasswordResetRequestAPIView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetRequestSerializer

    @swagger_auto_schema(
        operation_summary="Request a password reset",
        operation_description="Sends an email with a password reset link to the user's email address.",
        responses={200: "Password reset link sent."}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            # This will be replaced with a proper URL once the URL is configured
            reset_link = request.build_absolute_uri(f'/api/v1/core/accounts/password-reset/{uid}/{token}/')

            # In a real app, you would use django's email backend to send this.
            # I will just print to console for now.
            print(f"Password reset link for {email}: {reset_link}")

        return Response({"detail": "If an account with this email exists, a password reset link has been sent."},
                        status=status.HTTP_200_OK)


class PasswordResetConfirmAPIView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetSerializer

    @swagger_auto_schema(
        operation_summary="Confirm a password reset",
        operation_description="Sets a new password for the user.",
        responses={200: "Password has been reset."}
    )
    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "The reset link is invalid."}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(
        operation_summary="Login a user",
        operation_description="Takes a set of user credentials and returns an access and refresh JSON web token pair to prove the authentication of those credentials.",
        responses={200: TokenObtainPairSerializer()}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        operation_summary="Refresh an access token",
        operation_description="Takes a refresh JSON web token and returns an access JSON web token if the refresh token is valid.",
        responses={200: TokenRefreshSerializer()}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
