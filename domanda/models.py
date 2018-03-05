# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

# Create your models here.

class catastale_new(models.Model):
    part = models.CharField(max_length=5)
    foglio = models.CharField(max_length=8)
    comune = models.CharField(max_length=25)
    mpoly = models.MultiPolygonField(srid=3003)
    objects = models.GeoManager()

    # Returns the string representation of the model.
    def __str__(self):  # __unicode__ on Python 2
        return u'%s f: %s p: %s' % (self.comune, self.foglio[-4:], self.part)

    class Meta:
        verbose_name = 'catastale'
        verbose_name_plural = 'catastali'



class CatastaleSmall(models.Model):
    # Regular Django fields corresponding to the attributes in the
    # world borders shapefile.
    part = models.CharField(max_length=5)
    sub = models.CharField(max_length=5)
    foglio = models.CharField(max_length=8)
    idseq = models.BigIntegerField()
    comune = models.CharField(max_length=250,default='')

    # GeoDjango-specific: a geometry field (MultiPolygonField), and
    # overriding the default manager with a GeoManager instance.
    mpoly = models.MultiPolygonField(srid=4326)
    objects = models.GeoManager()

    # Returns the string representation of the model.
    def __str__(self):  # __unicode__ on Python 2
        return u'%s f: %s p: %s' %(self.comune, self.foglio,self.part)

    class Meta:
        verbose_name='catastale_v'
        verbose_name_plural='catastali_v'



class quadranti(models.Model):
    fid = models.FloatField()
    left = models.FloatField()
    top = models.FloatField()
    right = models.FloatField()
    bottom = models.FloatField()
    mpoly = models.MultiPolygonField(srid=3003)

    # Returns the string representation of the model.
    def __str__(self):  # __unicode__ on Python 2
        return u'fid: %s' % (self.fid)


