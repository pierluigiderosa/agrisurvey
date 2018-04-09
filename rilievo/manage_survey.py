import os.path as osp
import sqlite3 as sqlite
import json

from django.contrib.gis.geos import Point, GEOSGeometry
from pysqlite2 import dbapi2 as sqlite3




def ExportFormNotes(file_gpap):
    con = sqlite.connect(file_gpap._name)
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
            out_list=[]
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
                out_list.append(out)



        if cleanName.startswith('agrisurvey_anag'):
            for note in notes:
                # there are some more attributes to save ...
                rilievo = json.loads(note[7])
                sezioni = []
                for sec in range(len(rilievo['forms'])):
                    sezioni.append(rilievo['forms'][sec]['formname'])

                output=dict()
                for j in range(len(rilievo['forms'])):
                    formitem = rilievo['forms'][j]['formitems']
                    for item in formitem:
                        if item.has_key('key'):
                            output[item['key']] = item['value']
            #get firma
            firma = output['Firma']
            if len(firma.split(';'))>1:
                firma=firma.split(';')[1]
            imgsData = DBcursor.execute("SELECT * FROM imagedata WHERE _id = " + str(firma))
            imgData=imgsData.fetchone()
            #TODO scegliere il percorso dove salvare il file
            out_file = open(osp.join('/home/pierluigi/', 'firma.jpg'), 'wb')
            out_file.write(imgData[1])
            out_file.close()

    return output,out_list,errore


def ExportGeomSurvey(file_splite):
    conn = sqlite3.connect(file_splite._name)
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

    return geom_wkt



def spatial_join(poligoni,rilievi):
    out_str=''
    for id_rilievo in range(len(rilievi)):
        rilievo=rilievi[id_rilievo]
        rilievoPoint = Point(rilievo['lon'], rilievo['lat'], srid=4326)
        rilievoPoint.transform(3003)

        out_str+='<br><br>punto rilievo id: '+str(id_rilievo)
        out_str+=rilievoPoint.wkt

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

    return out_str


