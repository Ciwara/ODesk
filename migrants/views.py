# from django.shortcuts import render
import xlwt
from datetime import datetime
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# from django.shortcuts import redirect
# from desk.celery import app
from django.db.models import Count
from django.template import loader
from django.db.models.functions import TruncMonth
from django.db.models import Q
# from django.db.models import Sum, Count

from migrants.models import Survey, Person
from odkextractor.models import FormID
from migrants.forms import (SearchFormPerPeriod, SearchMigrantForm)

from desk.tools import str_to_date


@login_required
def dashboard(request):
    # TODO Export xls pour le partage.
    srv = Survey.objects.all()
    template = loader.get_template('migrants/dashboard.html')
    date_last_update = FormID.objects.order_by().first().last_update
    per_adresse_mali_lieu_regions = Person.objects.values(
        "survey__adresse_mali_lieu_region").annotate(Count("id")).order_by()
    total_survey = Survey.objects.all().count()
    total_person = Person.objects.all().count()
    total_male = Person.objects.filter(gender=Person.MALE).count()
    total_female = Person.objects.filter(gender=Person.FEMALE).count()
    s = Survey.objects.values("menage_pays_provenance").annotate(
        Count('instance_id')).order_by()
    date_entre = Survey.objects.values("date_entretien").annotate(
        Count('instance_id')).order_by("date_entretien")

    p = Person.objects.annotate(
        month=TruncMonth('survey__date_entretien')).values('month').annotate(
        c=Count('identifier')).order_by('survey__date_entretien')
    per_month = {
        'categories': [i.get('month').strftime('%d %b %Y') for i in p],
        'label': "",
        'title': "Nombre de retourné",
        'series':
            [{"name": "Total retournés", "data": [i.get('c') for i in p]},
            # {"name": "Homme", "data": [i.get('gm') for i in p]},
            # {"name": "Femme", "data": [i.get('gf') for i in p]},
            ],
    }

    per_adresse_mali_lieu_region = {
        'labels': [i.get('survey__adresse_mali_lieu_region').title() for i in per_adresse_mali_lieu_regions],
        'label': "Région de retour",
        'title': "",
        'data': [i.get('id__count') for i in per_adresse_mali_lieu_regions]
    }
    menage_per_prov = {
        'labels': [i.get('menage_pays_provenance').title() for i in s],
        'label': "Nombre total migrant",
        'title': "",
        'data': [i.get('instance_id__count') for i in s]
    }
    menage_per_date_entrtien = {
        'labels': [i.get('date_entretien').strftime('%d-%b-%y') for i in date_entre],
        'label': "Nombre total migrant",
        'title': "",
        'data': [i.get('instance_id__count') for i in date_entre]
    }
    context = {"srv": srv,
               "per_month": per_month,
               "menage_per_prov": menage_per_prov,
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
def manager_mig(request):

    template = loader.get_template('migrants/manager_data_migrantion.html')
    context = {}

    date_last_update = FormID.objects.order_by().first().last_update
    if request.method == 'POST':
        period_form = SearchFormPerPeriod(request.POST or None)
        date_s = str_to_date(request.POST.get('start_date'))
        date_e = str_to_date(request.POST.get('end_date'))
        persons = Person.objects.filter(
            survey__date_entretien__gte=date_s,
            survey__date_entretien__lte=date_e
        ).order_by('-survey__date_entretien')
        nb_person = persons.count()
        nb_person_f = persons.filter(gender=Person.FEMALE).count()
        nb_person_m = persons.filter(gender=Person.MALE).count()
        if 'export_per_date' in request.POST:
            file_name = "personne-{}-{} ".format(date_s, date_e)
            return export_users_xls(file_name, persons)
        # return redirect("export-xls/{start}/{end}".format(
        #     start=date_s, end=date_e))
    else:
        persons = Person.objects.all().order_by('-survey__date_entretien')[:100]
        nb_person = 0
        nb_person_f = 0
        nb_person_m = 0
        period_form = SearchFormPerPeriod()

    # paginator = Paginator(persons, 10)
    # page = request.GET.get('page')
    # try:
    #     persons = paginator.page(page)
    # except PageNotAnInteger:
    #     persons = paginator.page(1)
    # except EmptyPage:
    #     persons = paginator.page(paginator.num_pages)
    context.update({
        "persons": persons})
    context.update({"date_last_update": date_last_update,
                    "period_form": period_form, "nb_person": nb_person,
                    "nb_person_m": nb_person_m, "nb_person_f": nb_person_f})

    return HttpResponse(template.render(context, request))


@login_required
def find_mig(request):

    template = loader.get_template('migrants/find_migrants.html')
    if request.method == 'POST' and 'search' in request.POST:
        search_migrant_form = SearchMigrantForm(request.POST or None)
        search_text = request.POST.get('migrant')
        persons = Person.objects.filter(
            Q(prenoms__icontains=search_text) |
            Q(nom__icontains=search_text) |
            Q(survey__tel__icontains=search_text)
        ).order_by('-survey__date_entretien')
        context = {"persons": persons, }
    else:
        search_migrant_form = SearchMigrantForm()
    context = {"search_migrant_form": search_migrant_form}

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


def export_users_xls(file_name, persons):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="{}.xlsx"'.format(file_name)

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('persons')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ["ID ", "DATE ENTRETIEN", "DATE ARRIVEE", "PROVENANCE DU MIGRANT",
               "PRENOMS", "NOM", "SEXE", "DATE DE NAISSANCE", "AGE",
               "PROFESSION", "ETAT CIVIL", "LIEN",
               "REGION", "CERCLE", "COMMUNE", "VILLAGE", "TEL"]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = persons.values_list(
            'survey__instance_id',
            'survey__date_entretien',
            'survey__date_arrivee',
            'survey__menage_pays_provenance',
            'prenoms',
            'nom',
            'gender',
            'ddn',
            'age',
            'profession',
            'etat_civil',
            'lien',
            'survey__adresse_mali_lieu_region',
            'survey__adresse_mali_lieu_cercle',
            'survey__adresse_mali_lieu_commune',
            'survey__adresse_mali_lieu_village_autre',
            'survey__tel',)
    for row in rows:
        print(row)
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


# @login_required
# # @app.task
# def export_migrants_xls(request, *args, **kwargs):

#     start_date = date_format(kwargs["start"])
#     end_date = date_format(kwargs["end"])
#     # print(start_date)
#     response = HttpResponse(content_type='application/ms-excel')
#     response['Content-Disposition'] = 'attachment; filename="migrant_data.xls"'

#     wb = xlwt.Workbook(encoding='utf-8')
#     ws = wb.add_sheet('Users')

#     # Sheet header, first row
#     row_num = 0

#     font_style = xlwt.XFStyle()
#     font_style.font.bold = True

#     columns = ["ID ", "DATE ENTRETIEN", "DATE ARRIVEE", "AGENT", "PROVENANCE DU MIGRANT",
#                "PRENOMS", "NOM", "SEXE", "DATE DE NAISSANCE", "AGE",
#                "PROFESSION", "ETAT CIVIL", "LIEN", "VULNERABILITE",
#                "REGION", "CERCLE", "COMMUNE", "VILLAGE", "TEL"]

#     for col_num in range(len(columns)):
#         ws.write(row_num, col_num, columns[col_num], font_style)

#     # Sheet body, remaining rows
#     font_style = xlwt.XFStyle()

#     for row in Person.objects.filter(survey__date_entretien__gte=start_date,
#                                      survey__date_entretien__lte=end_date):
#         row_num += 1
#         col_num = 0
#         ws.write(row_num, col_num, row.survey.instance_id, font_style)
#         col_num += 1
#         ws.write(row_num, col_num, get_date(row.survey.date_entretien), font_style)
#         col_num += 1
#         ws.write(row_num, col_num, get_date(row.survey.date_arrivee), font_style)
#         col_num += 1
#         ws.write(row_num, col_num, row.survey.nom_agent, font_style)
#         col_num += 1
#         ws.write(row_num, col_num, row.survey.menage_pays_provenance.name, font_style)
#         col_num += 1
#         ws.write(row_num, col_num, row.prenoms, font_style)
#         col_num += 1
#         ws.write(row_num, col_num, row.nom, font_style)
#         col_num += 1
#         ws.write(row_num, col_num, get_sex(row.gender), font_style)
#         col_num += 1
#         ws.write(row_num, col_num, get_date(row.ddn), font_style)
#         col_num += 1
#         ws.write(row_num, col_num, row.age, font_style)
#         col_num += 1
#         ws.write(row_num, col_num, row.profession, font_style)
#         col_num += 1
#         ws.write(row_num, col_num, row.etat_civil, font_style)
#         col_num += 1
#         ws.write(row_num, col_num, row.lien, font_style)
#         col_num += 1
#         ws.write(row_num, col_num, "", font_style)
#         col_num += 1
#         ws.write(row_num, col_num, row.survey.adresse_mali_lieu_region, font_style)
#         col_num += 1
#         ws.write(row_num, col_num, row.survey.adresse_mali_lieu_cercle, font_style)
#         col_num += 1
#         ws.write(row_num, col_num, row.survey.adresse_mali_lieu_commune, font_style)
#         col_num += 1
#         ws.write(row_num, col_num, row.survey.adresse_mali_lieu_village_autre, font_style)
#         col_num += 1
#         ws.write(row_num, col_num, row.survey.tel, font_style)
#         # break
#     wb.save(response)

#     return response
