# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date

from django.contrib.gis.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Count

from domanda.models import danno

# Create your models here.

class rilievo_poly(models.Model):
    OperePrevenzione =  models.CharField(max_length=255,blank=True,null=True)
    comune = models.CharField(max_length=50,blank=True,null=True)
    particelle = models.CharField(max_length=50,blank=True,null=True)
    coltura = models.CharField(max_length=50,blank=True,null=True)
    lon = models.FloatField(blank=True,null=True)
    Localizzazione_fondo = models.CharField(max_length=100,blank=True,null=True)
    prod_media = models.FloatField(blank=True,null=True)
    Sup_totale = models.FloatField(blank=True,null=True)
    Specie1 = models.CharField(max_length=250,blank=True,null=True)
    lat = models.FloatField(blank=True,null=True)
    Sup_danneggiata = models.FloatField(blank=True,null=True)
    perc_danno = models.IntegerField(blank=True,null=True)
    Specie2 = models.CharField(max_length=250,blank=True,null=True)
    foglio = models.CharField(max_length=50,blank=True,null=True)
    varieta = models.CharField(max_length=50,blank=True,null=True,verbose_name='coltura e varieta')
    #nuovi campi aggiunti dopo modifica rilievo di cavini
    specie1_altro = models.CharField(max_length=250,blank=True,null=True,default='')
    statovegsanitario = models.CharField(max_length=250, blank=True, null=True, default='')
    numpiantesostituire = models.FloatField(blank=True, null=True, default=0)
    colturabiologica = models.CharField(max_length=250, blank=True, null=True, default='')
    note_colturali = models.CharField(max_length=250, blank=True, null=True, default='')
    OperePrevenzione_altro = models.CharField(max_length=250, blank=True, null=True, default='')
    coltura_altro = models.CharField(max_length=250, blank=True, null=True, default='')
    FunzionalitaPrevenzione = models.CharField(max_length=250, blank=True, null=True, default='')
    perc_specie2 = models.FloatField(blank=True, null=True, default=0)
    superficierisemina = models.FloatField(blank=True, null=True, default=0)
    Localizzazione_fondo_altro = models.CharField(max_length=250, blank=True, null=True, default='')
    quantitaprodotto = models.FloatField(blank=True, null=True, default=0,verbose_name='quantita prodotto perso in Q.Li')
    perc_specie1 = models.FloatField(blank=True, null=True, default=0)
    Specie2_altro = models.CharField(max_length=250, blank=True, null=True, default='')

    #id pratica
    id_pratica = models.ForeignKey(danno,on_delete=models.CASCADE,blank=True,null=True)

    # GeoDjango-specific: a geometry field (MultiPolygonField)
    mpoly = models.MultiPolygonField(srid=3003)

    # Returns the string representation of the model.
    def __str__(self):  # __unicode__ on Python 2
        return u'%s f: %s p: %s' % (self.comune, self.foglio, self.particelle)

    class Meta:
        verbose_name = 'rilievo'
        verbose_name_plural = 'rilievi'

class anagrafica(models.Model):
    mappa = models.CharField(max_length=250,blank=True, null=True)
    Firma = models.FileField(max_length=250,blank=True, upload_to='firme/', help_text='firma rapp. aziendale jpg')
    Rapp_Az = models.CharField(max_length=250,blank=True,null=True)
    Az_Ag_denominazione = models.CharField(max_length=250,blank=True, null=True)
    Rapp_Az_documento  = models.CharField(max_length=250,blank=True, null=True)
    Az_Ag_possesso = models.CharField(max_length=250,blank=True, null=True)
    Az_Ag_indirizzo = models.CharField(max_length=250,blank=True, null=True)
    #campi aggiunti da modifica di form di cavini
    data_sopralluogo = models.DateField(blank=True,null=True,default=date(2019, 8, 6)) #giorno di agosto che ho lavorato a agrisurvey
    tecnico_incaricato = models.CharField(max_length=250,blank=True,null=True,default='')
    Firma_rilevatore = models.FileField(max_length=250, blank=True, upload_to='firme/', help_text='firma rilevatore png')


    #id pratica
    id_pratica = models.ForeignKey(danno,on_delete=models.CASCADE,blank=True,null=True)

    # Returns the string representation of the model.
    def __str__(self):  # __unicode__ on Python 2
        return u'pratica: %s rapp: %s' % (self.id_pratica_id, self.Rapp_Az)

    class Meta:
        verbose_name = 'anagrafica'
        verbose_name_plural = 'anagrafiche'

def current_year():
    return date.today().year


def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)

def getColturaVarieta():
    COLTURA_CHOICES = []
    for sin_coltura in rilievo_poly.objects.values('varieta').order_by('varieta'):
            COLTURA_CHOICES.append((sin_coltura['varieta'], sin_coltura['varieta']))
    return COLTURA_CHOICES

class prezzo(models.Model):
    COLTURA_CHOICES = getColturaVarieta()
    coltura = models.CharField(choices=COLTURA_CHOICES,default='',max_length=50)
    anno = models.PositiveIntegerField(
        default=current_year(), validators=[MinValueValidator(1984), max_value_current_year])
    prezzo = models.DecimalField(max_digits=6, decimal_places=2,verbose_name='prezzo al Q.le')

    # Returns the string representation of the model.
    def __str__(self):  # __unicode__ on Python 2
        return u'%s anno:%s' % (self.coltura, self.anno)

    class Meta:
        verbose_name = 'prezzo'
        verbose_name_plural = 'prezzi'
        unique_together = ["coltura", "anno"]
