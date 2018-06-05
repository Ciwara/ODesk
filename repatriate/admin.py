from django.contrib import admin

# Register your models here.
# from desk.models.Entities import RegistrationSite
from repatriate.models import (
    Collect, Target, Settings, Person, ContactTemoin, DuplicateProgresMenage,
    OrganizationTarget, TargetTypeAssistance, VulnerabilityPerson,
    RegistrationSite, RegistrationSiteProvider)


@admin.register(RegistrationSiteProvider)
class RegistrationSiteProviderAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    list_filter = ('provider', 'site',)


@admin.register(RegistrationSite)
class RegistrationSiteAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug', 'name', 'confirmed')
    list_filter = ('confirmed',)


@admin.register(DuplicateProgresMenage)
class DuplicateProgresMenageAdmin(admin.ModelAdmin):

    model = DuplicateProgresMenage

    list_display = [
        'old_target',
        'new_target',
        'fixed_by',
        'detection_date',
        'fix_date',
        'fixed',
    ]
    list_filter = ['fixed_by', 'fixed']


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

    list_display = ('__str__', 'num_progres_individuel',
                    'is_doublon_pm_pi',
                    'is_invalide_num_pi',
                    'is_not_empty_num_pi_alg',
                    'is_vrf_wihtout_num_pi',
                    'is_sans_doc_avec_num_pi',
                    'is_num_pi_sans_num_pm')
    list_filter = [
        'target',
        'is_invalide_num_pi', 'is_num_pi_sans_num_pm',
        'is_not_empty_num_pi_alg', 'is_vrf_wihtout_num_pi',
        'is_sans_doc_avec_num_pi', 'membre_sexe', 'membre_vulnerabilite',
        'dispo_doc_etat_civil', 'partage_info_perso',
        'existe_centre_etat_civil', 'au_moins_deux_temoins', 'referer']


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):

    model = Target

    list_display = ('identifier', 'site_engistrement', 'num_progres_menage', 'validation_status',
                    'pays_asile', 'site_engistrement', 'camp')
    list_filter = [
        'is_zero_member', 'is_requise_num_progres_menage',
        'is_invalide_num_progres_menage', 'is_invalide_num_tel',
        'is_not_empty_num_progres_menage_alg', 'is_no_doc_with_num_pm',
        'is_site_not_existe', 'beneficiez_lassistance', 'abris', 'membre_pays',
        'etat_sante', 'suivi_formation', 'metier_pays_prove',
        'formation_socio_prof', 'projet_activite', 'camp', 'site_engistrement']


@admin.register(Collect)
class CollectAdmin(admin.ModelAdmin):

    model = Collect
    # list_filter = ['gender', 'etat_civil', 'vulnerabilite', 'nationalite']
