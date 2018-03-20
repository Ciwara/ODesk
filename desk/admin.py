from django.contrib import admin

# Register your models here.


from django.utils.translation import ugettext_lazy as _
# from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from desk.models import (
    Entity, EntityType, Provider, RegistrationSite)


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):

    list_display = ('slug', 'name', 'type', 'parent', 'parent_level')
    list_filter = ('type',)
    ordering = ('slug',)
    search_fields = ('slug', 'name')


@admin.register(RegistrationSite)
class RegistrationSiteAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug', 'name')


class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'identity', 'category', 'priority', 'provider')
    list_filter = ('category', 'priority')


class PhoneNumberTypeAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'priority')


@admin.register(Provider)
class ProviderAdmin(UserAdmin):
    # form = ProviderModificationForm
    # add_form = ProviderCreationForm
    list_display = ('__str__', 'username', 'email',
                    'first_name', 'last_name', 'is_staff')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email',
                       'is_superuser', 'is_staff', 'is_active', 'site')}),
        ("Personnal info", {
            'classes': ('wide',),
            'fields': ('gender', 'title', 'maiden_name', 'first_name',
                       'middle_name', 'last_name', 'position')}),
    )

    fieldsets = (
        (None, {'fields': ('username', 'password', 'email', 'site')}),
        (_('Personal info'), {'fields': ('gender', 'title', 'maiden_name',
                                         'first_name', 'middle_name',
                                         'last_name', 'position')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(EntityType)
class EntityTypeAdmin(admin.ModelAdmin):

    model = EntityType


# admin.site.register(Domain)
# admin.site.register(Cluster)
# admin.site.register(Group)
# admin.site.register(Participation)
# admin.site.register(PeriodicTask)
# admin.site.register(Privilege)
# admin.site.register(Accreditation)
