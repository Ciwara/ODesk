from django.contrib import admin

# Register your models here.
# from desk.models.Entities import RegistrationSite
from repatriate.models import (
    Collect, Target, Settings, Person, ContactTemoin, Camp, Organization,
    Lien, NiveauxScolaire, Activite, TypeAssistance,
    TargetTypeAssistance
)


@admin.register(TargetTypeAssistance)
class TargetTypeAssistanceAdmin(admin.ModelAdmin):

    model = TargetTypeAssistance


@admin.register(TypeAssistance)
class TypeAssistanceAdmin(admin.ModelAdmin):

    model = TypeAssistance


@admin.register(NiveauxScolaire)
class NiveauxScolaireAdmin(admin.ModelAdmin):

    model = NiveauxScolaire


@admin.register(Lien)
class LienAdmin(admin.ModelAdmin):

    model = Lien


@admin.register(Activite)
class ActiviteAdmin(admin.ModelAdmin):

    model = Activite


@admin.register(Camp)
class CampAdmin(admin.ModelAdmin):

    model = Camp


# @admin.register(RegistrationSite)
# class RegistrationSiteAdmin(admin.ModelAdmin):

#     model = RegistrationSite


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):

    model = Organization


@admin.register(ContactTemoin)
class ContactTemoinAdmin(admin.ModelAdmin):

    model = ContactTemoin


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):

    model = Settings


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):

    model = Person


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):

    model = Target
    # list_filter = ['menage_pays_provenance', 'cause', 'date_arrivee']


@admin.register(Collect)
class CollectAdmin(admin.ModelAdmin):

    model = Collect
    # list_filter = ['gender', 'etat_civil', 'vulnerabilite', 'nationalite']
