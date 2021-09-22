from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password


# Custom Serializer


class Custom_userSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email',
                  'role', 'contact', 'password')


class CustomRegisterSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text='Leave empty if no change needed',
        style={'input_type': 'password', 'placeholder': 'Password'}
    )

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'role', 'contact', 'password')
        extra_kwargs = {'password': {'write_only': True}, }

    def create(self, validated_data):
        validated_data['password'] = make_password(
            validated_data.get('password'))
        # validated_data['role'] = validated_data.get('role').lower()

        return super(CustomRegisterSerializer, self).create(validated_data)


# Roll Serializer


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = ('id', 'role')


# Forget Password
class OtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Otp
        fields = ('email',)


class ResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField()
    newpassword = serializers.CharField(max_length=150)
