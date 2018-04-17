from django.contrib import admin

# Register your models here.


from migrants.models import (
    Person, Survey, Country)


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):

    model = Survey
    list_display = ['__str__', 'cause', 'menage_pays_provenance',
                    'date_arrivee']
    list_filter = ['menage_pays_provenance', 'cause', 'date_arrivee']


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):

    model = Person

    list_display = ['__str__', 'identifier', 'nom', 'prenoms', 'lien', 'age', 'gender']
    list_filter = ['gender', 'survey__lieu_region', 'vulnerabilite',
                   'nationalite', 'survey__date_ebtretien']


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):

    model = Country
