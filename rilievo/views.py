# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views.generic import ListView
from djgeojson.views import GeoJSONLayerView
from domanda.models import danno

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render

from shape_engine.shape_responder import ShpResponder

from rilievo.models import rilievo_poly,anagrafica,prezzo
from .WriteToExcel import ReportColturaExcel, ReportAggregatoSpeciePeriziati, \
    ReportPeriziatiAgricoltoreSpecie,ReportAggregatoColturaPeriziati
from .forms import UploadGpapForm,prezzoColturaForm

#report
from reports import report_singolo,report_singolo_platypus


# Imaginary function to handle an uploaded file.
from manage_survey import ExportFormNotes, ExportGeomSurvey, spatial_join



# Create your views here.
@login_required
def upload_file(request,id):
    try:
        id_danno = int(id)
    except ValueError:
        raise Http404()
    submitted = False
    if request.method == 'POST':
        form = UploadGpapForm(request.POST, request.FILES)
        if form.is_valid():
            anagrafica, rilievo, errore = ExportFormNotes(request.FILES['file'],id_danno)
            geom = ExportGeomSurvey(request.FILES['splite_file'])
            #la funzione spatial_join si occupa anche di salvare i dati in db per questo non serve salvare il form
            stampa = spatial_join(geom, rilievo,id_danno)
            #cambio lo stato della pratica a completa
            danno_id = danno.objects.get(id=id_danno)
            danno_id.stato_pratica = 'completa'
            danno_id.save()
            return render(request, 'success_upload.html', {'iddanno': str(id_danno) })
            # return HttpResponse(str(geom) + '<br><p>anagrafica: </p>' + str(anagrafica) +
            #                     '<br><p>rilievo</p>' + str(rilievo) +
            #                     '<br><p>spatial join: </p><br>' + str(stampa))
    else:
        form = UploadGpapForm()
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'uploadRilievo.html', {'form': form, 'submitted': submitted,'iddanno':str(id_danno)})

@login_required
def upgradePrezzo(request):
    if request.user.is_staff:
        submitted = False
        if request.method == "POST":
            form = prezzoColturaForm(request.POST)
            if form.is_valid():
                model_instance = form.save(commit=False)
                model_instance.save()
                return render(request, 'success_prezzo.html')

        else:
            form = prezzoColturaForm()
            if 'submitted' in request.GET:
                submitted = True

        return render(request, "uploadPrezzo.html", {'form': form,'submitted': submitted})
    else:
        raise PermissionDenied


@login_required
def mostra_rilievi(request):
    #solo i rilevatori vedono la pagina
    if request.user.groups.filter(name__in=['Rilevatore']).exists():
       mostra=True
       danniRilevatore = danno.objects.filter(Rilevatore=request.user, stato_pratica='rilievo').order_by('-data_ins', 'id')
       danniRilevatoreComplete = danno.objects.filter(Rilevatore=request.user, stato_pratica='completa').order_by('-data_ins', 'id')
       danniRilevatoreNonInseribili = danno.objects.filter(Rilevatore=request.user, stato_pratica='lavorazione').order_by('-data_ins','id')
       return render(request, "rilievi.html", {'mostra': mostra, 'danniRilevatore': danniRilevatore,
                                               'pratichenoninseribili': danniRilevatoreNonInseribili,
                                               'pratichecompletate': danniRilevatoreComplete})

    else:
        mostra=False
        return render(request, "rilievi.html",{'mostra':mostra})

@login_required
def mostra_singolo_rilievo(request,id):
    try:
        id_danno = int(id)
    except ValueError:
        raise Http404()

    #estraggo tutti i dati che mi servono

    rilievi_pratica = rilievo_poly.objects.filter(id_pratica__id=id_danno)
    anagrafica_pratica = anagrafica.objects.filter(id_pratica__id=id_danno)
    if anagrafica_pratica.count() >1:
        anagrafica_pratica=anagrafica_pratica[0]
    else:
        anagrafica_pratica = anagrafica_pratica.first()
    #domanda = anagrafica_pratica.id_pratica
    error=False

    return render(request, "rilievo_singolo.html", {'anagrafica': anagrafica_pratica,'rilievi':rilievi_pratica ,'error': error})

