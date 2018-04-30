from django.contrib import admin

# Register your models here.
# from desk.models.Entities import RegistrationSite
from repatriate.models import (
    Collect, Target, Settings, Person, ContactTemoin,
    OrganizationTarget, TargetTypeAssistance)


@admin.register(TargetTypeAssistance)
class TargetTypeAssistanceAdmin(admin.ModelAdmin):

    model = TargetTypeAssistance

    list_filter = ['type_assistance', ]


@admin.register(ContactTemoin)
class ContactTemoinAdmin(admin.ModelAdmin):

    model = ContactTemoin


@admin.register(OrganizationTarget)
class OrganizationTargetAdmin(admin.ModelAdmin):

    model = OrganizationTarget

    list_filter = ['organization', ]


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):

    model = Settings


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):

    model = Person


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):

    model = Target

    list_display = ('identifier', 'validation_status', 'pays_asile',
                    'site_engistrement', 'camp')
    list_filter = ['validation_status', 'site_engistrement', 'camp']


@admin.register(Collect)
class CollectAdmin(admin.ModelAdmin):

    model = Collect
    # list_filter = ['gender', 'etat_civil', 'vulnerabilite', 'nationalite']
