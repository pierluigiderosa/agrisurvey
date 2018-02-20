from django.contrib.auth.models import User

from domanda.models import danno,Agricoltore

danno.objects.all()
danno2=danno.objects.get(id=2) #una particella
danno5=danno.objects.get(id=2) # due particelle
#lista dei fields di un modello
danno2._meta.get_fields()
#se voglio il richiedente del danno - chiave esterna
danno2.richiedente
#info specifiche
danno2.richiedente.email
#se voglio i danni di un utente
User.objects.all()
riccardo=User.objects.get(username='RiccardoGuadagno')
#tutti i danni di riccardo
riccardo.danno_set.all()
#quanti sono
len(riccardo.danno_set.all())

#geodjango
danno2.fog_part_certified.all() #tutti le particelle assegnate
catastale = danno2.fog_part_certified.all()[0] # elemento catastale spaziale
catastale.mpoly.geojson #geojson del catastale


#individuare id del quadrante
from domanda.models import quadranti
for i in range(danno2.fog_part_certified.count()):
    print i

catasto = danno2.fog_part_certified.all()[0]
#riproietto a 3003
catasto.mpoly.transform('3003')
quad_interessati=quadranti.objects.filter(mpoly__intersects=catasto.mpoly)
# i quadranti quad_interessati
quad_interessati.count()
# il fid del quadrante
miofid=quad_interessati[0].fid