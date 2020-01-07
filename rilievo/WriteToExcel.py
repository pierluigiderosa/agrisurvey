#!/usr/bin/python
# -*- coding: utf-8 -*-

import StringIO
import xlsxwriter
from django.db.models import Sum, FloatField, Avg
from django.utils.translation import ugettext

def getPrezzoColtVarieta(colturavarieta,annointeresse=2019):
    from rilievo.models import prezzo
    prezzi_prodotti = prezzo.objects.filter(coltura=colturavarieta,anno=annointeresse)
    if prezzi_prodotti.count() == 1:
        prezzo_prodotto=prezzi_prodotti.first().prezzo
    elif prezzi_prodotti.count() > 1:
        #TODO vedere come correggere se trovo più prezzi...
        prezzo_prodotto = prezzi_prodotti.first().prezzo
    else:
        prezzo_prodotto = 0.0
    return float(prezzo_prodotto)

def ReportColturaExcel(rilievi):
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)

    worksheet_s = workbook.add_worksheet("Report")
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'left',
        'valign': 'vcenter'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'left',
        'valign': 'top',
        'border': 1
    })
    cell_center = workbook.add_format({
       'align': 'center'
    })
    title_text = u"{0} {1}".format(ugettext("Consuntivo Totale per Agricoltore - Coltura "), rilievi[0].id_pratica)
    worksheet_s.merge_range('A1:H1', title_text, title)
    #add rows header
    worksheet_s.write(3, 0, ugettext("AGRICOLTORE"), header)
    worksheet_s.write(3, 1, ugettext("COLTURA"), header)
    worksheet_s.write(3, 2, ugettext("RICHIESTI"), header)
    worksheet_s.write(3, 3, ugettext("PERIZIATI"), header)
    worksheet_s.write(3, 4, ugettext("Euro A QUINTALE"), header)
    worksheet_s.write(3, 5, ugettext("IMPORTO LORDO"), header)
    worksheet_s.write(3, 6, ugettext("IMPORTO NETTO"), header)

    worksheet_s.set_column('A:A', 10)
    worksheet_s.set_column('L:L', 10)
    worksheet_s.set_column('M:M', 10)
    worksheet_s.set_column('N:N', 16)
    worksheet_s.set_column('O:O', 14)

    worksheet_s.write(2,0,ugettext("Resosconto per anno 2019 e ATC 9 - LIVORNO"))


    # Here we will adding the code to add data
    for idx, rilievo in enumerate(rilievi):
        row = 4 + idx
        worksheet_s.write(row, 0, rilievo.id_pratica.richiedente.first_name+' '+rilievo.id_pratica.richiedente.last_name, cell_center)
        worksheet_s.write(row, 1, rilievo.varieta, cell_center)
        worksheet_s.write_number(row, 2, rilievo.id_pratica.ValoreDanno, cell_center)
        worksheet_s.write(row, 3, rilievo.quantitaprodotto, cell_center)
        worksheet_s.write(row, 4, getPrezzoColtVarieta(rilievo.varieta), cell_center)
        worksheet_s.write(row, 5, rilievo.quantitaprodotto*getPrezzoColtVarieta(rilievo.varieta), cell_center)
        worksheet_s.write(row, 6, rilievo.quantitaprodotto*getPrezzoColtVarieta(rilievo.varieta), cell_center)



    workbook.close()
    xlsx_data = output.getvalue()
    # xlsx_data contains the Excel file
    return xlsx_data

