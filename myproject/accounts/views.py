from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from .forms import SignUpForm, UserUpdateForm
from django.contrib.messages.views import SuccessMessageMixin

from django.contrib.auth.models import User
from django.urls import reverse_lazy

from django.contrib import messages



from django.views.generic import UpdateView, CreateView


# Create your views here.

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


