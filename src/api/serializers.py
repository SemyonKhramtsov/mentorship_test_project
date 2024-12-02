from rest_framework.exceptions import ValidationError
from rest_framework.fields import ListField
from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework import fields

from .models import User


class UserCreateSerializer(Serializer):
    username = fields.CharField(required=True, max_length=32)
    password = fields.CharField(required=True, max_length=128)
    email = fields.CharField(required=False, max_length=32)
    phone_number = fields.CharField(required=False, max_length=32)

    def create(self, attrs: dict) -> User:
        new_instance = User.objects.create(**attrs)
        return new_instance


class UserListSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "mentor",
            "mentees",
        ]


class UserDetailSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "email",
            "phone_number",
            "mentor",
            "mentees",
        ]

    mentor = fields.CharField(source="mentor.username")

    def to_representation(self, instance: User) -> dict:
        ret = super().to_representation(instance)
        ret["mentees"] = [mentee.username for mentee in instance.mentees.all()]
        return ret


class UserUpdateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "email",
            "phone_number",
            "mentor",
            "mentees",
        ]

    username = fields.CharField(allow_null=True, max_length=255, required=False)
    password = fields.CharField(allow_null=True, max_length=128, required=False)
    email = fields.EmailField(allow_null=True, max_length=255, required=False)
    phone_number = fields.CharField(allow_null=True, max_length=16, required=False)
    mentor = fields.CharField(source="mentor.username", allow_null=True, required=False)
    mentees = ListField(child=fields.CharField(), required=False)

    def validate(self, attrs: dict) -> dict:
        errors = {}

        username = attrs.get("username")
        if username and User.objects.get_or_none(username=username):
            errors.update({"username": f"Уже есть пользователь с таким username - {username}"})

        mentor = attrs.get("mentor", {}).get("username")
        if mentor and not User.objects.get_or_none(username=mentor):
            errors.update({"mentor": f"Не существует пользователя с таким username - {mentor}"})

        mentees = attrs.get("mentees")
        if mentees and isinstance(mentees, list):
            mentee_errors = []
            for mentee in mentees:
                if not User.objects.get_or_none(username=mentee):
                    mentee_errors.append({"mentee": f"Не существует пользователя с таким username - {mentee}"})
            if mentee_errors:
                errors.update({"mentee": mentee_errors})

        if errors:
            raise ValidationError(detail=errors)

        return attrs

    def update(self, instance: User, validated_data: dict) -> User:
        mentor_username = validated_data.pop("mentor", {}).get("username")
        if mentor_username:
            instance.mentor = User.objects.get(username=mentor_username)

        mentees_data = validated_data.pop("mentees", None)
        if mentees_data:
            mentees_users = User.objects.filter(username__in=mentees_data)
            instance.mentees.set(mentees_users)

        return super().update(instance, validated_data)
