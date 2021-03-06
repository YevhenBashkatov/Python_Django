from django import forms
from .models import Board, Topic, Post, Interests, Categories, User, Blogger, Reader, Photo
from django.contrib.auth.forms import UserCreationForm

from django.db import transaction
from django.shortcuts import redirect


class NewTopicForm(forms.ModelForm):
    photo = forms.IntegerField(required=False, widget=forms.HiddenInput, label="")
    message = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 5, 'placeholder': 'What is on your mind?'}
    ),
        max_length=4000,
        help_text='The max length of the text is 4000')

    class Meta:
        model = Topic
        fields = ['subject', 'message', 'photo']


class PhotoForm(forms.ModelForm):
    photo = forms.FileField(widget=forms.FileInput)

    class Meta:
        model = Photo
        fields = ('photo',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message', ]


class BloggerSignUpForm(UserCreationForm):
    birthday = forms.DateField(input_formats=['%d/%m/%Y'], required=True, help_text='Example: 02/07/2000')
    city = forms.CharField(required=True)
    country = forms.CharField(required=True)

    categories = forms.ModelMultipleChoiceField(queryset=Categories.objects.all(),
                                           widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
                                           required=True,
                                                )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", 'password1', 'password2', 'email', "birthday", "country", 'city', 'categories')

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_blogger = True
        user.email = self.cleaned_data.get('email')
        print('USER Email _____________', user.email)
        user.save()
        print('USER SAVE _____________', user.is_blogger)

        blogger = Blogger.objects.create(user=user)
        print('Blogger CREATED _____________', user.is_blogger)

        blogger.birthday = self.cleaned_data.get('birthday')
        blogger.city = self.cleaned_data.get('city')
        blogger.country = self.cleaned_data.get('country')
        blogger.categories.add(*self.cleaned_data.get('categories'))
        blogger.save()
        print('Blogger SAVED _____________', user.is_blogger)

        return user


class ReaderSignUpForm(UserCreationForm):
    is_adult = forms.BooleanField()
    interests = forms.ModelMultipleChoiceField(queryset=Interests.objects.all(),
                                               widget=forms.CheckboxSelectMultiple,
                                               required=True)

    class Meta(UserCreationForm.Meta):
        model = User

        fields = ("username", 'interests')

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_reader = True
        user.save()
        reader = Reader.objects.create(user=user)
        reader.is_adult = self.cleaned_data.get('is_adult')
        reader.interests.add(*self.cleaned_data.get('interests'))
        reader.save()

        return user


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ('name', 'description')
