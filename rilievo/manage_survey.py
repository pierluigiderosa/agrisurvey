import os.path as osp
import sqlite3 as sqlite
import json

import cStringIO
from django.contrib.gis.geos import Point, GEOSGeometry
from django.core.files import File
from pysqlite2 import dbapi2 as sqlite3
from .models import rilievo_poly,anagrafica
from domanda.models import danno
from datetime import datetime as dt


def ExportFormNotes(file_gpap,id_danno):
    con = sqlite.connect(file_gpap.temporary_file_path())
    DBcursor = con.cursor()
    # get the rough list of section names (rough means like: {"sectionname":"my name")
    sectionNames = DBcursor.execute("SELECT DISTINCT substr(form,0,instr(form,',')) AS formName FROM notes")
    sectionNames = sectionNames.fetchall()
    errore=''

    if len(sectionNames) == 0:
        sectionNames = [('', '')]
        errore = "non sono stati inseriti i rilievi"

    # for each section name make a new vector file
    for sn in sectionNames:
        baseFieldNames = ["_id", "lon", "lat", "altim", "ts", "description", "text", "form", "style", "isdirty"]

        notes = DBcursor.execute("SELECT * FROM notes WHERE form LIKE '" + sn[0] + "%'")
        cleanName = sn[0].split(":")
        cleanName = cleanName[1].replace('"', '')

        if cleanName == 'agrisurvey':
            rilievo_list=[]
            for note in notes:
                out=dict()
                long = note[1]
                lat=note[2]
                out['lat']=lat
                out['lon']=long

                rilievo = json.loads(note[7])
                for j in range(len(rilievo['forms'])):
                    formitem = rilievo['forms'][j]['formitems']
                    for item in formitem:
                        if item.has_key('key'):
                            out[item['key']] = item['value']
                rilievo_list.append(out)


        if cleanName.startswith('agrisurvey_anag'):
            for note in notes:
                # there are some more attributes to save ...
                rilievo = json.loads(note[7])
                sezioni = []
                for sec in range(len(rilievo['forms'])):
                    sezioni.append(rilievo['forms'][sec]['formname'])

                anagrafica_output=dict()
                for j in range(len(rilievo['forms'])):
                    formitem = rilievo['forms'][j]['formitems']
                    for item in formitem:
                        if item.has_key('key'):
                            anagrafica_output[item['key']] = item['value']
            #get firma rappresentante aziendale
            firma = anagrafica_output['Firma']
            if len(firma.split(';'))>1:
                firma=firma.split(';')[1]
            imgsData = DBcursor.execute("SELECT * FROM imagedata WHERE _id = " + str(firma))
            imgData=imgsData.fetchone()
            #salvo il file in tmp dir
            out_file = open(osp.join('/tmp/', 'firma_pratica.jpg'), 'wb')
            out_file.write(imgData[1])
            out_file.close()

            #get firma rilevatore
            firma_rilevatore = anagrafica_output['Firma_rilevatore']
            if len(firma_rilevatore.split(';')) > 1:
                firma_rilevatore = firma_rilevatore.split(';')[1]
            imgsData_rilevatore = DBcursor.execute("SELECT * FROM imagedata WHERE _id = " + str(firma_rilevatore))
            imgsData_rilevatore = imgsData_rilevatore.fetchone()
            # salvo il file in tmp dir
            out_file = open(osp.join('/tmp/', 'firma_pratica_rilevatore.png'), 'wb')
            out_file.write(imgsData_rilevatore[1])
            out_file.close()

            #data sopralluogo
            datasop_string = anagrafica_output['data_sopralluogo']
            data_soprallugo = dt.strptime(datasop_string, '%Y-%m-%d')
            #salvo anagrafica in DB

            anag = anagrafica(
                mappa=anagrafica_output['mappa'],

                Rapp_Az = anagrafica_output['Rapp_Az'],
                Az_Ag_denominazione = anagrafica_output['Az_Ag_denominazione'],
                Rapp_Az_documento = anagrafica_output['Rapp_Az_documento'],
                Az_Ag_possesso = anagrafica_output['Az_Ag_possesso'],
                Az_Ag_indirizzo = anagrafica_output['Az_Ag_indirizzo'],
                # campi aggiunti da modifica form di cavini
                data_sopralluogo = data_soprallugo,
                tecnico_incaricato=anagrafica_output['tecnico_incaricato'],
                # id pratica
                id_pratica = danno.objects.get(pk=id_danno),
            )

            anag.save()
            anag.Firma.save('firma_pratica_%s.jpg' %(str(id_danno)), File(open('/tmp/firma_pratica.jpg', 'r')))
            # aggiunta firma rilevatore da modifica form di cavini
            anag.Firma_rilevatore.save('firma_pratica_rilevatore_%s.jpg' % (str(id_danno)), File(open('/tmp/firma_pratica_rilevatore.png', 'r')))

    con.close()
    return anagrafica_output,rilievo_list,errore


