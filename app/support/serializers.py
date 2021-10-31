from datetime import datetime, timedelta

import jwt
from django.conf import settings
from rest_framework import serializers

from .models import Ticket, User


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    """Serializing the Logging User"""
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)

    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    def validate(self, data):
        validated_data = super().validate(data)

        email = validated_data['email']
        password = validated_data['password']

        error_msg = 'email or password are incorrect'

        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                raise serializers.ValidationError(error_msg)
            validated_data['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError(error_msg)

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )
        return validated_data

    def create(self, validated_data):

        access_payload = {
            'iss': 'support-api',
            'user_id': validated_data['user'].id,
            'exp': datetime.utcnow() + timedelta(seconds=int(settings.JWT_ACCESS_TTL)),
            'type': 'access'
        }
        access_token = jwt.encode(
            payload=access_payload, key=settings.JWT_SECRET, algorithm='HS256')

        refresh_payload = {
            'iss': 'support-api',
            'user_id': validated_data['user'].id,
            'exp': datetime.utcnow() + timedelta(seconds=int(settings.JWT_REFRESH_TTL)),
            'type': 'refresh'
        }
        refresh_token = jwt.encode(
            payload=refresh_payload, key=settings.JWT_SECRET, algorithm='HS256')

        return {
            'access': access_token,
            'refresh': refresh_token
        }


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
