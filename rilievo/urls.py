from django.conf.urls import url
from views import upload_file

urlpatterns = [
        url(r'^inserisci/$', upload_file, name='upload_file'),
    ]