# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.contrib import messages
from django.contrib.auth.models import Group
from django.views.generic import ListView
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.generic.edit import UpdateView
from djgeojson.views import GeoJSONLayerView
from django.core.mail import send_mail
from django.contrib.staticfiles import finders

from splite import make as mksplite
from .forms import DannoFormAgricoltore, UserForm, AgricoltoreForm, DannoFormCAA
from datetime import date
from django.conf import settings

from .models import danno, quadranti, catastale_new, quandranti_livorno


# Create your views here.
class ListaDomande(ListView):
    context_object_name = 'danni_lista'
    # queryset=danno.objects.all().order_by('-data_ins','id')
    template_name = "domanda/lista_domande.html"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if not self.request.user.is_superuser:
                #mostro i la lista dei danni a seconda del tipo di utente
                if self.request.user.groups.filter(name__in=['Agricoltore']).exists():
                    return danno.objects.filter(richiedente=self.request.user).order_by('-data_ins', 'id')
                if self.request.user.groups.filter(name__in=['CAA']).exists():
                    return danno.objects.filter(CAA=self.request.user).order_by('-data_ins', 'id')
                # TODO togliere le due righe sotto
                if self.request.user.groups.filter(name__in=['Rilevatore']).exists():
                    return danno.objects.filter(Rilevatore=self.request.user).order_by('-data_ins', 'id')
            else:
                return danno.objects.all().order_by('-data_ins', 'id')
        else:
            return Http404


class lista_rilievi(ListView):
    context_object_name = 'rilievi_lista'
    # queryset=danno.objects.all().order_by('-data_ins','id')
    template_name = "domanda/lista_rilievi.html"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if not self.request.user.is_superuser:
                #mostro i la lista dei danni a seconda del tipo di utente
                if self.request.user.groups.filter(name__in=['Rilevatore']).exists():
                    return danno.objects.filter(Rilevatore=self.request.user).order_by('-data_ins', 'id')
            else:
                return danno.objects.all().order_by('-data_ins', 'id')
        else:
            return Http404

@login_required
def quadrante(request,id):
    try:
        pid = int(id)
    except ValueError:
        raise Http404()
    danno_pid = danno.objects.get(id=pid)

    # variables che conservano i dati
    quad_id = []
    html_str = ''
    html_test=''
    # per ogni catastale inserito nel danno
    for i in range(danno_pid.fog_part_db.count()):
        catasto = danno_pid.fog_part_db.all()[i]
        catasto.mpoly.transform('3003')
        #prendevo i quadranti da tutta la regione
        #quad_interessati = quadranti.objects.filter(mpoly__intersects=catasto.mpoly)

        quad_interessati = quandranti_livorno.objects.filter(geom__intersects=catasto.mpoly)

        # ciclo per ogni quadtante toccato dal singolo catastale
        for quadrante in quad_interessati:
            quad_id.append(int(quadrante.num))

    # prendo i valori unici di tutti i quadranti
    quadranti_list = list(set(quad_id))
    mbtilesPathList=[]
    for qd in range(len(quadranti_list)):
        mbtilesPath = os.path.join(settings.STATIC_URL, 'mbtiles', '%d'%(quadranti_list[qd])+'.mbtiles' )
        #controllo se il file esiste
        result = finders.find('mbtiles/%d'%(quadranti_list[qd])+'.mbtiles')
        # una lista che contiene una tupla con path e quadrante
        mbtilesPathList.append((result,mbtilesPath,quadranti_list[qd]))
        # TODO: corregge il path sotto
        html_test += '<a href="%s">mbtiles %d</a>' % (mbtilesPath, quadranti_list[qd])
        html_test += '<br>'
    #return HttpResponse(html_test)
    return render(request, "domanda/lista_ortofoto.html", {'mbtilesPaths': mbtilesPathList})



@login_required
def danno_singolo(request, id):
    if request.user.is_authenticated:
        try:
            idDannoint = int(id)
        except ValueError:
            raise Http404()

        dannoid = danno.objects.filter(id=idDannoint).first()

        # controllo che solo i proprietari della domanda possono vedere i dettagli della singola domanda
        error = None
        if request.user.groups.filter(name__in=['CAA']).exists():
            if dannoid.CAA != request.user:
                error = 'Utente CAA %s non risulta proprietario della domanda a codice %s' % (
                request.user.get_username(), dannoid.id)
        else:
            if dannoid.richiedente != request.user:
                error = 'Utente %s non risulta proprietario della domanda a codice %s' % (
                request.user.get_username(), dannoid.id)

        return render(request, "domanda/domanda.html", {'danno': dannoid, 'error': error})

    else:
        return Http404()


class dannoEdit(UpdateView):
    model = danno
    fields = ('foglio', 'particella', 'coltura', 'varieta', 'SumTot',
              'SumSem', 'PercDanno', 'Produzione', 'PerProdPersa', 'ValoreDanno', 'NumPianteDan',
              'TipoPiante', 'SelvagginaSem', 'OpereProtezione')
    template_name = 'domanda/danno_update.html'

    def user_passes_test(self, request):
        if request.user.is_authenticated():
            self.object = self.get_object()
            if not self.object.CAA == request.user:
                return self.object.richiedente == request.user
        return False

    def dispatch(self, request, *args, **kwargs):
        if self.user_passes_test(request):
            return redirect('/admin/')
        return super(dannoEdit, self).dispatch(
            request, *args, **kwargs)

