from django import forms
from .models import prezzo

class UploadGpapForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField(label='file di progetto .gpap')
    splite_file = forms.FileField(label='File spatialite')


class prezzoColturaForm(forms.ModelForm):
    class Meta:
        model= prezzo
        fields='__all__'