from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import upload_file, mostra_rilievi,mostra_singolo_rilievo,MapLayer,help_rilievo,report_rilievo_singolo,lista_reports,\
        exportConsuntivoTotaleAgricoltoreColtura,exportConsuntivoTotaleRichiestiPeriziatiSpecie,exportShp,\
    exportConsuntivoTotaleRichiestiPeriziatiColtura,exportAllShp, upgradePrezzo
from .models import rilievo_poly

urlpatterns = [
        url(r'^inserisci/(?P<id>\d+)$', upload_file, name='upload_file'),
        url(r'^inserisci/prezzo/$', upgradePrezzo, name='upload_prezzo'),
        url(r'^mostra/(?P<id>\d+)$', mostra_singolo_rilievo, name='rilievo_singolo'),
        url(r'^report/consagriccolt/$', exportConsuntivoTotaleAgricoltoreColtura, name='consuntivo-agricoltore-coltura'),
        url(r'^report/consspecie.(?P<comune>\w+)/$', exportConsuntivoTotaleRichiestiPeriziatiSpecie,
            name='consuntivo-specie-comune'),
        url(r'^report/consspecie/$', exportConsuntivoTotaleRichiestiPeriziatiSpecie,
            name='consuntivo-specie'),
        url(r'^report/conscoltura/$', exportConsuntivoTotaleRichiestiPeriziatiColtura,
            name='consuntivo-coltura'),
        url(r'^downloadshp/(?P<id>\d+)$', exportShp,name='shape_rilievo_singolo'),
        url(r'^downloadAllshp/$', exportAllShp,name='shape_tutti_rilievi'),
        url(r'^report/(?P<id>\d+)$', report_rilievo_singolo, name='report_rilievo_singolo'),
        url(r'^reports/$',login_required(lista_reports.as_view()),name='list_reports'),
        url(r'^help/$',help_rilievo,name='help_rilievo'),
        url(r'^rilievo.geojson$', MapLayer.as_view(model=rilievo_poly), name='rilievo_poligono'),
        url(r'^$',mostra_rilievi, name='mostra-rilievi'),
    ]