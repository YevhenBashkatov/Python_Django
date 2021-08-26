import math

from django.db import models

from django.utils.safestring import mark_safe

from django.utils.text import Truncator
from django.contrib.auth.models import AbstractUser
from markdown import markdown

# Create your models here.
from simple_history.models import HistoricalRecords


class User(AbstractUser):
    is_blogger = models.BooleanField(default=False)
    is_reader = models.BooleanField(default=False)

    def __get__(self, instance, owner):
        return self.username


class Categories(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Interests(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Reader(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    interests = models.ManyToManyField(Interests, related_name='interested_reader')
    is_adult = models.BooleanField(default=False)


class Blogger(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    birthday = models.DateField(null=True, blank=True)
    country = models.CharField(null=True, max_length=30)
    city = models.CharField(null=True, max_length=30)
    categories = models.ManyToManyField(Categories, related_name='categories_reader')


class Board(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)
    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return self.name

    def get_post_count(self):
        return Post.objects.filter(topic__board=self).count()

    def get_last_post(self):
        return Post.objects.filter(topic__board=self).order_by('-created_at').first()


class Topic(models.Model):
    subject = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(Board, related_name='topics', on_delete=models.CASCADE)
    starter = models.ForeignKey(User, related_name='topics', on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.subject

    def get_page_count(self):
        count = self.posts.count()
        pages = count / 20
        return math.ceil(pages)


class Post(models.Model):
    message = models.TextField(max_length=4000)
    topic = models.ForeignKey(Topic, related_name='posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, null=True, related_name='+', on_delete=models.CASCADE)

    def __str__(self):
        truncated_message = Truncator(self.message)
        return truncated_message.chars(30)

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))


class Photo(models.Model):
    topic = models.ForeignKey(Topic, related_name='photos', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255, blank=True)
    file = models.ImageField(upload_to='photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