# Create your views here.
class lista_reports(ListView):
    context_object_name = 'danni_lista'
    # queryset=danno.objects.all().order_by('-data_ins','id')
    template_name = "lista_reports.html"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if not self.request.user.is_superuser:
                #mostro i la lista dei danni a seconda del tipo di utente
                if self.request.user.groups.filter(name__in=['Agricoltore']).exists():
                    return danno.objects.filter(richiedente=self.request.user,stato_pratica='completa').order_by('-data_ins', 'id')
                if self.request.user.groups.filter(name__in=['CAA']).exists():
                    return danno.objects.filter(CAA=self.request.user,stato_pratica='completa').order_by('-data_ins', 'id')
                # TODO togliere le due righe sotto
                if self.request.user.groups.filter(name__in=['Rilevatore']).exists():
                    return danno.objects.filter(Rilevatore=self.request.user,stato_pratica='completa').order_by('-data_ins', 'id')
            else:
                return danno.objects.filter(stato_pratica='completa').order_by('-data_ins', 'id')
        else:
            return Http404

@login_required
def exportConsuntivoTotaleAgricoltoreColtura(request):
    '''
    vista relativa a Colsultivo Agrocoltore coltura o Consuntivo per coltura
    '''

    if request.user.groups.filter(name='CAA').exists():
        # si tratta di un caa
        rilievi_eseguiti=rilievo_poly.objects.filter(id_pratica__CAA=request.user)
    elif request.user.groups.filter(name='Rilevatore').exists():
        rilievi_eseguiti=rilievo_poly.objects.filter(id_pratica__Rilevatore=request.user)
    elif request.user.groups.filter(name='Agricoltore').exists():
        rilievi_eseguiti=rilievo_poly.objects.filter(id_pratica__richiedente=request.user)
    elif request.user.is_staff or request.user.groups.filter(name='atc-admin').exists():
        rilievi_eseguiti = rilievo_poly.objects.all()
    else:
         return Http404

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Consuntivo_Totale_Agricoltore_Coltura.xlsx'
    # xlsx_data = WriteToExcel(weather_period, town)
    xlsx_data = ReportColturaExcel(rilievi_eseguiti)
    response.write(xlsx_data)
    return response

@login_required
def exportConsuntivoTotaleRichiestiPeriziatiColtura(request):
    if request.user.groups.filter(name='CAA').exists():
        # si tratta di un caa
        rilievi_eseguiti=rilievo_poly.objects.filter(id_pratica__CAA=request.user)

    elif request.user.groups.filter(name='Rilevatore').exists():
        rilievi_eseguiti=rilievo_poly.objects.filter(id_pratica__Rilevatore=request.user)
    elif request.user.groups.filter(name='Agricoltore').exists():
        rilievi_eseguiti=rilievo_poly.objects.filter(id_pratica__richiedente=request.user)
    elif request.user.is_staff or request.user.groups.filter(name='atc-admin').exists():
        rilievi_eseguiti = rilievo_poly.objects.all()
    else:
         return Http404
    prezzi= prezzo.objects.all()
    response = HttpResponse(content_type='application/vnd.ms-excel')

    # xlsx_data = WriteToExcel(weather_period, town)
    response['Content-Disposition'] = 'attachment; filename=Consuntivo Totale per Coltura.xls'
    xlsx_data = ReportAggregatoColturaPeriziati(rilievi_eseguiti, prezzi)

    response.write(xlsx_data)
    return response

