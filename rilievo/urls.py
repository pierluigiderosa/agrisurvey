from django.conf.urls import url
from views import upload_file, mostra_rilievi,mostra_singolo_rilievo,MapLayer
from .models import rilievo_poly

urlpatterns = [
        url(r'^inserisci/(?P<id>\d+)$', upload_file, name='upload_file'),
        url(r'^mostra/(?P<id>\d+)$', mostra_singolo_rilievo, name='rilievo_singolo'),
        url(r'^rilievo.geojson$', MapLayer.as_view(model=rilievo_poly), name='rilievo_poligono'),
        url(r'^$',mostra_rilievi, name='mostra-rilievi'),
    ]