import os.path as osp
import sqlite3 as sqlite
import json





def ExportFormNotes(file_gpap):
    con = sqlite.connect(file_gpap._name)
    DBcursor = con.cursor()
    # get the rough list of section names (rough means like: {"sectionname":"my name")
    sectionNames = DBcursor.execute("SELECT DISTINCT substr(form,0,instr(form,',')) AS formName FROM notes")
    sectionNames = sectionNames.fetchall()

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

    return output,out_list

