# from django.shortcuts import render


import xlwt
from datetime import datetime
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# from django.shortcuts import redirect, render
from migrants.models import Survey, Person
# from desk.celery import app
from django.db.models import Count
from django.template import loader

from odkextractor.models import FormID
# from migrants.forms import (UserCreationForm, UserChangeForm)


@login_required
def dashboard(request):
    # TODO Export xls pour le partage.
    srv = Survey.objects.all()
    template = loader.get_template('migrants/dashboard.html')
    date_last_update = FormID.objects.order_by().first().last_update
    per_adresse_mali_lieu_regions = Person.objects.values(
        "survey__adresse_mali_lieu_region").annotate(Count("id")).order_by()
    total_survey = Survey.objects.all().count()
    persons = Person.objects.all()
    persons_m = persons.filter(gender=Person.MALE)
    persons_f = persons.filter(gender=Person.FEMALE)

    total_person = persons.count()
    total_male = persons_m.count()
    total_female = persons_f.count()
    persons_per_pprov = persons.values("survey__menage_pays_provenance").annotate(
        Count('identifier')).order_by()
    persons_per_pprov_m = persons_m.values("survey__menage_pays_provenance").annotate(
        Count('identifier')).order_by()
    persons_per_pprov_f = persons_f.values("survey__menage_pays_provenance").annotate(
        Count('identifier')).order_by()
    per_adresse_mali_lieu_region = {
        'title': "Les migrants par région de retour.",
        'name': "Région de retour",
        'tooltip': "Nb. migrant",
        'series': [[i.get('survey__adresse_mali_lieu_region').upper(),
                    i.get('id__count')] for i in per_adresse_mali_lieu_regions]
    }
    persons_per_pprov_for_chart = {
        'categories': [i.get('survey__menage_pays_provenance').title() for i in persons_per_pprov],
        'label': "Nombre de migrants",
        'title': "",
        'series': [
            {'name': 'Total',
             'data': [i.get('identifier__count') for i in persons_per_pprov]},
            {'name': 'Total',
             'data': [i.get('identifier__count') for i in persons_per_pprov_m]},
            {'name': 'Total',
             'data': [i.get('identifier__count') for i in persons_per_pprov_f]}
        ]
    }

    date_entre = Person.objects.values("survey__date_entretien").annotate(
        Count('identifier')).order_by("survey__date_entretien")
    date_entre_m = Person.objects.filter(
        gender=Person.MALE).values("survey__date_entretien").annotate(
        Count('identifier')).order_by()
    date_entre_f = Person.objects.filter(
        gender=Person.FEMALE).values("survey__date_entretien").annotate(
        Count('identifier')).order_by()
    menage_per_date_entrtien = {
        'categories': [i.get('survey__date_entretien').strftime(
            '%d-%b-%y') for i in date_entre],
        'text': "Nombre de migrants",
        'title': "Nombre total retourné par date arrivée.",
        'type': "line",
        'series': [
            {"name": "Total", "data": [i.get(
                'identifier__count') for i in date_entre]},
            {"name": "Total homme", "data": [i.get(
                'identifier__count') for i in date_entre_m]},
            {"name": "Total femme", "data": [i.get(
                'identifier__count') for i in date_entre_f]}]
    }
    context = {"srv": srv,
               "persons_per_pprov_for_chart": persons_per_pprov_for_chart,
               "menage_per_date_entrtien": menage_per_date_entrtien,
               "total_survey": total_survey,
               "total_person": total_person,
               "total_female": total_female,
               "total_male": total_male,
               "per_adresse_mali_lieu_region": per_adresse_mali_lieu_region,
               "date_last_update": date_last_update
               }

    return HttpResponse(template.render(context, request))


@login_required
def database_mig(request):
    persons = Person.objects.all()
    context = {"persons": persons}
    template = loader.get_template('migrants/person_tables.html')
    return HttpResponse(template.render(context, request))


@login_required
def find_mig(request):

    surveys = Survey.objects.all()
    context = {"surveys": surveys}
    template = loader.get_template('migrants/survey_tables.html')

    return HttpResponse(template.render(context, request))


@login_required
def survey_table(request):

    surveys = Survey.objects.all().order_by('-date_entretien')
    paginator = Paginator(surveys, 10)

    page = request.GET.get('page')
    try:
        surveys = paginator.page(page)
    except PageNotAnInteger:
        surveys = paginator.page(1)
    except EmptyPage:
        surveys = paginator.page(paginator.num_pages)
    context = {"surveys": surveys}
    template = loader.get_template('migrants/survey_tables.html')

    return HttpResponse(template.render(context, request))


@login_required
def person_table(request, *args, **kwargs):
    iid = kwargs["iid"]

    survey = Survey.objects.get(instance_id=iid)
    persons = Person.objects.filter(survey=survey)
    context = {"persons": persons, "survey": survey}
    template = loader.get_template('migrants/person_tables.html')

    return HttpResponse(template.render(context, request))


@login_required
def person(request, *args, **kwargs):
    iid = kwargs["pk"]
    person = Person.objects.get(id=iid)
    person.person_photo_url = reverse("person_photo", args=[person.id])

    context = {"person": person}
    template = loader.get_template('migrants/person_detail.html')

    return HttpResponse(template.render(context, request))


@login_required
def show_media(request, *args, **kwargs):
    from odkextractor.commons import get_path
    key_odk = kwargs["key_odk"]
    p = Person.objects.get(id=key_odk)
    return HttpResponse(get_path("data,{}".format(p.membre_photo)))


def get_sex(value):
    return "M" if value == "male" else "F"


def get_profession(value):
    if value.get("membre-profession") == 'other':
        return value.get("membre-profession_other")
    return value.get("membre-profession")


def get_date(date):
    if date:
        date = date.strftime("%x")
    return date


def date_format(strdate):
    return datetime.strptime(strdate, '%d-%m-%Y')


@login_required
# @app.task
def export_migrants_xls(request, *args, **kwargs):

    start_date = date_format(kwargs["start"])
    end_date = date_format(kwargs["end"])
    print(start_date)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="migrant_data.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ["ID ", "DATE ENTRETIEN", "DATE ARRIVEE", "AGENT", "PROVENANCE DU MIGRANT",
               "PRENOMS", "NOM", "SEXE", "DATE DE NAISSANCE", "AGE",
               "PROFESSION", "ETAT CIVIL", "LIEN", "VULNERABILITE",
               "REGION", "CERCLE", "COMMUNE", "VILLAGE", "TEL"]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    for row in Person.objects.filter(survey__date_entretien__gte=start_date,
                                     survey__date_entretien__lte=end_date):
        row_num += 1
        col_num = 0
        ws.write(row_num, col_num, row.survey.instance_id, font_style)
        col_num += 1
        ws.write(row_num, col_num, get_date(row.survey.date_entretien), font_style)
        col_num += 1
        ws.write(row_num, col_num, get_date(row.survey.date_arrivee), font_style)
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
        ws.write(row_num, col_num, get_date(row.ddn), font_style)
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
        ws.write(row_num, col_num, row.survey.adresse_mali_lieu_region, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.survey.adresse_mali_lieu_cercle, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.survey.adresse_mali_lieu_commune, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.survey.adresse_mali_lieu_village_autre, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.survey.tel, font_style)
        # break
    wb.save(response)

    return response