@login_required
def exportConsuntivoTotaleRichiestiPeriziatiSpecie(request,comune=False):
    '''
    pulsante #2
    vista relativa a Report per Agricoltore -> Comune -> Specie -> Coltura
    e all'aggregato in caso comune=True a:
        Consuntivo specie
    '''

    if request.user.groups.filter(name='CAA').exists():
        # si tratta di un caa
        rilievi_eseguiti=rilievo_poly.objects.filter(id_pratica__CAA=request.user)

    elif request.user.groups.filter(name='Rilevatore').exists():
        rilievi_eseguiti=rilievo_poly.objects.filter(id_pratica__Rilevatore=request.user)
    elif request.user.groups.filter(name='Agricoltore').exists():
        rilievi_eseguiti=rilievo_poly.objects.filter(id_pratica__richiedente=request.user)
    elif request.user.is_staff or request.user.groups.filter(name='atc-admin').exists():
        rilievi_eseguiti = rilievo_poly.objects.all()

    # rilievi_eseguiti = rilievo_poly.objects.get(id_pratica__richiedente=request.user)
    #todo correggere sopra con l'utente
    # rilievi_eseguiti = rilievo_poly.objects.all()
    prezzi= prezzo.objects.all()
    response = HttpResponse(content_type='application/vnd.ms-excel')

    # xlsx_data = WriteToExcel(weather_period, town)
    if comune:
        response['Content-Disposition'] = 'attachment; filename=Consuntivo Totale per Agricoltore-Comune-Specie-Coltura.xls'
        xlsx_data = ReportPeriziatiAgricoltoreSpecie(rilievi_eseguiti)
    else:
        response['Content-Disposition'] = 'attachment; filename=Consuntivo_Totale_per Specie.xlsx'
        xlsx_data = ReportAggregatoSpeciePeriziati(rilievi_eseguiti, prezzi)
    response.write(xlsx_data)
    return response

@login_required
def exportShp(request,id):
    try:
        id_danno = int(id)
    except ValueError:
        raise Http404()
    from rilievo.models import rilievo_poly as rilievo_geomodel
    w = rilievo_geomodel.objects.filter(id_pratica__id=id_danno)
    # w = quadranti.objects.all()
    shp_response = ShpResponder(w)
    shp_response.file_name = w.first().id_pratica.author_full_name()
    return shp_response()

@login_required
def exportAllShp(request):
    from rilievo.models import rilievo_poly as rilievo_geomodel
    w = rilievo_geomodel.objects.all()
    # w = quadranti.objects.all()
    shp_response = ShpResponder(w)
    shp_response.file_name = 'Complessivo shapefiles'
    return shp_response()


def help_rilievo(request):
    return render(request,"help.html")

@login_required
def report_rilievo_singolo(request,id):
    try:
        id_danno = int(id)
    except ValueError:
        raise Http404()

    #prendo i dati dei rilievi
    rilievi_pratica = rilievo_poly.objects.filter(id_pratica__id=id_danno)
    anagrafica_pratica = anagrafica.objects.filter(id_pratica__id=id_danno)
    anagrafica_pratica = anagrafica_pratica.first()

    #get data for reports
    nome =anagrafica_pratica.id_pratica.richiedente.first_name
    cognome = anagrafica_pratica.id_pratica.richiedente.last_name
    agricoltore = anagrafica_pratica.id_pratica.richiedente.agricoltore
    danno=anagrafica_pratica.id_pratica

    if danno.stato_pratica == 'completa':
        # rea il pdf solo per le pratiche complete
        #create the Httpresponse object with teh appropriate PDF using platypus
        pdf = report_singolo_platypus(id_danno,nome,cognome,agricoltore,danno,anagrafica_pratica,rilievi_pratica)

        return pdf
    else:
        HttpResponse('Non si genera il report di questa pratiche non completa')


class MapLayer(GeoJSONLayerView):

    # Options
    precision = 4   # float
    simplify = 0.5  # generalization
    geometry_field = 'mpoly' #colonna geometrie
    properties = ['particelle','foglio','comune']



    def get_queryset(self):
        pk_id = self.request.GET.get('pid')
        try:
            pk_id_int = int(pk_id)
        except ValueError:
            Http404
        #reverse selection di rilievo a partire dal danno
        context = rilievo_poly.objects.filter(id_pratica__id=pk_id_int)
        return context