from django.contrib import admin
from .models import Animal


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ("id", 'name', 'species', 'breed', 'age', 'adopted')
    search_fields = ('name', 'species', 'breed')
    list_filter = ('species', 'adopted')
    ordering = ('name',)