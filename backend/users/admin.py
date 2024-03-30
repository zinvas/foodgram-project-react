from django.contrib import admin

from users.models import User, Subscribe


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'password'
    )
    list_filter = (
        'email',
        'username',
    )
    list_editable = ('password',)
    search_fields = ('username', 'email')


class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
