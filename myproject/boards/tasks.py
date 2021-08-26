from celery import Celery
from django.core.mail import send_mail

app = Celery('tasks', broker='redis://guest@localhost//')


@app.task
def add(x, y):
    return x + y


@app.task
def send_signup_email(email):
    send_mail(
        'Registration congratulations!',
        'Welcome to the club, buddy!',
        'djangotestcomp@gmail.com',
        [email],
        fail_silently=False,
    )


@app.task
def send_reply_email(email, name):
    send_mail(
        'Topic {} was replayed'.format(name),
        'Welcome to the club, buddy!',
        'djangotestcomp@gmail.com',
        [email],
        fail_silently=False,
    )
