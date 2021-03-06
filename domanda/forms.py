# -*- coding: utf-8 -*-
from ajax_select import make_ajax_field
from ajax_select.fields import AutoCompleteSelectMultipleField
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.admin.widgets import FilteredSelectMultiple
from .models import danno, Agricoltore, CatastaleSmall, catastale_new


#creai tuoi form sotto
class DannoFormAgricoltore(forms.ModelForm):
    # fog_part_certified = forms.ModelMultipleChoiceField(queryset=CatastaleSmall.objects.all(), widget=
    # FilteredSelectMultiple("Catastale", False))#, attrs={'rows': '10'}))

    class Meta:
        model = danno
        fields = ('CAA','coltura', 'varieta','SumTot',
                  'SumSem','PercDanno','Produzione','PerProdPersa','ValoreDanno', 'NumPianteDan',
                  'TipoPiante','SelvagginaSem','OpereProtezione','polizza','biologica','iban','mappale','documentopdf','visurapdf','titolopossessopdf','note','foglio', 'particella')
        #widgets = {'fog_part_certified': forms.CheckboxSelectMultiple}
        widgets = {
            'note': forms.Textarea(attrs={'rows':4, 'cols':15}),
        }
        labels = {
            'mappale': 'Estratto di mappa',
            'documentopdf': 'Documento di identità in pdf',
            'visurapdf': 'Visura catastale',
            'titolopossessopdf': 'Titolo di possesso',

        }

    fog_part_db = make_ajax_field(danno, 'fog_part_db', 'catastali', help_text='Inserire nel formato Comune foglio e particella del tipo : -<b>Empoli 060 317</b>- dove 060 è il foglio è 60 e la particella è 317 ')

    class Media:
        css = {'all': ('/static/admin/css/widgets.css',), }  # custom css
        js = ('/admin/jsi18n',)


    # def __init__(self, parents=None, *args, **kwargs):
    #     super(DannoForm, self).__init__(*args, **kwargs)

class DannoFormCAA(forms.ModelForm):
    # fog_part_certified = forms.ModelMultipleChoiceField(queryset=CatastaleSmall.objects.all(), widget=
    # FilteredSelectMultiple("Catastale", False))#, attrs={'rows': '10'}))

    class Meta:
        model = danno
        fields = ('richiedente','data_danno', 'coltura', 'varieta','SumTot',
                  'SumSem','PercDanno','Produzione','PerProdPersa','ValoreDanno', 'NumPianteDan',
                  'TipoPiante','SelvagginaSem','OpereProtezione','mappale','documentopdf','visurapdf','titolopossessopdf',
                  'note','foglio', 'particella','comune',)
        #widgets = {'fog_part_certified': forms.CheckboxSelectMultiple}
        widgets = {
            'data_danno': forms.SelectDateWidget(years=range(2015, 2100))
        }
        labels = {
            'mappale': 'Estratto di mappa',
            'documentopdf': 'Documento di identità in pdf',
            'visurapdf': 'Visura catastale',
            'titolopossessopdf': 'Titolo di possesso',
        }

    fog_part_db = make_ajax_field(danno, 'fog_part_db', 'catastali', help_text='Inserire nel formato Comune foglio e particella del tipo : -    <b>Empoli 060 317</b>- dove 060 è il foglio 60 e la particella è 317.')

    class Media:
        css = {'all': ('/static/admin/css/widgets.css',), }  # custom css
        js = ('/admin/jsi18n',)





class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        labels = {
            'username': ('Codice Fiscale'),
        }
        help_texts = {
            'username': ('CF Agricoltore - obbligatorio'),
        }

class AgricoltoreForm(forms.ModelForm):

    # il formato corretto per inserire la data risulta: mm/dd/yyyy
    class Meta:
        model = Agricoltore
        exclude = ('user','CF')
        #widgets = {'dataNascita', forms.DateInput}
        widgets = {
            'dataNascita': forms.SelectDateWidget(years=range(1900, 2000))
        }