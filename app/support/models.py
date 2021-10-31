from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.contrib.postgres.fields import ArrayField
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError('Users must have a username.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    opened_dialogs = ArrayField(models.IntegerField(), default=list)

    update_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username


class Ticket(models.Model):
    text = models.CharField(max_length=200)
    STATUS_TYPE = (
        (1, 'resolved'),
        (2, 'unresolved'),
        (3, 'frozen'),
    )
    status = models.IntegerField(choices=STATUS_TYPE, default=1)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_sender', default=None)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_recipient', default=None)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s %s" % (self.id, self.text)

