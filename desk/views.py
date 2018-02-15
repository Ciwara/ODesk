# from django.shortcuts import render

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from desk.models import Survey, Person, Member
from django.db.models import Count
from django.template import loader
from desk.forms import (UserCreationForm, UserChangeForm)


@login_required
def dashboard(request):
    # TODO Export xls pour le partage.
    srv = Survey.objects.all()
    template = loader.get_template('dashboard.html')
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
def index(request):

    srv = Survey.objects.all()
    context = {"srv": srv}
    template = loader.get_template('index.html')

    return HttpResponse(template.render(context, request))


@login_required
def table(request):

    srv = Survey.objects.all()
    template = loader.get_template('tables.html')

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
    template = loader.get_template('survey_tables.html')

    return HttpResponse(template.render(context, request))


@login_required
def person_table(request, *args, **kwargs):
    iid = kwargs["iid"]

    survey = Survey.objects.get(instanceID=iid)
    persons = Person.objects.filter(survey=survey)
    for person in persons:
        person.person_detail_url = reverse("person", args=[person.id])

    context = {"persons": persons}
    template = loader.get_template('person_tables.html')

    return HttpResponse(template.render(context, request))


@login_required
def person(request, *args, **kwargs):
    iid = kwargs["pk"]
    print(iid)

    person = Person.objects.get(id=iid)
    context = {"person": person}
    template = loader.get_template('person_detail.html')

    return HttpResponse(template.render(context, request))



@login_required
def user_new(request):
    if request.method == 'POST' and '_user_new' in request.POST:
        user_new_form = UserCreationForm(request.POST or None)
        if user_new_form.is_valid():
            user_new_form.save()
            return redirect("/home")
    else:
        user_new_form = UserCreationForm()
    cxt = {"user_new_form": user_new_form}
    return render(request, 'user_new.html', cxt)


@login_required
def user_change(request, *args, **kwargs):
    id_url = kwargs["pk"]

    selected_member = Member.objects.get(pk=id_url)
    if request.method == 'POST' and '_user_change' in request.POST:
        user_change_form = UserChangeForm(request.POST,
                                          instance=selected_member)
        if user_change_form.is_valid():
            user_change_form.save()
            return redirect("/user_manager")
    else:
        user_change_form = UserChangeForm(instance=selected_member)
    cxt = {"user_change_form": user_change_form}
    return render(request, 'user_change.html', cxt)


