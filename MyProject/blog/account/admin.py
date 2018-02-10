from django.contrib import admin

from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('cute_name', 'user')
    search_fields = ('cute_name',)


admin.site.register(Profile, ProfileAdmin)
