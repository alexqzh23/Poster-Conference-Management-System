from django.db import models
from random import choice
from cms.models import Attendee


# Create your models here.
class LuckyDrawer(models.Model):
    winner = models.OneToOneField(Attendee, primary_key=True, on_delete=models.CASCADE)
    prize_level = models.IntegerField()

    @classmethod
    def create(cls, prize_level):
        cls.prize_level = prize_level
        return cls

    def generate_first_winner(self, email_list):
        if len(email_list) == 0:
            return None
        self.email = choice(email_list)
        return self.email

    def generate_second_winner(self, email_list):
        if len(email_list) == 0:
            return None
        self.email = choice(email_list)
        return self.email

    def generate_third_winner(self, email_list):
        if len(email_list) == 0:
            return None
        self.email = choice(email_list)
        return self.email

    class Meta:
        db_table = 'LuckyDrawer'