class danno(models.Model):
    richiedente = models.ForeignKey(User, null=True, blank=True,limit_choices_to={'groups__name': "Agricoltore"})
    foglio = models.CharField(max_length=50,verbose_name='Fogli colpiti da danno',default='',null=True, blank=True,help_text='<b>Attenzione</b> da inserire solo nel caso in cui non si ritrova il catastale nel campo in fondo alla pagina')
    particella = models.CharField(max_length=50,default='',null=True, blank=True,help_text='<b>Attenzione</b> da inserire solo nel caso in cui non si ritrova il catastale nel campo in fondo alla pagina')
    coltura = models.CharField(max_length=50,default='')
    varieta = models.CharField(max_length=50,verbose_name='varietà colturale',blank=True)
    SumTot = models.FloatField(verbose_name='Superficie totale particelle ettari',default=0)
    SumSem = models.FloatField(verbose_name='Superficie seminativa particella ettari',default=0)
    PercDanno = models.IntegerField(verbose_name='% stimata del danno',default=0,validators=[MinValueValidator(0), MaxValueValidator(100)],help_text='valore compreso tra 0 e 100')
    Produzione = models.BigIntegerField(verbose_name='produzione prevista nella particella',default=0)
    PerProdPersa = models.BigIntegerField(verbose_name='% produzione persa',default=0,validators=[MinValueValidator(0), MaxValueValidator(100)],help_text='valore compreso tra 0 e 100')
    ValoreDanno = models.BigIntegerField(verbose_name='ipotetico valore del danno stimato dal dichiarante',default=0)
    NumPianteDan = models.BigIntegerField(verbose_name='numero piante danneggiate',default=0,blank=True)
    TipoPiante  = models.CharField(max_length=50,blank=True)
    SelvagginaSem = models.CharField(max_length=250,default='',verbose_name='Selvaggina che ha fatto i danni alla coltura')
    OpereProtezione = models.CharField(max_length=250,blank=True)
    #dati addizionali
    data_ins = models.DateField(auto_now_add=True,verbose_name='Data inserimento')
    note = models.CharField(max_length=1000,blank=True,null=True,verbose_name='Note (facoltativo)')
    #stato di lavorazione della
    LAVORAZIONE = 'lavorazione'
    RILIEVO = 'rilievo'
    COMPLETA = 'completa'
    STATI_PRATICA = (
        (LAVORAZIONE, 'In lavorazione'),
        (RILIEVO, 'In rilievo'),
        (COMPLETA, 'Completa'),
    )

    stato_pratica = models.CharField(
        max_length=20,
        choices=STATI_PRATICA,
        default=LAVORAZIONE,
    )
    CAA = models.ForeignKey(User, null=True, blank=True, limit_choices_to={'groups__name': "CAA"}, related_name='+', help_text='Centro di Assistenza agricolo')
    Rilevatore = models.ForeignKey(User, null=True, blank=True, limit_choices_to={'groups__name': "Rilevatore"}, related_name='+', )
    mappale = models.FileField(blank=True,upload_to='mappali/',help_text='file pdf')
    fog_part_certified = models.ManyToManyField(CatastaleSmall,verbose_name='Foglio Particella da Catastale',help_text='aiuto')
    fog_part_db = models.ManyToManyField(catastale_new, verbose_name='Foglio Particella da Catastale',
                                                help_text='Inserire nel formato Comune foglio e particella del tipo : -<b>Empoli 0600 317</b>- dove 0600 è il foglio e 317 la particella')

    #Add helper function for Admin display
    def author_full_name(self):
        return self.richiedente.get_full_name()
    author_full_name.short_description = 'Nome Cognome'

    def save(self):
        if self.id:
            old_danno = danno.objects.get(pk=self.id)
            if old_danno.Rilevatore is None and self.Rilevatore is not None:
                #individuo il destinatario
                if self.Rilevatore.email == '':
                    to_mail = 'pierluigi.derosa@gfosservices.it'
                else:
                    to_mail = self.Rilevatore.email
                #costruisco il corpo del messaggio
                body = '''
                Gentile %s,
                le è stato appena assegnato un nuovo rilievo.
                La preghiamo di voler accedere alla propria pagina personale per scaricare i dati.
                Cordiali saluti
                ''' %(self.Rilevatore.get_username())
                send_mail('Assegnazione rilievo %d' %(self.id), body, 'noreply@parsifal.co', [to_mail])
        super(danno, self).save()


    class Meta:
        verbose_name = 'danno'
        verbose_name_plural = 'danni'

    def get_absolute_url(self):
        return reverse('danno_singolo',kwargs={'id': self.id})

    def __str__(self):
        return u'%s %s %s' % (self.richiedente,self.foglio, self.particella)


class Agricoltore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,limit_choices_to={'groups__name': "Agricoltore"})
    luogoNascita = models.CharField(max_length=100,verbose_name='luogo di nascita')
    dataNascita = models.DateField(blank=True,verbose_name='data di nascita',null=True)
    viaResidenza = models.CharField(max_length=100,verbose_name='via')
    ComuneRes = models.CharField(max_length=50, default='',verbose_name='Comune di residenza')
    telefono = models.CharField(max_length=50, default='',blank=True)
    CF = models.CharField(max_length=50,default='')
    PIva = models.CharField(max_length=255, default='',verbose_name='P. IVA')
    Referente = models.CharField(max_length=255, default='',blank=True)
    RefTel = models.CharField(max_length=255, default='',blank=True,verbose_name='Tel: referente')
    azNome = models.CharField(max_length=255, default='',blank=True,verbose_name='Nome azienda')
    azLoc = models.CharField(max_length=255, default='',blank=True,verbose_name='Località')
    azComune = models.CharField(max_length=255, default='',blank=True,verbose_name='Comune Azienda')




    def __str__(self):
        return u'Nome %s %s - CF: %s' % (str(self.user.first_name), str(self.user.last_name), self.CF)

    class Meta:
        verbose_name='Agricoltore'
        verbose_name_plural='Agricoltori'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Agricoltore.objects.create(user=instance)

