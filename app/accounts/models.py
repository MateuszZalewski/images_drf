from django.db import models
from django.contrib.auth.models import User


class Perk(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f'{self.name}'


class Tier(models.Model):
    name = models.CharField(max_length=100)
    perks = models.ManyToManyField(Perk)

    def __str__(self):
        return f'{self.name}'


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tier = models.ForeignKey(Tier, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.user.username} account'
