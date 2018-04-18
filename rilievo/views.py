# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from djgeojson.views import GeoJSONLayerView
from domanda.models import danno

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render

from rilievo.models import rilievo_poly,anagrafica
from .forms import UploadGpapForm

# Imaginary function to handle an uploaded file.
from manage_survey import ExportFormNotes, ExportGeomSurvey, spatial_join



# Create your views here.
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
            stampa = spatial_join(geom, rilievo,id_danno)
            return HttpResponse(str(geom) + '<br><p>anagrafica: </p>' + str(anagrafica) +
                                '<br><p>rilievo</p>' + str(rilievo) +
                                '<br><p>spatial join: </p><br>' + str(stampa))
    else:
        form = UploadGpapForm()
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'upload.html', {'form': form, 'submitted': submitted,'iddanno':str(id_danno)})


@login_required
def mostra_rilievi(request):
    #solo i rilevatori vedono la pagina
    if request.user.groups.filter(name__in=['Rilevatore']).exists():
       mostra=True
       danniRilevatore = danno.objects.filter(Rilevatore=request.user, stato_pratica='rilievo').order_by('-data_ins', 'id')
       danniRilevatoreNonInseribili = danno.objects.filter(Rilevatore=request.user, stato_pratica='lavorazione').order_by('-data_ins',
                                                                                                         'id')
    else:
        mostra=False

    return render(request, "rilievi.html",{'mostra':mostra,'danniRilevatore':danniRilevatore,'pratichenoninseribili':danniRilevatoreNonInseribili})


def mostra_singolo_rilievo(request,id):
    try:
        id_danno = int(id)
    except ValueError:
        raise Http404()

    #estraggo tutti i dati che mi servono

    rilievi_pratica = rilievo_poly.objects.filter(id_pratica__id=id_danno)
    anagrafica_pratica = anagrafica.objects.filter(id_pratica__id=id_danno)
    if len(anagrafica_pratica) !=1:
        anagrafica_pratica=anagrafica_pratica[0]

    anagrafica_pratica = anagrafica_pratica.first()
    domanda = anagrafica_pratica.id_pratica
    error=False

    #TODO togliere first a rilievi_pratica e fare il loop nel template

    return render(request, "rilievo_singolo.html", {'anagrafica': anagrafica_pratica,'rilievo':rilievi_pratica.first() ,'error': error})






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