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
                  'TipoPiante','SelvagginaSem','OpereProtezione','mappale','note','foglio', 'particella')
        #widgets = {'fog_part_certified': forms.CheckboxSelectMultiple}
        widgets = {
            'note': forms.Textarea(attrs={'rows':4, 'cols':15}),
        }
        labels = {
            'mappale': 'Estratto di mappa',
        }

    fog_part_db = make_ajax_field(danno, 'fog_part_db', 'catastali', help_text='Inserire nel formato Comune foglio e particella del tipo : -<b>Empoli 0600 317</b>- dove il foglio è 0600 e la particella è 317 ')

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
        fields = ('richiedente', 'coltura', 'varieta','SumTot',
                  'SumSem','PercDanno','Produzione','PerProdPersa','ValoreDanno', 'NumPianteDan',
                  'TipoPiante','SelvagginaSem','OpereProtezione','mappale','note','foglio', 'particella',)
        #widgets = {'fog_part_certified': forms.CheckboxSelectMultiple}
        labels = {
            'mappale': 'Estratto di mappa',
        }

    fog_part_db = make_ajax_field(danno, 'fog_part_db', 'catastali', help_text='Inserire nel formato Comune foglio e particella del tipo : -<b>Empoli 0600 317</b>- dove il foglio è 0600 e la particella è 317 ')

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

    # il formato correto per inserire la data risulta: mm/dd/yyyy
    class Meta:
        model = Agricoltore
        exclude = ('user','RefTel','CF')
        #widgets = {'dataNascita', forms.DateInput}
        widgets = {
            'dataNascita': forms.SelectDateWidget(years=range(1900, 2000))
        }