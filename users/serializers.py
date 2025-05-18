# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import Group
from .models import User

class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Group.objects.all(),
        required=False
    )

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'read_only': True},  
        }

    def create(self, validated_data):
        groups = validated_data.pop('groups', None)
        password = validated_data.pop('password', None)

        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
        if groups is not None:
            user.groups.set(groups)
        user.save()  

        return user

    def update(self, instance, validated_data):
        groups = validated_data.pop('groups', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        if groups is not None:
            instance.groups.set(groups)

        instance.save() 

        return instance
