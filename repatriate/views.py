# from django.shortcuts import render

import xlwt

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.db.models import Count
from django.template import loader
from django.contrib import messages
from django.utils import timezone

from rolepermissions.checkers import has_role

from OIMDesk.roles import (
    DeskAssistantAdmin, DNDSTech, SuperAdmin, DeskControle)
from desk.models import Provider
from repatriate.forms import (SearchForm, SearchFormPerPeriod, TargetForm,
                              FixedPersonForm)
from repatriate.models import (Person, Target, DuplicateProgresMenage,
                               RegistrationSiteProvider)


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
        'categories': [i.get('target__date_entretien').strftime(
            '%d-%b-%y') for i in date_entre],
        'text': "Nombre de retourné",
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
               "menage_per_prov": menage_per_prov,
               "menage_per_date_entrtien": menage_per_date_entrtien,
               "total_target": total_target,
               "total_person": total_person,
               "total_female": total_female,
               "total_male": total_male,
               "per_lieu_region": per_lieu_region
               }

    nb_menage = srv.count()
    pn = Person.objects.all()
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
def desk_controle(request):

    template = loader.get_template('repatriate/desk_controle.html')

    prov = Provider.objects.get(username=request.user.username)
    sites = [rs.site.slug for rs in RegistrationSiteProvider.objects.filter(
        provider=prov)]
    context = {"user": prov}
    if has_role(prov, [DeskAssistantAdmin, SuperAdmin, DNDSTech]):
        srv = Target.active_objects.all()
        pn = Person.active_objects.all()
        d_progres_m = DuplicateProgresMenage.not_fix_objects.all()
        context.update({'d_progres_m': d_progres_m})
    elif has_role(prov, [DeskControle]):
        srv = Target.active_objects.filter(site_engistrement__in=sites)
        pn = Person.active_objects.filter(target__site_engistrement__in=sites)
    else:
        return redirect('/')

    if request.method == 'POST' and '_per_Date' in request.POST:
        period_form = SearchFormPerPeriod(request.POST or None)
        date_s = request.POST.get('start_date').replace("/", "-")
        date_e = request.POST.get('end_date').replace("/", "-")
        return redirect("export-xls/{start}/{end}".format(
            start=date_s, end=date_e))
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
    sans_doc_avec_num_pi = pn.filter(is_sans_doc_avec_num_pi=True)
    requise_num_progres_menage = srv.filter(is_requise_num_progres_menage=True)
    invalide_num_progres_menage = srv.filter(is_invalide_num_progres_menage=True)
    invalide_num_tel = srv.filter(is_invalide_num_tel=True)
    not_empty_num_progres_menage_alg = srv.filter(is_not_empty_num_progres_menage_alg=True)
    no_doc_with_num_pm = srv.filter(is_no_doc_with_num_pm=True)
    site_not_existe = srv.filter(is_site_not_existe=True)

    context.update({
        'invalide_num_pi': invalide_num_pi,
        'num_pi_sans_num_pm': num_pi_sans_num_pm,
        'not_empty_num_pi_alg': not_empty_num_pi_alg,
        'vrf_wihtout_num_pi': vrf_wihtout_num_pi,
        'sans_doc_avec_num_pi': sans_doc_avec_num_pi,
        'requise_num_progres_menage': requise_num_progres_menage,
        'invalide_num_progres_menage': invalide_num_progres_menage,
        'invalide_num_tel': invalide_num_tel,
        'not_empty_num_progres_menage_alg': not_empty_num_progres_menage_alg,
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
def person_correction(request, *args, **kwargs):

    template = loader.get_template('repatriate/fixed_person.html')
    context = {}

    id_url = kwargs["id"]
    selected_person = Person.objects.get(identifier=id_url)
    person_form = FixedPersonForm(request.POST or None, instance=selected_person)
    if request.method == 'POST' and '_fixed_person' in request.POST:
        if person_form.is_valid():
            person_form.save()
            messages.success(request, '{} a été corrigé avec succès'.format(
                selected_person))
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
            messages.success(request, 'Corrigé avec succès')
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


@login_required
def end_merge_target(request, *args, **kwargs):
    identifier = kwargs["id"]
    tgt = Target.active_objects.get(identifier=identifier)
    dup = DuplicateProgresMenage.not_fix_objects.get(new_target=tgt)
    dup.fixed_by = Provider.objects.get(username=request.user.username)
    dup.fix_date = timezone.datetime.now()
    dup.fixed = True
    dup.save()
    target = dup.new_target
    target.delete()
    for m in target.get_membres():
        m.delete()
    messages.success(request, 'a été add avec succès')
    return redirect('controle')


@login_required
def merge_add(request, *args, **kwargs):
    identifier = kwargs["id"]
    pn = Person.active_objects.get(identifier=identifier)
    dup = DuplicateProgresMenage.not_fix_objects.get(new_target=pn.target)
    # old_pn = dup.old_target
    pn.target = dup.old_target
    pn.save()
    messages.success(request, 'a été add avec succès')

    return redirect('merge_manager', id=dup.id)


@login_required
def merge_update(request, *args, **kwargs):
    identifier = kwargs["id"]
    new_pn = Person.active_objects.get(identifier=identifier)
    dup = DuplicateProgresMenage.not_fix_objects.get(new_target=new_pn.target)
    old_pn = dup.old_target
    # Supression du remplacer.
    for u in old_pn.get_membres():
        if u.num_progres_individuel == new_pn.num_progres_individuel:
            new_pn.target = old_pn
            new_pn.save()
            u.deleted = True
            u.save()
            messages.success(request, '{} a été update avec succès'.format(new_pn))
            break

    return redirect('merge_manager', id=dup.id)


@login_required
def merge_manager(request, *args, **kwargs):
    context = {}
    template = loader.get_template('repatriate/gestion_merge.html')
    slug = kwargs["id"]
    d_progres_m = DuplicateProgresMenage.not_fix_objects.get(id=slug)
    target = d_progres_m.new_target
    target_old = d_progres_m.old_target
    context.update({"target": target, "target_old": target_old})
    return HttpResponse(template.render(context, request))


def get_date(date):
    if date:
        date = date.strftime("%Y/%m/%d")
    return date


def date_format(strdate):
    return timezone.datetime.strptime(strdate, '%d-%m-%Y')


def get_sex(value):
    return "M" if value == "male" else "F"


@login_required
def export_xls(request, *args, **kwargs):

    start = date_format(kwargs["start"])
    end = date_format(kwargs["end"])
    prov = Provider.objects.get(username=request.user.username)
    if has_role(prov, [DeskControle]):
        sites = [rs.site.slug for rs in RegistrationSiteProvider.objects.filter(provider=prov)]
        pn = Person.active_objects.filter(target__site_engistrement__in=sites)
    if has_role(prov, [DeskAssistantAdmin, SuperAdmin, DNDSTech]):
        pn = Person.active_objects.all()
    else:
        redirect('/')

    pn = pn.filter(target__date_entretien__gte=start, target__date_entretien__lte=end)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="export brute retournés.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = [
        'identifier',
        'nom_agent',
        'num_enregistrement',
        'site_engistrement',
        'date_arrivee',
        'date_entretien',
        'continent_asile',
        'pays_asile',
        'ville_asile',
        'camp',
        'num_progres_menage',
        'point_de_entree',
        'continent_naissance',
        'pays_naissance',
        'lieu_naissance',
        'chef_etat_civil',
        'chef_profession',
        'chef_doc',
        'num_doc',
        'beneficiez_lassistance',
        'actuelle_region',
        'actuelle_cercle',
        'actuelle_commune',
        'actuelle_qvf',
        'actuelle_nom_generale_utilise',
        'rue',
        'porte',
        'tel',
        'abris',
        'nature_construction',
        'type_hebergement',
        'membre_pays',
        'nbre_membre_reste',
        'etat_sante',
        'situation_maladie',
        'type_maladie',
        'type_aigue',
        'prise_medicament',
        'type_medicaments',
        'suivi_formation',
        'domaine_formation',
        'metier_pays_prove',
        'exercice_secteur',
        'formation_socio_prof',
        'secteur_prof',
        'projet_activite',
        'type_projet',
        'souhait_activite',
        'lieu_region',
        'lieu_cercle',
        'lieu_commune',
        'lieu_qvf',
        'lieu_non_generale_utilise',
        'num_progres_individuel'
    ]
    # columns = [f.name for f in Target._meta.get_fields()] + [
    #     f.name for f in Person._meta.get_fields()]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    for row in pn:
        row_num += 1
        col_num = 0
        ws.write(row_num, col_num, row.target.identifier, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.nom_agent, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.num_enregistrement, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.site_engistrement.name, font_style)
        col_num += 1
        ws.write(row_num, col_num, get_date(row.target.date_arrivee), font_style)
        col_num += 1
        ws.write(row_num, col_num, get_date(row.target.date_entretien), font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.continent_asile, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.pays_asile, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.ville_asile, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.camp, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.num_progres_menage, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.point_de_entree, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.continent_naissance, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.pays_naissance, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.lieu_naissance, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.chef_etat_civil, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.chef_profession, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.chef_doc, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.num_doc, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.beneficiez_lassistance, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.actuelle_region, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.actuelle_cercle, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.actuelle_commune, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.actuelle_qvf, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.actuelle_nom_generale_utilise, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.rue, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.porte, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.tel, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.abris, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.nature_construction, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.type_hebergement, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.membre_pays, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.nbre_membre_reste, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.etat_sante, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.situation_maladie, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.type_maladie, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.type_aigue, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.prise_medicament, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.type_medicaments, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.suivi_formation, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.domaine_formation, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.metier_pays_prove, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.exercice_secteur, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.formation_socio_prof, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.secteur_prof, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.projet_activite, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.type_projet, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.souhait_activite, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.lieu_region, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.lieu_cercle, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.lieu_commune, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.lieu_qvf, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.target.lieu_non_generale_utilise, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.num_progres_individuel, font_style)
        col_num += 1
        # break
    wb.save(response)

    return response
