# -*- coding: utf-8 -*-
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm,mm,inch
from reportlab.lib import utils
from reportlab.lib import colors
from django.core.files.storage import FileSystemStorage
from reportlab.platypus.flowables import HRFlowable
import tempfile

def report_singolo(response,id_danno):
    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")
    p.drawString(50, 100, "Domanda %s" % id_danno)

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 10)
    canvas.setTitle('Report Agrisurvey')
    page_number_text = "pagina %d" % (doc.page)
    canvas.drawCentredString(
        0.75 * inch,
        0.75 * inch,
        page_number_text
    )
    canvas.restoreState()

def report_singolo_platypus(id,nome,cognome,agricoltore,danno,anagrafica,rilievi):
    tf=tempfile.NamedTemporaryFile()

    stile_tabella=TableStyle([
        ('TEXTCOLOR', (0, 0), (0, -1), colors.blue),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ])

    doc = SimpleDocTemplate(tf.name,
                            pagesize=A4,
                            rightMargin=1 * cm,
                            leftMargin=1 * cm,
                            topMargin=2 * cm,
                            bottomMargin=2 * cm
                            )
    styles = getSampleStyleSheet()
    Story = []
    #inizio la generazione dell'oggetto del report
    P0 = Paragraph("<b>Report rilievo</b><br/><font size=12><i>Agrisurvey</i></font>",
                   styles['Heading1'])
    P1 = Paragraph('''<font size=8>Richiedente:%s %s<br/></font>
    	                  <br/>
    	                  <u><font size=10 color=red>Codice Fiscale : %s</font></u>
    	               ''' % (nome,cognome,agricoltore.CF), styles['Normal'])
    data = [[P0, ''],
            [P1, '']]
    t = Table(data, 2 * [9.5 * cm], 2 * [1.7 * cm])
    t.setStyle(TableStyle([('GRID', (0, 0), (1, -2), 1, colors.grey),
                           ('BOX', (0, 0), (1, -1), 2, colors.black),
                           ('SPAN', (1, -1), (-1, -1))]))
    Story.append(t)
    Story.append(Spacer(2 * cm, 2 * cm))
    Story.append(Paragraph(
        "Dati inseriti nel portale in fase di domanda",
        styles['Heading1']))
    Story.append(HRFlowable(width=20*cm, thickness=0.2, color=colors.darkgrey))
    Story.append(Paragraph(
        "Dati dell'agricoltore che ha fatto domanda",
        styles['Heading2']))
    dettagli_agricoltore = [['Luogo di nascita', str(agricoltore.luogoNascita)],
                            ['data di nascita',agricoltore.dataNascita],
                            ['Codice Fiscale', agricoltore.CF],
                            ['pec',agricoltore.pec],
                            ['telefono',agricoltore.telefono],
                            ['Referente aziendale',agricoltore.Referente],
                            ['Telf.referente aziendale', agricoltore.RefTel],
                            ['Residenza',agricoltore.viaResidenza],
                            ['comune di residenza',agricoltore.ComuneRes],
                            ['P. Iva',agricoltore.PIva],
                            ['nome azienda',agricoltore.azNome],
                            ['località azienda',agricoltore.azLoc],
                            ['Azienda biologica',agricoltore.biologica],
                            ['Iban',agricoltore.iban],
                            ['Comune azienda',agricoltore.azComune]
                            ]
    t = Table(dettagli_agricoltore, 2 * [5.5 * cm], len(dettagli_agricoltore)  * [1 * cm], hAlign='LEFT')
    t.setStyle(stile_tabella)
    Story.append(t)
    Story.append(Spacer(2 * cm, 2 * cm))
    Story.append(Paragraph(
        "Dati inseriti nella domanda di danno",
        styles['Heading2']))
    danno_inserito = [['Foglio catastale',danno.foglio],
                      ['Particella catastale', danno.particella],
                      ['Superficie totale particelle ettari',danno.SumTot],
                      ['Superficie seminativa particella ettari', danno.SumSem],
                      ['% stimata del danno', danno.PercDanno],
                      ['Produzione prevista nella particella',danno.Produzione],
                      ['% produzione persa',danno.PerProdPersa],
                      ['ipotetico valore del danno stimato dal dichiarante',danno.ValoreDanno],
                      ['numero piante danneggiate',danno.NumPianteDan],
                      ['Selvaggina che ha causato i danni alla coltura',danno.SelvagginaSem],
                      ['Opere di protezione presenti',danno.OpereProtezione],
                      ['Coltura',danno.coltura],
                      ['varietà',danno.varieta],
                      ['Tipologia di piante',danno.TipoPiante],
                      ['Polizza assicurativa',danno.polizza],
                      ['Azienda biologica',danno.biologica],
                      ['iban',danno.iban],
                      ['data inserimento domanda',str(danno.data_ins.day)+'/'+str(danno.data_ins.month)+'/'+str(danno.data_ins.year)],
                      ['Note',danno.note]
                      ]
    if danno.data_danno is not None:
        danno_inserito.append(['Data danno presunta',
         str(danno.data_danno.day) + '/' + str(danno.data_danno.month) + '/' + str(danno.data_danno.year)])

    t = Table(danno_inserito, 2 * [8.5 * cm], len(danno_inserito) * [1 * cm], hAlign='LEFT')
    t.setStyle(stile_tabella)
    Story.append(t)
    Story.append(PageBreak())

    Story.append(Paragraph(
        "Rilievo svolto da %s %s" %(danno.Rilevatore.first_name,danno.Rilevatore.last_name),
        styles['Heading1']))
    Story.append(HRFlowable(width=20 * cm, thickness=0.2, color=colors.darkgrey))
    Story.append(Paragraph(
        "Anagrafica",
        styles['Heading2']))
    #prendo la firma agricoltore
    img = utils.ImageReader(anagrafica.Firma.path)
    width = 5 * cm
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    Firma = Image(anagrafica.Firma.path, width=width, height=(width * aspect))

    #prendo firma rilevatore
    img_ril = utils.ImageReader(anagrafica.Firma_rilevatore.path)
    width = 5 * cm
    iw, ih = img_ril.getSize()
    aspect = ih / float(iw)
    Firma_ril = Image(anagrafica.Firma_rilevatore.path, width=width, height=(width * aspect))

    anagrafica_tabella = [['mappale',anagrafica.mappa],
                          ['Rappresentante aziendale',anagrafica.Rapp_Az],
                          ['Documento rappresentante',anagrafica.Rapp_Az_documento],
                          ['Denominazione azienda',anagrafica.Az_Ag_denominazione],
                          ['Titolo di possesso',anagrafica.Az_Ag_possesso],
                          ['indirizzo',anagrafica.Az_Ag_indirizzo],
                          ['data di sopralluogo',str(anagrafica.data_sopralluogo.day)+'/'+str(anagrafica.data_sopralluogo.month)+'/'+str(anagrafica.data_sopralluogo.year)],
                          ['Tecnico incaricato',anagrafica.tecnico_incaricato]
                          ]
    t = Table(anagrafica_tabella, 2 * [5.5 * cm], len(anagrafica_tabella) * [1 * cm], hAlign='LEFT')
    t.setStyle(stile_tabella)
    Story.append(t)
    Story.append(Paragraph(
        "Firma Agricoltore/Rappresentante aziendale",
        styles['Normal']))
    Firma.hAlign = 'CENTER'
    Story.append(Firma)
    Story.append(Spacer(0.5 * cm, 0.5 * cm))
    Story.append(Paragraph(
        "Firma Tecnico incaricato",
        styles['Normal']))
    Firma_ril.hAlign = 'CENTER'
    Story.append(Spacer(0.5 * cm, 0.5 * cm))
    Story.append(Firma_ril)

    Story.append(Paragraph(
        "Elenco dei rilievi singoli",
        styles['Heading2']))
    count=1
    for rilievo in rilievi:
        rilievo_data=[
            ['Opere di prevenzione',rilievo.OperePrevenzione],
            ['Altre opere di prevenzione',rilievo.OperePrevenzione_altro],
            ['Comune',rilievo.comune],
            ['coltura',rilievo.coltura],
            ['Altra coltura',rilievo.coltura_altro],
            ['Localizzazione fondo',rilievo.Localizzazione_fondo],
            ['Altra localizzazione del fondo',rilievo.Localizzazione_fondo_altro],
            ['produzione media',rilievo.prod_media],
            ['Superficie totale',rilievo.Sup_totale],
            ['Prima specie',rilievo.Specie1],
            ['Prima specie altro',rilievo.specie1_altro],
            ['% danno specie 1',rilievo.perc_specie1],
            ['Seconda specie',rilievo.Specie2],
            ['Seconda specie altro',rilievo.Specie2_altro],
            ['% danno specie 2',rilievo.perc_specie2],
            ['Superficie danneggiata',rilievo.Sup_danneggiata],
            ['Percentuale danno',rilievo.perc_danno],
            ['particella', rilievo.particelle],
            ['foglio',rilievo.foglio],
            ['varietà',rilievo.varieta],
            ['Stato vegetazionele e fitosanitario',rilievo.statovegsanitario],
            ['Numero di piante da sostituire',rilievo.numpiantesostituire],
            ['Funzionalita Prevenzione',rilievo.FunzionalitaPrevenzione],
            ['Coltura biologica',rilievo.colturabiologica],
            ['superficie di risemina',rilievo.superficierisemina],
            ['quantità di prodotto perduto',rilievo.quantitaprodotto],

            ['note: ',rilievo.note_colturali]
        ]
        t = Table(rilievo_data, 2 * [7.0 * cm], len(rilievo_data) * [1 * cm], hAlign='LEFT')
        t.setStyle(stile_tabella)
        Story.append(Paragraph(
            "Rilievo %s" % count,
            styles['Heading4']))
        Story.append(HRFlowable(width=20*cm, thickness=0.2, color=colors.grey))
        Story.append(Spacer(1 * cm, 1 * cm))

        Story.append(t)
        Story.append(Spacer(2 * cm, 2 * cm))
        count+=1

    #fine generazione oggetto report----


    doc.build(
        Story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )
    fs = FileSystemStorage("/tmp")
    with open(tf.name) as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report %s.pdf"' % id
        return response

    return response
