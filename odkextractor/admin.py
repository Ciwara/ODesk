from django.contrib import admin

# Register your models here.


from odkextractor.models import (ODKSetting, FormID)


class FormIDInline(admin.TabularInline):

    model = FormID


@admin.register(ODKSetting)
class ODKSettingAdmin(admin.ModelAdmin):

    model = ODKSetting
    list_display = ['__str__', 'app', 'odk_username',
                    'active', 'last_update']
    list_filter = ['active', 'last_update']

    inlines = [
        FormIDInline,
    ]


@admin.register(FormID)
class FormIDAdmin(admin.ModelAdmin):

    model = FormID
    list_display = ['__str__', 'form_id',
                    'last_update', 'odk_setting', 'active', 'status']
    list_filter = ['active', 'last_update', 'status']