def ReportPeriziatiAgricoltoreSpecie(rilievi):
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)

    worksheet_s = workbook.add_worksheet("Report Agricoltori specie")
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'left',
        'valign': 'vcenter'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'left',
        'valign': 'top',
        'border': 1
    })
    cell_center = workbook.add_format({
        'align': 'center'
    })
    title_text = u"{0} {1}".format(ugettext("Consuntivo Totale per Agricoltore -> Comune -> Specie -> Coltura"), rilievi[0].id_pratica)
    worksheet_s.merge_range('A1:H1', title_text, title)
    # add rows header
    worksheet_s.write(3, 0, ugettext("AGRICOLTORE"), header)
    worksheet_s.write(3, 1, ugettext("COMUNE"), header)
    worksheet_s.write(3, 2, ugettext("SPECIE"), header)
    worksheet_s.write(3, 3, ugettext("RICHIESTI"), header)
    worksheet_s.write(3, 4, ugettext("PERIZIATI"), header)
    worksheet_s.write(3, 5, ugettext("Euro A QUINTALE"), header)
    worksheet_s.write(3, 6, ugettext("IMPORTO LORDO"), header)
    worksheet_s.write(3, 7, ugettext("IMPORTO NETTO"), header)

    worksheet_s.set_column('A:A', 10)
    worksheet_s.set_column('L:L', 10)
    worksheet_s.set_column('M:M', 10)
    worksheet_s.set_column('N:N', 16)
    worksheet_s.set_column('O:O', 14)

    worksheet_s.write(2, 0, ugettext("Resosconto per anno 2019 e ATC 9 - LIVORNO"))

    # Here we will adding the code to add data
    for idx, rilievo in enumerate(rilievi):
        row = 4 + idx
        worksheet_s.write(row, 0,
                          rilievo.id_pratica.richiedente.first_name + ' ' + rilievo.id_pratica.richiedente.last_name,
                          cell_center)
        worksheet_s.write(row, 1, rilievo.comune, cell_center)
        worksheet_s.write(row, 2, rilievo.Specie1, cell_center)
        worksheet_s.write_number(row, 3, rilievo.id_pratica.ValoreDanno, cell_center)
        worksheet_s.write(row, 4, rilievo.quantitaprodotto, cell_center)
        worksheet_s.write(row, 5, getPrezzoColtVarieta(rilievo.varieta), cell_center)
        worksheet_s.write(row, 6, rilievo.quantitaprodotto * getPrezzoColtVarieta(rilievo.varieta), cell_center)
        worksheet_s.write(row, 7, rilievo.quantitaprodotto * getPrezzoColtVarieta(rilievo.varieta), cell_center)

    workbook.close()
    xlsx_data = output.getvalue()
    # xlsx_data contains the Excel file
    return xlsx_data


def findRichiestiSpecie(richiesti, specie):
    danno=None
    for idx in richiesti:
        if idx['id_pratica__SelvagginaSem']==specie:
            danno=idx['sumValoreDanno']
    return  danno

def findRichiestVarieta(richiesti,varieta):
    danno=None
    for idx in richiesti:
        if idx['id_pratica__varieta']==varieta:
            danno=idx['mediaValoreDanno']
    return  danno


def ReportAggregatoSpeciePeriziati(rilievi, prezzi):
    '''
    report aggregato per tutte le perizia per specie
    FUNZIONA
    '''
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)

    #----------- Inizio il calcolo dei dati aggregati
    # periziati =rilievi.values('Specie1').annotate(sup_per_perc_danno=Sum('Sup_danneggiata') * Sum('perc_danno', output_field=FloatField()))
    periziati = rilievi.values('Specie1', 'varieta', 'quantitaprodotto')

    for perizia in periziati:
        #TODO controllare cosa succede se più colture hanno un prezzo
        if  prezzi.filter(coltura=perizia['varieta']).exists():
            perizia.update({'prezzo': prezzi.filter(coltura=perizia['varieta']).first().prezzo})
        else:
            perizia.update({'prezzo':0})


    periziatiDict=dict()
    tot=0
    for idx in periziati:
        if not periziatiDict.has_key(idx['Specie1']):
            tot = float(idx['prezzo']) * idx['quantitaprodotto']
        else:
            tot=tot+float(idx['prezzo'])*idx['quantitaprodotto']
        periziatiDict.update({idx['Specie1']:tot})

    richiesti=rilievi.select_related('id_pratica').values('id_pratica__SelvagginaSem').annotate(
        sumValoreDanno=Sum('id_pratica__ValoreDanno'))


    worksheet_s = workbook.add_worksheet("Report specie")
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'left',
        'valign': 'vcenter'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'left',
        'valign': 'top',
        'border': 1
    })
    cell_center = workbook.add_format({
       'align': 'center'
    })
    title_text = u"{0}".format(ugettext("Consuntivo Totale richesti e totali periziati per specie"))
    worksheet_s.merge_range('A1:H1', title_text, title)
    #add rows header
    worksheet_s.write(3, 0, ugettext("SPECIE"), header)
    worksheet_s.write(3, 1, ugettext("RICHIESTI"), header)
    worksheet_s.write(3, 2, ugettext("PERIZIATI"), header)

    worksheet_s.set_column('A:A', 10)
    worksheet_s.set_column('L:L', 10)
    worksheet_s.set_column('M:M', 10)
    worksheet_s.set_column('N:N', 16)
    worksheet_s.set_column('O:O', 14)

    worksheet_s.write(2,0,ugettext("Resosconto per anno 2019 e ATC 9 - LIVORNO"))


    # Here we will adding the code to add data
    for idx, specie in enumerate(periziatiDict):
        row = 4 + idx
        worksheet_s.write(row, 0, specie, cell_center)
        worksheet_s.write(row, 1, findRichiestiSpecie(richiesti, specie), cell_center)
        worksheet_s.write_number(row, 2, periziatiDict[specie], cell_center)

    workbook.close()
    xlsx_data = output.getvalue()
    # xlsx_data contains the Excel file
    return xlsx_data

