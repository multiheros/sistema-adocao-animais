from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, Profile


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
	pass


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ("id", 'user', 'phone_number')
	search_fields = ('user__username', 'phone_number')