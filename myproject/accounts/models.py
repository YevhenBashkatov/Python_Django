from django.db import models


# Create your models here.


class Avatar(models.Model):
    file = models.ImageField(upload_to='avatars/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'avatar'
        verbose_name_plural = 'avatars'
