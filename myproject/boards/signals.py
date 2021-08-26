from django.db.models.signals import post_save, post_init
from django.core.signals import request_finished

from django.dispatch import receiver
from django.http import HttpResponse

from .tasks import send_reply_email, send_signup_email
from .models import Post, Topic


@receiver(post_save, sender=Post)
def post_reply_email(sender, instance, **kwargs):
    print(instance.topic.starter.email)
    print(instance.topic.subject)
    send_reply_email.delay(email=instance.topic.starter.email, name=instance.topic.subject)
    #
    return print('Email send!')
