from django.contrib.auth.models import AbstractUser

#from cms.system_function import short_uuid
from django.db import models

from cms.system_function import short_uuid

"""
basic models
- User(AbstractUser)
- Attendee(models.Model)
- Admin(models.Model)
"""


class User(AbstractUser):
    """
    Superclass for all users in the system
    inherits and overrides from django AbstractUser type
    """

    # The Type of User
    class Role(models.TextChoices):
        Chairman = 'Chairman',
        Admin = 'Admin',
        Head_Judge = 'Head Judge',
        Programme_Judge = 'Programme Judge',
        Programme_Coordinator = 'Programme Coordinator'
        Attendee = 'Attendee'

    user_id = models.CharField(max_length=8, primary_key=True)
    user_type = models.CharField(choices=Role.choices, max_length=64)

    # set unused inherited attributes to None
    username = None
    password = None
    first_name = None
    last_name = None
    email = None
    is_staff = None
    date_joined = None
    is_superuser = None
    is_active = None
    last_login = None

    # primary key: user_id
    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['user_type']

    @classmethod
    def create(cls):
        # auto generate user_id
        cls.user_id = short_uuid()
        return cls

    class Meta:
        db_table = 'User'

    def get_user_id(self):
        return self.user_id

    def get_user(self, user_id):
        try:
            return User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return None


class Attendee(models.Model):
    """
    Attendee
    """
    email = models.CharField(max_length=128, primary_key=True)
    vote_status = models.BooleanField(default=False)  # {0: un_voted, 1: voted}
    user_id = models.OneToOneField(User, to_field='user_id', on_delete=models.CASCADE, related_name='attendee')

    def set_vote_status(self):
        self.vote_status = True

    def get_vote_status(self):
        return self.vote_status

    def get_email(self):
        return self.email

    class Meta:
        db_table = 'Attendee'
        verbose_name = 'Attendees'
        verbose_name_plural = verbose_name


class Admin(models.Model):
    """
    Admin of system
    """
    user_id = models.OneToOneField(User, to_field='user_id', on_delete=models.CASCADE, primary_key=True)
    password = models.CharField(max_length=10)

    def get_pwd(self):
        return self.password

    class Meta:
        db_table = 'Admin'
        verbose_name = 'Admins'
        verbose_name_plural = verbose_name
