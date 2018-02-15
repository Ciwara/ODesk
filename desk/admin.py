from django.contrib import admin

# Register your models here.


# from django.contrib.auth.models import Group
# from django.contrib.auth.admin import UserAdmin
from desk.models import Person, Survey, Country, Entity, EntityType


@admin.register(EntityType)
class EntityTypeAdmin(admin.ModelAdmin):

    model = EntityType


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):

    model = Entity

    list_filter = ['type', 'parent']


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
    # list_filter = ['isactivated', 'author']
