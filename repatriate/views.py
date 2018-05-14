# from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.db.models import Count
from django.template import loader
from django.contrib import messages

from rolepermissions.checkers import has_role

from OIMDesk.roles import (
    DeskAssistantAdmin, DNDSTech, DeskAdmin, DeskControle)
from desk.models import Provider
from repatriate.forms import (SearchForm, SearchFormPerPeriod, TargetForm,
                              FixedPersonForm)
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
        membre_sexe=Person.FEMALE).values("target__date_entretien").annotate(
        Count('identifier')).order_by()

    per_lieu_region = {
        'labels': [i.get('target__lieu_region') for i in per_lieu_regions],
        'label': "Région de retour",
        'title': "",
        'data': [i.get('id__count') for i in per_lieu_regions]
    }
    menage_per_prov = {
        'labels': [i.get('point_de_entree').title() for i in s],
        'label': "Nombre de retourné",
        'title': "",
        'data': [i.get('instance_id__count') for i in s]
    }
    menage_per_date_entrtien = {
        'categories': [i.get('target__date_entretien').strftime('%d-%b-%y') for i in date_entre],
        'text': "Nombre de retourné",
        'title': "Nombre total retourné par date arrivée.",
        'type': "line",
        'series': [
            {"name": "Total", "data": [i.get('identifier__count') for i in date_entre]},
            {"name": "Total homme", "data": [i.get('identifier__count') for i in date_entre_m]},
            {"name": "Total femme", "data": [i.get('identifier__count') for i in date_entre_f]}]
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


@login_required
def desk_controle(request):

    template = loader.get_template('repatriate/desk_controle.html')

    prov = Provider.objects.get(username=request.user.username)

    if has_role(prov, [DeskControle]):
        srv = Target.active_objects.filter(site_engistrement=prov.site)
        pn = Person.active_objects.filter(target__site_engistrement=prov.site)
    if has_role(prov, [DeskAssistantAdmin, DeskAdmin, DNDSTech]):
        srv = Target.active_objects.all()
        pn = Person.active_objects.all()
    else:
        redirect('/')

    context = {"user": prov}

    if request.method == 'POST' and '_per_Date' in request.POST:
        period_form = SearchFormPerPeriod(request.POST or None)
        if period_form.is_valid():
            print("VALIDATED DATE FILTER")
            return redirect("/")
    else:
        period_form = SearchFormPerPeriod()
    context.update({'period_form': period_form})

    search_form = SearchForm(request.POST or None)
    result = ""
    result_not_found = ""
    if request.method == 'POST' and '_search' in request.POST:
        print("search")
        if search_form.is_valid():
            result = search_form.get_result('num_progres_individuel')
            if not result:
                print("Not found")
                result_not_found = "Aucun numéro ne correspond"
    context.update({'result_not_found': result_not_found,
                    'search_form': search_form, 'msg_result': result})

    invalide_num_pi = pn.filter(is_invalide_num_pi=True)
    num_pi_sans_num_pm = pn.filter(is_num_pi_sans_num_pm=True)
    not_empty_num_pi_alg = pn.filter(is_not_empty_num_pi_alg=True)
    vrf_wihtout_num_pi = pn.filter(is_vrf_wihtout_num_pi=True)
    suspect_new_member = pn.filter(is_suspect_new_member=True)
    suspect_update_member = pn.filter(is_suspect_update_member=True)
    sans_doc_avec_num_pi = pn.filter(is_sans_doc_avec_num_pi=True)
    zero_member = srv.filter(is_zero_member=True)
    requise_num_progres_menage = srv.filter(is_requise_num_progres_menage=True)
    invalide_num_progres_menage = srv.filter(is_invalide_num_progres_menage=True)
    invalide_num_tel = srv.filter(is_invalide_num_tel=True)
    not_empty_num_progres_menage_alg = srv.filter(is_not_empty_num_progres_menage_alg=True)
    many_chef_menage = srv.filter(is_many_chef_menage=True)
    no_chef_manage = srv.filter(is_no_chef_manage=True)
    no_doc_with_num_pm = srv.filter(is_no_doc_with_num_pm=True)
    site_not_existe = srv.filter(is_site_not_existe=True)

    context.update({
        'invalide_num_pi': invalide_num_pi,
        'num_pi_sans_num_pm': num_pi_sans_num_pm,
        'not_empty_num_pi_alg': not_empty_num_pi_alg,
        'vrf_wihtout_num_pi': vrf_wihtout_num_pi,
        'suspect_new_member': suspect_new_member,
        'suspect_update_member': suspect_update_member,
        'sans_doc_avec_num_pi': sans_doc_avec_num_pi,
        'zero_member': zero_member,
        'requise_num_progres_menage': requise_num_progres_menage,
        'invalide_num_progres_menage': invalide_num_progres_menage,
        'invalide_num_tel': invalide_num_tel,
        'not_empty_num_progres_menage_alg': not_empty_num_progres_menage_alg,
        'many_chef_menage': many_chef_menage,
        'no_chef_manage': no_chef_manage,
        'no_doc_with_num_pm': no_doc_with_num_pm,
        'site_not_existe': site_not_existe,
    })

    nb_menage = srv.count()
    nb_person = pn.count()
    nb_person_f = pn.filter(membre_sexe=Person.FEMALE).count()
    nb_person_m = pn.filter(membre_sexe=Person.MALE).count()

    pn_0_4 = pn.filter(membre_age__lte=4)
    pn_5_11 = pn.filter(membre_age__gte=5, membre_age__lte=11)
    pn_12_17 = pn.filter(membre_age__gte=12, membre_age__lte=17)
    pn_18_59 = pn.filter(membre_age__gte=18, membre_age__lte=59)
    pn_plus60 = pn.filter(membre_age__gte=60)

    pn_0_4_count_m = pn_0_4.filter(membre_sexe=Person.MALE).count()
    pn_0_4_count_f = pn_0_4.filter(membre_sexe=Person.FEMALE).count()
    pn_0_4_count = pn_0_4_count_m + pn_0_4_count_f
    pn_5_11_count_m = pn_5_11.filter(membre_sexe=Person.MALE).count()
    pn_5_11_count_f = pn_5_11.filter(membre_sexe=Person.FEMALE).count()
    pn_5_11_count = pn_5_11_count_m + pn_5_11_count_f
    pn_12_17_count_m = pn_12_17.filter(membre_sexe=Person.MALE).count()
    pn_12_17_count_f = pn_12_17.filter(membre_sexe=Person.FEMALE).count()
    pn_12_17_count = pn_12_17_count_f + pn_12_17_count_m
    pn_18_59_count_m = pn_18_59.filter(membre_sexe=Person.MALE).count()
    pn_18_59_count_f = pn_18_59.filter(membre_sexe=Person.FEMALE).count()
    pn_18_59_count = pn_18_59_count_f + pn_18_59_count_m
    plus60_count_m = pn_plus60.filter(membre_sexe=Person.MALE).count()
    plus60_count_f = pn_plus60.filter(membre_sexe=Person.FEMALE).count()
    plus60_count = plus60_count_f + plus60_count_m

    context.update({
        "srv": srv,
        "pn_0_4_count_m": pn_0_4_count_m,
        "pn_0_4_count_f": pn_0_4_count_f,
        "pn_0_4_count": pn_0_4_count,
        "pn_5_11_count_m": pn_5_11_count_m,
        "pn_5_11_count_f": pn_5_11_count_f,
        "pn_5_11_count": pn_5_11_count,
        "pn_12_17_count_m": pn_12_17_count_m,
        "pn_12_17_count_f": pn_12_17_count_f,
        "pn_12_17_count": pn_12_17_count,
        "pn_18_59_count_m": pn_18_59_count_m,
        "pn_18_59_count_f": pn_18_59_count_f,
        "pn_18_59_count": pn_18_59_count,
        "plus60_count_m": plus60_count_m,
        "plus60_count_f": plus60_count_f,
        "plus60_count": plus60_count,
        "nb_menage": nb_menage,
        "nb_person": nb_person,
        "nb_person_m": nb_person_m,
        "nb_person_f": nb_person_f,
    })

    return HttpResponse(template.render(context, request))


@login_required
def desk_monitoring(request):

    template = loader.get_template('repatriate/desk_monitoring.html')
    user = request.user

    context = {"user": user}

    prov = Provider.objects.get(username=request.user.username)

    if has_role(prov, [DeskAdmin, DNDSTech, DeskAssistantAdmin]):
        srv = Target.active_objects.all()
        pn = Person.active_objects.all()
    else:
        redirect('/')

    invalide_num_pi = pn.filter(is_invalide_num_pi=True)
    num_pi_sans_num_pm = pn.filter(is_num_pi_sans_num_pm=True)
    not_empty_num_pi_alg = pn.filter(is_not_empty_num_pi_alg=True)
    vrf_wihtout_num_pi = pn.filter(is_vrf_wihtout_num_pi=True)
    suspect_new_member = pn.filter(is_suspect_new_member=True)
    suspect_update_member = pn.filter(is_suspect_update_member=True)
    sans_doc_avec_num_pi = pn.filter(is_sans_doc_avec_num_pi=True)
    zero_member = srv.filter(is_zero_member=True)
    requise_num_progres_menage = srv.filter(is_requise_num_progres_menage=True)
    invalide_num_progres_menage = srv.filter(is_invalide_num_progres_menage=True)
    invalide_num_tel = srv.filter(is_invalide_num_tel=True)
    not_empty_num_progres_menage_alg = srv.filter(is_not_empty_num_progres_menage_alg=True)
    many_chef_menage = srv.filter(is_many_chef_menage=True)
    no_chef_manage = srv.filter(is_no_chef_manage=True)
    no_doc_with_num_pm = srv.filter(is_no_doc_with_num_pm=True)
    site_not_existe = srv.filter(is_site_not_existe=True)

    context.update({
        'invalide_num_pi': invalide_num_pi,
        'num_pi_sans_num_pm': num_pi_sans_num_pm,
        'not_empty_num_pi_alg': not_empty_num_pi_alg,
        'vrf_wihtout_num_pi': vrf_wihtout_num_pi,
        'suspect_new_member': suspect_new_member,
        'suspect_update_member': suspect_update_member,
        'sans_doc_avec_num_pi': sans_doc_avec_num_pi,
        'zero_member': zero_member,
        'requise_num_progres_menage': requise_num_progres_menage,
        'invalide_num_progres_menage': invalide_num_progres_menage,
        'invalide_num_tel': invalide_num_tel,
        'not_empty_num_progres_menage_alg': not_empty_num_progres_menage_alg,
        'many_chef_menage': many_chef_menage,
        'no_chef_manage': no_chef_manage,
        'no_doc_with_num_pm': no_doc_with_num_pm,
        'site_not_existe': site_not_existe,
    })

    return HttpResponse(template.render(context, request))


@login_required
def person_correction(request, *args, **kwargs):

    template = loader.get_template('repatriate/fixed_person.html')
    context = {}

    id_url = kwargs["id"]
    selected_person = Person.objects.get(identifier=id_url)
    person_form = FixedPersonForm(request.POST or None, instance=selected_target)
    if request.method == 'POST' and '_fixed_target' in request.POST:
        if person_form.is_valid():
            # notice = person_form.save(commit=False)
            # notice.author = Person.objects.filter()
            person_form.save()
            messages.success(request, 'Error message here')
            return redirect("/repatriate/desk-controle")
    context.update({'selected_person': selected_person, 'person_form': person_form})

    return HttpResponse(template.render(context, request))


@login_required
def target_correction(request, *args, **kwargs):
    template = loader.get_template('repatriate/fixed_target.html')

    context = {}
    id_url = kwargs["id"]
    selected_target = Target.objects.get(identifier=id_url)

    target_form = TargetForm(request.POST or None, instance=selected_target)
    if request.method == 'POST' and '_fixed_target' in request.POST:
        if target_form.is_valid():
            target_form.save()

            messages.success(request, 'Modifier avec succès')
            return redirect("/repatriate/desk-controle")
    context.update({'selected_target': selected_target, 'target_form': target_form})

    return HttpResponse(template.render(context, request))


@login_required
def target_validated(request, *args, **kwargs):
    id_url = kwargs["pk"]
    selected_target = Target.objects.get(identifier=id_url)
    selected_target.validation_status = Target.VALIDATED
    selected_target.save()
    return redirect("/home")
