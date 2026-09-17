from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Type_User(models.Model):
	name = models.CharField(max_length=50, blank=False)

	def __str__(self):
		return str(self.name)


class Profile(models.Model):
	user=models.OneToOneField(User, null=True, on_delete=models.SET_NULL)
	user_type = models.OneToOneField(Type_User, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return f'{self.user.username}'

def create_profile(sender, instance, created, **kwargs):
	if created:
		profile = Profile(user=instance)
		profile.save()

post_save.connect(create_profile, sender=User)
