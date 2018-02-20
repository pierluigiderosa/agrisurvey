from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from.views import MapLayer
from .views import ListaDomande, lista_rilievi, danno_singolo, InserisciDanno, InserisciAgricoltore, dannoEdit, download_sqlite, quadrante
from .models import CatastaleSmall



urlpatterns = [
    url(r'^(?P<id>\d+)/$',danno_singolo, name='danno_singolo'),
    url(r'^(?P<pk>\d+)/edit/$', login_required(dannoEdit.as_view()), name='danno_edit'),
    url(r'^assegna/$', login_required(lista_rilievi.as_view()), name='lista_rilievi'),
    url(r'^assegna/(?P<id>\d+)/download/$', download_sqlite, name='down_sqlite'),
    url(r'^assegna/quadrante/(?P<id>\d+)/$', quadrante, name='quadrante'),
    url(r'^inserisci/agricoltore/$',InserisciAgricoltore,name='inserisci_agricoltore'),
    url(r'^inserisci/$',InserisciDanno,name='inserisci_danno'),
    url(r'^catastale.geojson$', MapLayer.as_view(model=CatastaleSmall), name='data'),
    url(r'^$', ListaDomande.as_view(), name='lista_domande'),
    # url(r'^(?P<id>\d+)/$', DetailView.as_view(
    #     model= danno,
    #     template_name="domanda.html"
    # ),name="danno_singolo")
    #url(r'^$', views.lista_domande, name='lista_domande'),
]