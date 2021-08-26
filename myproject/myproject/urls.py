"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from accounts import views as accounts_views
from boards import views

from django.urls import reverse_lazy

from boards import utils

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.BoardListView.as_view(), name='home'),
    path('signup/', accounts_views.signup, name='signup'),
    path('signup/blogger', views.BloggerSignUpView.as_view(), name='blogger_signup'),
    path('signup/reader', views.ReaderSignUpView.as_view(), name='reader_signup', ),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('oauth/', include('social_django.urls', namespace='social')),

    path('reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset.html',
        email_template_name='password_reset_email.html',
        subject_template_name='password_reset_subject.txt'
    ),
         name='password_reset'),
    path('reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),

    path('settings/account', accounts_views.UserUpdateView.as_view(), name='my_account'),
    path('settings/password/', auth_views.PasswordChangeView.as_view(template_name='password_change.html'),
         name='password_change'),
    path('settings/password/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'),
         name='password_change_done'),

    path('boards/create/', views.board_create, name='board_create'),
    path('boards/<int:pk>/update', views.board_update, name='board_update'),
    path('boards/<int:pk>/delete', views.board_delete, name='board_delete'),

    path('boards/<int:pk>', views.TopicListView.as_view(), name='board_topics'),

    path('boards/<int:pk>/new/', views.new_topic, name='new_topic'),
    path('boards/<int:pk>/new/basic-upload', views.BasicUploadView.as_view(), name='basic_upload'),
    path('boards/<int:pk>/to_pdf/', utils.to_pdf, name='to_pdf'),
    path('boards/<int:pk>/export_topics_csv/', utils.export_topics_csv, name='export_topics_csv'),
    path('email_send/', utils.test_send, name='test_send'),
    path('boards/<int:pk>/topics/<int:topic_pk>', views.PostListView.as_view(), name='topic_posts'),
    path('boards/<int:pk>/topics/<int:topic_pk>/reply', views.reply_topic, name='reply_topic'),
    path('boards/<int:pk>/topics/<int:topic_pk>/post/<int:post_pk>/edit', views.PostUpdateView.as_view(),
         name='edit_post'),

    path('pages/', include('django.contrib.flatpages.urls')),
    path('admin/', admin.site.urls),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)