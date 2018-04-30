from django.contrib import admin

# Register your models here.


from migrants.models import (
    Person, Survey, Country)


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):

    model = Survey
    list_display = ['__str__', 'cause', 'menage_pays_provenance',
                    'date_arrivee', 'date_entretien']
    list_filter = ['menage_pays_provenance', 'cause', 'date_arrivee',
                   'date_entretien']


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):

    model = Person

    list_display = ['__str__', 'identifier', 'profession', 'lien', 'age', 'gender']
    list_filter = ['gender', 'survey__adresse_mali_lieu_region', 'survey__adresse_mali_lieu_cercle', 'membre_vulnerabilite',
                   'nationalite', 'survey__date_entretien']


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):

    model = Country