def ExportGeomSurvey(file_splite):
    conn = sqlite3.connect(file_splite.temporary_file_path())
    conn.enable_load_extension(True)
    # initializing Spatial MetaData
    # using v.2.4.0 this will automatically create
    # GEOMETRY_COLUMNS and SPATIAL_REF_SYS
    conn.execute("SELECT load_extension('mod_spatialite');")

    sql_conteggio='select count(*) from danni_editabile'
    c=conn.cursor()
    c.execute(sql_conteggio)
    n_geom=c.fetchone()[0]

    sql_geom_unita='select aswkt(geom) from danni_editabile'
    c.execute(sql_geom_unita)
    geom_wkt = c.fetchall()

    conn.close()
    return geom_wkt



def spatial_join(poligoni,rilievi,id_danno):
    out_str=''
    for id_rilievo in range(len(rilievi)):
        rilievo=rilievi[id_rilievo]
        rilievoPoint = Point(rilievo['lon'], rilievo['lat'], srid=4326)
        rilievoPoint.transform(3003)

        out_str+='<br><br>punto rilievo id: '+str(id_rilievo)
        out_str+=rilievoPoint.wkt

        #ricerco il poligono piu vicino ed inizio con il primo
        id_ok=0
        min_distance=rilievoPoint.distance(GEOSGeometry(poligoni[id_ok][0],srid=3003))

        for id_poligono in range(len(poligoni)):
            poligono=GEOSGeometry(poligoni[id_poligono][0], srid=3003)
            distanza=rilievoPoint.distance(poligono)
            if distanza<min_distance:
                min_distance=distanza
                id_ok=id_poligono
            out_str+='<br>id polig: '+str(id_poligono)
            out_str+='<br> distanza: '+str(distanza)
        out_str+='<br>Minimo id: '+str(id_ok)+'distanza: '+str(min_distance)

        #salvo i dati nel DB
        rilievo_copy={}
        for k,v in rilievo.iteritems():
            if v=='':
                v=0
            rilievo_copy[k] = v
        rilievo=rilievo_copy

        r = rilievo_poly(
            OperePrevenzione=rilievo['OperePrevenzione'],
            comune = rilievo['comune'],
            particelle = rilievo['particelle'],
            coltura = rilievo['coltura'],
            lon = rilievo['lon'],
            Localizzazione_fondo =rilievo['Localizzazione_fondo'],
            prod_media = rilievo['prod_media'],
            Sup_totale = rilievo['Sup_totale'],
            Specie1 = rilievo['Specie1'],
            lat =rilievo['lat'],
            Sup_danneggiata = rilievo['Sup_danneggiata'],
            perc_danno =rilievo['perc_danno'],
            Specie2 =rilievo['Specie2'],
            foglio = rilievo['foglio'],
            varieta = rilievo['varieta'],
            #salvataggio altri dati di rilievo dopo modifica cavini
            specie1_altro=rilievo['Specie1_altro'],
            statovegsanitario = rilievo['statovegsanitario'],
            numpiantesostituire = rilievo['numpiantesostituire'],
            colturabiologica = rilievo['colturabiologica'],
            note_colturali = rilievo['note_colturali'],
            OperePrevenzione_altro = rilievo['OperePrevenzione_altro'],
            coltura_altro = rilievo['coltura_altro'],
            FunzionalitaPrevenzione = rilievo['FunzionalitaPrevenzione'],
            perc_specie2 =rilievo['perc_specie2'],
            superficierisemina =rilievo['superficierisemina'],
            Localizzazione_fondo_altro =rilievo['Localizzazione_fondo_altro'],
            quantitaprodotto = rilievo['quantitaprodotto'],
            perc_specie1 = rilievo['perc_specie1'],
            Specie2_altro = rilievo['Specie2_altro'],

            # id pratica
            id_pratica = danno.objects.get(pk=id_danno),
            mpoly = poligoni[id_ok][0],
                         )
        r.save()

    return out_str


