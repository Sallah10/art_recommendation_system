from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Create your models here.
class Art_Work(models.Model):
	artiste = models.CharField(max_length=60, null=True, blank=False)
	art_title = models.CharField(max_length=60, blank=False)
	art_image = models.ImageField(blank=True, upload_to="art_images/")
	art_desc = models.TextField(blank=True)

	def __str__(self):
		return f'{self.artiste} {self.art_title}'



class UserInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artwork = models.ForeignKey(Art_Work, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)
    bookmarked = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    last_interacted = models.DateTimeField(auto_now=True)
