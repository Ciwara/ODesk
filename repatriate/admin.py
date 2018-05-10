from django.contrib import admin

# Register your models here.
# from desk.models.Entities import RegistrationSite
from repatriate.models import (
    Collect, Target, Settings, Person, ContactTemoin,
    OrganizationTarget, TargetTypeAssistance, VulnerabilityPerson)


@admin.register(VulnerabilityPerson)
class VulnerabilityPersonAdmin(admin.ModelAdmin):

    model = VulnerabilityPerson

    list_filter = ['sub_besoin', 'besoin_specifique']


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

    list_display = ('identifier', 'membre_nom', 'membre_prenom', 'membre_sexe',
                    'membre_age')
    list_filter = ['membre_sexe', 'membre_vulnerabilite',
                   'dispo_doc_etat_civil', 'partage_info_perso',
                   'existe_centre_etat_civil', 'au_moins_deux_temoins',
                   'referer']


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):

    model = Target

    list_display = ('identifier', 'validation_status', 'pays_asile',
                    'site_engistrement', 'camp')
    list_filter = ['beneficiez_lassistance', 'abris', 'membre_pays',
                   'etat_sante', 'suivi_formation', 'metier_pays_prove',
                   'formation_socio_prof', 'projet_activite', 'camp',
                   'site_engistrement']


@admin.register(Collect)
class CollectAdmin(admin.ModelAdmin):

    model = Collect
    # list_filter = ['gender', 'etat_civil', 'vulnerabilite', 'nationalite']