def getDannoRichiesto(richiesti,varieta):
    danno=0
    for idx in richiesti:
        if idx['id_pratica__varieta']==varieta:
            danno=idx['sumValoreDanno']
    return  danno

def ReportAggregatoColturaPeriziati(rilievi, prezzi):
    '''
    report aggregato per tutte le perizie per coltura
    '''
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)

    # ----------- Inizio il calcolo dei dati aggregati
    # periziati =rilievi.values('Specie1').annotate(sup_per_perc_danno=Sum('Sup_danneggiata') * Sum('perc_danno', output_field=FloatField()))
    periziati = rilievi.values('varieta', 'quantitaprodotto', 'numpiantesostituire','superficierisemina')

    #aggrego per coltua le quantità di prodotto
    periziatiDict = periziati.values('varieta').annotate(SumQuantita=Sum('quantitaprodotto'))

    #prendo i valori di danno richiesti per ogni coltura
    #TODO controllare non funziona bene la richiesta.
    # se più rilievi riferiscono alla stessa domanda e hanno stessa varietà lui somma le richieste di danno
    richiesti = rilievi.select_related('id_pratica').values('id_pratica__varieta').annotate(
        mediaValoreDanno=Sum('id_pratica__ValoreDanno'))

    worksheet_s = workbook.add_worksheet("Report per coltura")
    title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'left',
        'valign': 'vcenter'
    })
    header = workbook.add_format({
        'bg_color': '#F7F7F7',
        'color': 'black',
        'align': 'left',
        'valign': 'top',
        'border': 1
    })
    cell_center = workbook.add_format({
        'align': 'center'
    })
    title_text = u"{0}".format(ugettext("Consuntivo Totale richesti e totali periziati per coltura"))
    worksheet_s.merge_range('A1:H1', title_text, title)
    # add rows header
    worksheet_s.write(3, 0, ugettext("COLTURA"), header)
    worksheet_s.write(3, 1, ugettext("RICHIESTI"), header)
    worksheet_s.write(3, 2, ugettext("PERIZIATI"), header)
    worksheet_s.write(3, 3, ugettext("Euro A QUINTALE"), header)
    worksheet_s.write(3, 4, ugettext("IMPORTO LORDO"), header)
    worksheet_s.write(3, 5, ugettext("IMPORTO NETTO"), header)

    worksheet_s.set_column('A:A', 10)
    worksheet_s.set_column('L:L', 10)
    worksheet_s.set_column('M:M', 10)
    worksheet_s.set_column('N:N', 16)
    worksheet_s.set_column('O:O', 14)

    worksheet_s.write(2, 0, ugettext("Resosconto per anno 2019 e ATC 9 - LIVORNO"))

    # Here we will adding the code to add data
    for idx, perizia in enumerate(periziatiDict):
        row = 4 + idx
        worksheet_s.write(row, 0, perizia['varieta'], cell_center)
        worksheet_s.write(row, 1, findRichiestVarieta(richiesti,perizia['varieta']), cell_center)
        worksheet_s.write_number(row, 2, perizia['SumQuantita'], cell_center)
        worksheet_s.write_number(row, 3, getPrezzoColtVarieta(perizia['varieta']), cell_center)
        worksheet_s.write_number(row, 4, perizia['SumQuantita'] *1.* getPrezzoColtVarieta(perizia['varieta']),
                                 cell_center)
        worksheet_s.write_number(row, 5,
                                 perizia['SumQuantita'] *1.* getPrezzoColtVarieta(perizia['varieta']),
                                 cell_center)

    workbook.close()
    xlsx_data = output.getvalue()
    # xlsx_data contains the Excel file
    return xlsx_data
