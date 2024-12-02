from datetime import datetime, timedelta

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.core.validators import RegexValidator
from django.db import models

from config import settings


class UserManager(BaseUserManager):
    def create_user(self, username: str, email: str, password: str):
        if username is None:
            raise TypeError('Users must have a username.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class User(AbstractBaseUser):
    username = models.CharField(db_index=True, max_length=255, unique=True)
    email = models.EmailField(null=True)
    mentor = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='mentees')
    phone_number = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Номер должен быть введен в формате: '+999999999'. Допускается до 15 цифр."
            ),
        ],
    )
    USERNAME_FIELD = 'username'
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    def __str__(self):
        return self.username

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')
