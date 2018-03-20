from django.contrib import admin

# Register your models here.


from migrants.models import (
    Person, Survey, Country)


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):

    model = Survey
    list_filter = ['menage_pays_provenance', 'cause', 'date_arrivee']


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):

    model = Person
    list_filter = ['gender', 'etat_civil', 'vulnerabilite', 'nationalite']


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):

    model = Country
