# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .forms import UploadGpapForm

# Imaginary function to handle an uploaded file.
from manage_survey import ExportFormNotes,ExportGeomSurvey,spatial_join

def upload_file(request):
    submitted = False
    if request.method == 'POST':
        form = UploadGpapForm(request.POST, request.FILES)
        if form.is_valid():
            anagrafica,rilievo,errore =ExportFormNotes(request.FILES['file'])
            geom=ExportGeomSurvey(request.FILES['splite_file'])
            stampa=spatial_join(geom,rilievo)
            return HttpResponse(str(geom)+'<br><p>aa: </p>'+str(anagrafica)+
                                '<br><p>bb</p>'+str(rilievo)+
                                '<br>'+str(stampa))
    else:
        form = UploadGpapForm()
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'upload.html', {'form': form,'submitted': submitted})