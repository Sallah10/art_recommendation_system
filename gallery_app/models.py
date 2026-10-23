from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class Collection(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    description = models.TextField(blank=True)
    accent = models.CharField(max_length=20, default="#C4532D")
    featured = models.BooleanField(default=False)
    artworks = models.ManyToManyField("Art_Work", related_name="collections", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Art_Work(models.Model):
    art_title = models.CharField(max_length=120)
    artiste = models.CharField(max_length=120, blank=True, default="Unattributed")
    art_desc = models.TextField(blank=True)
    art_image = models.ImageField(upload_to="artworks/", blank=True)
    style = models.CharField(max_length=60, blank=True)
    era = models.CharField(max_length=60, blank=True)
    medium = models.CharField(max_length=60, blank=True)
    year = models.CharField(max_length=30, blank=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("art_title",)
        indexes = [
            models.Index(fields=["style"]),
            models.Index(fields=["era"]),
            models.Index(fields=["featured"]),
        ]

    def __str__(self):
        return f"{self.art_title} - {self.artiste}"

    @property
    def tags(self):
        return [tag for tag in (self.style, self.era, self.medium) if tag]


class UserInteraction(models.Model):
    # `session_key` lets anonymous visitors get personalised recommendations
    # without creating an account. Logged-in users are linked through `user`.
    session_key = models.CharField(max_length=64, db_index=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    artwork = models.ForeignKey(Art_Work, related_name="interactions", on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)
    bookmarked = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    last_interacted = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("session_key", "artwork")
        indexes = [
            models.Index(fields=["session_key", "artwork"]),
            models.Index(fields=["artwork", "liked"]),
        ]

    def __str__(self):
        return f"{self.session_key} -> {self.artwork_id}"
