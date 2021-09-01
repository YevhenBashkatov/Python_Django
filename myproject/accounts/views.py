import json
from urllib import parse, request, response

from PIL import Image
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login, authenticate, login
from .forms import SignUpForm, UserUpdateForm
from django.contrib.messages.views import SuccessMessageMixin

from django.contrib.auth.models import User
from django.urls import reverse_lazy

from django.contrib import messages



from django.views.generic import UpdateView, CreateView


# Create your views here.
from .models import Avatar
from myproject import settings


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')

    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


class UserUpdateView(SuccessMessageMixin, UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email',)
    template_name = 'my_account.html'
    success_message = 'Account has been updated!'
    success_url = reverse_lazy('home')

    def form_valid(self, form):

        if(self.request.FILES):
            print(self.request.FILES)
            avatar = Avatar.objects.create(file=self.request.FILES['photo'], description='avatar')
            x = float(self.request.POST.get('x'))
            y = float(self.request.POST.get('y'))
            h = float(self.request.POST.get('height'))
            w = float(self.request.POST.get('width'))

            image = Image.open(avatar.file)
            cropped_image = image.crop((x, y, w+x, h+y))
            resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
            resized_image.save(avatar.file.path, "PNG")
            self.request.user.avatar = avatar

        form.save()
        messages.success(
            self.request, 'Your account was updated successfully!')
        return redirect('my_account')

    def get_object(self):
        return self.request.user

#
# def account_settings(request):
#     user = get
#     if request.method == 'POST':
#         form = UserUpdateForm(request.user, request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request,'Account has been updated!')
#     else:
#         form = UserUpdateForm(request.user)
#     return render(request,'my_account.html', {'form': form})


class LoginViewCustom(LoginView):
    template_name = 'login.html'
    model = User

    def form_valid(self, form):
        recaptcha_response = self.request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = parse.urlencode(values).encode()
        req = request.Request(url, data=data)
        response = request.urlopen(req)
        result = json.loads(response.read().decode())
        if result['success']:
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            if user is not None:
                login(self.request, user)
                return redirect('home')
            else:
                messages.error(self.request, 'Incorrect username or password. Please try again.')
                return render(self.request, 'login.html', {'form': form})
        else:
            messages.error(self.request, 'Invalid reCAPTCHA. Please try again.')
            return render(self.request, 'login.html', {'form': form})