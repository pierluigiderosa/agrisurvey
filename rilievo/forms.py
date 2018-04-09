from django import forms

class UploadGpapForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField(label='file di progetto .gpap')
    splite_file = forms.FileField(label='File spatialite')