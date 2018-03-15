# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .forms import UploadGpapForm

# Imaginary function to handle an uploaded file.
from manage_gpap import ExportFormNotes

def upload_file(request):
    submitted = False
    if request.method == 'POST':
        form = UploadGpapForm(request.POST, request.FILES)
        if form.is_valid():
            aa,bb=ExportFormNotes(request.FILES['file'])
            return HttpResponse(str(aa)+'<br>'+str(bb))
    else:
        form = UploadGpapForm()
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'upload.html', {'form': form,'submitted': submitted})