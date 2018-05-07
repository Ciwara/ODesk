# from django.shortcuts import render

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.db.models import Count
from django.template import loader
from repatriate.models import Person, Target


@login_required
def dashboard(request):
    # TODO Export xls pour le partage.
    srv = Target.objects.all()
    template = loader.get_template('repatriate/dashboard.html')
    per_lieu_regions = Person.objects.values(
        "target__lieu_region").annotate(Count("identifier")).order_by()
    total_target = Target.objects.all().count()
    total_person = Person.objects.all().count()
    total_male = Person.objects.filter(membre_sexe=Person.MALE).count()
    total_female = Person.objects.filter(membre_sexe=Person.FEMALE).count()
    s = Target.objects.values("point_de_entree").annotate(
        Count('instance_id')).order_by()
    date_entre = Person.objects.values("target__date_entretien").annotate(
        Count('identifier')).order_by()
    date_entre_m = Person.objects.filter(
        membre_sexe=Person.MALE).values("target__date_entretien").annotate(
        Count('identifier')).order_by()
    date_entre_f = Person.objects.filter(
        membre_sexe=Person.MALE).values("target__date_entretien").annotate(
        Count('identifier')).order_by()

    per_lieu_region = {
        'labels': [i.get('target__lieu_region').title() for i in per_lieu_regions],
        'label': "Région de retour",
        'title': "",
        'data': [i.get('id__count') for i in per_lieu_regions]
    }
    menage_per_prov = {
        'labels': [i.get('point_de_entree').title() for i in s],
        'label': "Nombre de migrants",
        'title': "",
        'data': [i.get('instance_id__count') for i in s]
    }
    menage_per_date_entrtien = {
        'categories': [i.get('target__date_entretien').strftime('%d-%b-%y') for i in date_entre],
        'text': "Nombre de migrants",
        'title': "Nombre total migrants par date arrivée.",
        'type': "line",
        'series': [{
                "name": "Homme",
                "data": [i.get('identifier__count') for i in date_entre_m]},
                {"name": "Femme",
                "data": [i.get('identifier__count') for i in date_entre_f]}]
    }

    context = {"srv": srv,
               "menage_per_prov": menage_per_prov,
               "menage_per_date_entrtien": menage_per_date_entrtien,
               "total_target": total_target,
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

    srv = Target.objects.all()
    per_lieu_regions = Person.objects.values(
        "target__lieu_region").annotate(Count("identifier")).order_by()
    total_target = Target.objects.all().count()
    total_person = Person.objects.all().count()
    total_male = Person.objects.filter(membre_sexe=Person.MALE).count()
    total_female = Person.objects.filter(membre_sexe=Person.FEMALE).count()
    s = Target.objects.values("point_de_entree").annotate(
        Count('instance_id')).order_by()
    date_entre = Person.objects.values("target__date_entretien").annotate(
        Count('identifier')).order_by()
    date_entre_m = Person.objects.filter(
        membre_sexe=Person.MALE).values("target__date_entretien").annotate(
        Count('identifier')).order_by()
    date_entre_f = Person.objects.filter(
        membre_sexe=Person.MALE).values("target__date_entretien").annotate(
        Count('identifier')).order_by()

    context = {"srv": srv,
               "total_target": total_target,
               "total_person": total_person,
               "total_female": total_female,
               "total_male": total_male,
               }

    return HttpResponse(template.render(context, request))


def assis_admin(request):

    template = loader.get_template('repatriate/assis_admin.html')
    user = request.user

    context = {"user": user}

    srv = Target.objects.all()
    total_target = Target.objects.all().count()
    total_person = Person.objects.all().count()
    total_male = Person.objects.filter(membre_sexe=Person.MALE).count()
    total_female = Person.objects.filter(membre_sexe=Person.FEMALE).count()

    context = {"srv": srv,
               "total_target": total_target,
               "total_person": total_person,
               "total_female": total_female,
               "total_male": total_male,
               }

    return HttpResponse(template.render(context, request))


@login_required
def target_validated(request, *args, **kwargs):
    id_url = kwargs["pk"]
    selected_target = Target.objects.get(identifier=id_url)
    selected_target.validation_status = Target.VALIDATED
    selected_target.save()
    return redirect("/home")
