from django.contrib import admin

# Register your models here.


from odkextractor.models import (FormSettings)


@admin.register(FormSettings)
class FormSettingsAdmin(admin.ModelAdmin):

    model = FormSettings
    list_display = ['__str__', 'form_id', 'app', 'odk_username',
                    'active', 'last_update']
    list_filter = ['active', 'last_update']