class MapLayer(GeoJSONLayerView):

    # Options
    precision = 4   # float
    simplify = 0.5  # generalization
    geometry_field = 'mpoly' #colonna geometrie
    properties = ['part','foglio','comune']



    def get_queryset(self):
        pk_id = self.request.GET.get('pid')
        try:
            pk_id_int = int(pk_id)
        except ValueError:
            Http404
        #reverse selection di catastale a partire dal danno
        context = catastale_new.objects.filter(danno__id=pk_id_int)
        return context

@login_required
def InserisciDanno(request):
    # controllo che sono Agricoltori possono inserire domande
    if request.user.groups.filter(name__in=['Agricoltore', 'CAA']).exists():
        error = None
        # if this is a POST request we need to process the form data
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            if request.user.groups.filter(name='Agricoltore').exists():
                form = DannoFormAgricoltore(request.POST,request.FILES)
            else:
                form = DannoFormCAA(request.POST,request.FILES)
            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                dannoEntry = form.save(commit=False)
                if request.user.groups.filter(name='Agricoltore').exists():
                    dannoEntry.richiedente = request.user
                dannoEntry.data_ins = date.today()
                if request.user.groups.filter(name__in=['CAA']).exists():
                    dannoEntry.CAA = request.user
                dannoEntry.stato_pratica = u'lavorazione'
                dannoEntry.mappale = form.cleaned_data['mappale']
                dannoEntry.save()

                #sostituito il modo per salvare le particelle con ajax per gestire molte righe
                # for item in range(len(form.cleaned_data['fog_part_certified'])):
                #     dannoEntry.fog_part_certified.add(form.cleaned_data['fog_part_certified'][item])
                # dannoEntry.save()

                for item in range(len(form.cleaned_data['fog_part_db'])):
                    pk_id = form.cleaned_data['fog_part_db'][item]
                    catastale_obj=catastale_new.objects.get(id=pk_id)
                    dannoEntry.fog_part_db.add(catastale_obj)
                dannoEntry.save()


                # redirect to a new URL:
                return HttpResponseRedirect('/domanda/%s/' % (str(dannoEntry.id)))

        # if a GET (or any other method) we'll create a blank form
        else:
            if request.user.groups.filter(name='Agricoltore').exists():
                form = DannoFormAgricoltore()
            else:
                form = DannoFormCAA()
    else:
        form = None
        error = 'Utente %s non risulta inserito tra gli Agricoltori/CAA accreditati ad inserire domande' % (
        request.user.get_username())

    return render(request, 'domanda/inserisci_danno.html', {'form': form, 'errore': error})




@login_required
@transaction.atomic
def InserisciAgricoltore(request):
    if request.user.groups.filter(name__in=['CAA']).exists():
        error = None
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            user_form = UserForm(request.POST)
            profile_form = AgricoltoreForm(request.POST)
            # check whether it's valid:
            if user_form.is_valid() and profile_form.is_valid():
                # process the data in form.cleaned_data as required
                user = user_form.save()
                user.refresh_from_db()  # This will load the Agricoltore Profile created by the Signal
                profile_form = AgricoltoreForm(request.POST,
                                               instance=user.agricoltore)  # Reload the profile form with the profile instance
                profile_form.full_clean()  # Manually clean the form this time. It is implicitly called by "is_valid()" method
                profile_form.save(commit=False)
                data = profile_form.cleaned_data.get('birth_date')
                profile_form.dataNascita = data
                user_form.save()
                profile_form.save()  # Gracefully save the form
                user.groups.add(Group.objects.get(name='Agricoltore'))
                messages.success(request, 'Your profile was successfully updated!')
                # redirect to a new URL:
                return HttpResponseRedirect('/domanda/')
            else:
                messages.error(request, 'Correggi gli errori sotto')
        else:
            user_form = UserForm()
            profile_form = AgricoltoreForm()
    else:
        user_form = None
        profile_form = None
        error = 'Utente %s non risulta inserito tra i CAA accreditati ad inserire Agricoltori' % (
        request.user.get_username())

    # return render(request, 'domanda/inserisci_agricoltore.html', {'form': form})
    return render(request, 'domanda/inserisci_agricoltore.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'errore': error
    })


@login_required
def download_sqlite(request, id):
    # TODO cancellare il file una vota scaricato
    idint = int(id)
    danno_id = danno.objects.get(id=idint)
    if danno_id.fog_part_db.count() == 0:
        messages.warning(request, 'Non puoi esportare perchè non ci sono particelle')
        return render(request, 'domanda/messaggio.html')
    else:
        richiedente = danno_id.richiedente.get_username()
        suffix = '.sqlite'
        base_filename = str(richiedente) + '_' + str(idint) + suffix
        filePath = os.path.join(settings.MEDIA_ROOT, 'splite', base_filename)
        mksplite(danno, idint, filePath)
        if os.path.exists(filePath):
            fsock = open(filePath, "rb")
        if os.path.exists(filePath + suffix):
            fsock = open(filePath + suffix, "rb")
        # cambio lo stato della pratica a rilievo
        danno_id.stato_pratica = 'rilievo'
        danno_id.save()
        response = HttpResponse(fsock, content_type='application/x-sqlite3')
        response['Content-Disposition'] = 'attachment; filename=%s' % base_filename
        return response
