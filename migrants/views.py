# from django.shortcuts import render


import xlwt

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
# from django.shortcuts import redirect, render
from migrants.models import Survey, Person
from django.db.models import Count
from django.template import loader
# from migrants.forms import (UserCreationForm, UserChangeForm)


@login_required
def dashboard(request):
    # TODO Export xls pour le partage.
    srv = Survey.objects.all()
    template = loader.get_template('migrants/dashboard.html')
    per_lieu_regions = Person.objects.values(
        "survey__lieu_region").annotate(Count("id")).order_by()
    total_survey = Survey.objects.all().count()
    total_person = Person.objects.all().count()
    total_male = Person.objects.filter(gender=Person.MALE).count()
    total_female = Person.objects.filter(gender=Person.FEMALE).count()
    s = Survey.objects.values("menage_pays_provenance").annotate(
        Count('instanceID')).order_by()
    date_entre = Survey.objects.values("date_ebtretien").annotate(
        Count('instanceID')).order_by()

    per_lieu_region = {
        'labels': [i.get('survey__lieu_region').title() for i in per_lieu_regions],
        'label': "Région de retour",
        'title': "",
        'data': [i.get('id__count') for i in per_lieu_regions]
    }
    menage_per_prov = {
        'labels': [i.get('menage_pays_provenance').title() for i in s],
        'label': "Nombre de migrants",
        'title': "",
        'data': [i.get('instanceID__count') for i in s]
    }
    menage_per_date_entrtien = {
        'labels': [i.get('date_ebtretien').strftime('%d-%b-%y') for i in date_entre],
        'label': "Nombre de migrants",
        'title': "",
        'data': [i.get('instanceID__count') for i in date_entre]
    }
    context = {"srv": srv,
               "menage_per_prov": menage_per_prov,
               "menage_per_date_entrtien": menage_per_date_entrtien,
               "total_survey": total_survey,
               "total_person": total_person,
               "total_female": total_female,
               "total_male": total_male,
               "per_lieu_region": per_lieu_region
               }
    return HttpResponse(template.render(context, request))


# @login_required
# def index(request):

#     srv = Survey.objects.all()
#     context = {"srv": srv}
#     template = loader.get_template('index.html')

#     return HttpResponse(template.render(context, request))


@login_required
def table(request):

    srv = Survey.objects.all()
    template = loader.get_template('migrants/tables.html')

    per_lieu_regions = Person.objects.values(
        "survey__lieu_region").annotate(Count("id")).order_by()
    menage_per_prov = Survey.objects.values("menage_pays_provenance").annotate(
        Count('instanceID')).order_by()
    menage_per_date_entrtien = Survey.objects.values("date_ebtretien").annotate(
        Count('instanceID')).order_by()

    context = {"srv": srv,
               "per_lieu_regions": per_lieu_regions,
               "menage_per_prov": menage_per_prov,
               "menage_per_date_entrtien": menage_per_date_entrtien,
               }
    return HttpResponse(template.render(context, request))


@login_required
def survey_table(request):

    surveys = Survey.objects.all()
    for survey in surveys:
        survey.person_url = reverse("person_table", args=[survey.instanceID])
    context = {"surveys": surveys}
    template = loader.get_template('migrants/survey_tables.html')

    return HttpResponse(template.render(context, request))


@login_required
def person_table(request, *args, **kwargs):
    iid = kwargs["iid"]

    survey = Survey.objects.get(instanceID=iid)
    persons = Person.objects.filter(survey=survey)
    for person in persons:
        person.person_detail_url = reverse("person", args=[person.id])

    context = {"persons": persons}
    template = loader.get_template('migrants/person_tables.html')

    return HttpResponse(template.render(context, request))


@login_required
def person(request, *args, **kwargs):
    iid = kwargs["pk"]
    person = Person.objects.get(id=iid)
    context = {"person": person}
    template = loader.get_template('migrants/person_detail.html')

    return HttpResponse(template.render(context, request))


def get_sex(value):
    return "M" if value == "male" else "F"


def get_profession(value):
    if value.get("membre-profession") == 'other':
        return value.get("membre-profession_other")
    return value.get("membre-profession")


@login_required
def export_migrants_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ["ID ", "DATE", "AGENT", "PROVENANCE DU MIGRANT",
               "PRENOMS", "NOM", "SEXE", "DATE DE NAISSANCE", "AGE",
               "PROFESSION", "ETAT CIVIL", "LIEN", "VULNERABILITE",
               "REGION", "CERCLE", "COMMUNE", "VILLAGE", "TEL"]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    for row in Person.objects.all():
        row_num += 1
        col_num = 0
        ws.write(row_num, col_num, row.survey.instanceID, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.survey.date_ebtretien, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.survey.nom_agent, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.survey.menage_pays_provenance.name, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.prenoms, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.nom, font_style)
        col_num += 1
        ws.write(row_num, col_num, get_sex(row.gender), font_style)
        col_num += 1
        ws.write(row_num, col_num, row.ddn, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.age, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.profession, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.etat_civil, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.lien, font_style)
        col_num += 1
        ws.write(row_num, col_num, "", font_style)
        col_num += 1
        ws.write(row_num, col_num, row.survey.lieu_region, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.survey.lieu_cercle, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.survey.lieu_commune, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.survey.lieu_village_autre, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.survey.tel, font_style)
        # break
    wb.save(response)

    return response
