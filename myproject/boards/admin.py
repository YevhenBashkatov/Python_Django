from django.contrib import admin
from .models import Board, Reader, Blogger, User
from django.contrib.auth.admin import UserAdmin


# Register your models here.

class ReaderInline(admin.StackedInline):
    model = Reader
    can_delete = False
    verbose_name_plural = 'Reader'
    fk_name = 'user'


class BloggerInline(admin.StackedInline):
    model = Blogger
    can_delete = False
    verbose_name_plural = 'Blogger'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_blogger')
    list_select_related = ('reader', 'blogger',)

    def get_is_blogger(self, instance):
        return instance.profile.location

    get_is_blogger.short_description = 'is_blogger'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Board)
