# from django.shortcuts import render

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from migrants.models import Survey, Person
from django.db.models import Count
from django.template import loader
# from migrants.forms import (UserCreationForm, UserChangeForm)
from repatriate.models.collects import Collect
from repatriate.models.targets import Target


@login_required
def dashboard(request):
    # TODO Export xls pour le partage.
    srv = Survey.objects.all()
    template = loader.get_template('repatriate/dashboard.html')
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


def desk_controle(request):

    template = loader.get_template('repatriate/desk_controle.html')
    user = request.user

    context = {"user": user}

    return HttpResponse(template.render(context, request))
