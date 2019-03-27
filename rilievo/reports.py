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
    page_number_text = "%d" % (doc.page)
    canvas.drawCentredString(
        0.75 * inch,
        0.75 * inch,
        page_number_text
    )
    canvas.restoreState()

def report_singolo_platypus(id,nome,cognome,agricoltore,danno,anagrafica,rilievi):
    tf=tempfile.NamedTemporaryFile()

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
        "Dati dell'agricoltore che ha fatto domanda",
        styles['Heading1']))
    dettagli_agricoltore = [['Luogo di nascita', str(agricoltore.luogoNascita)],
                            ['data di nascita',agricoltore.dataNascita],
                            ['pec',agricoltore.pec],
                            ['telefono',agricoltore.telefono],
                            ['Residenza',agricoltore.viaResidenza],
                            ['comune di residenza',agricoltore.ComuneRes],
                            ['P. Iva',agricoltore.PIva],
                            ['nome azienda',agricoltore.azNome],
                            ['località azienda',agricoltore.azLoc],
                            ['Comune azienda',agricoltore.azComune]
                            ]
    t = Table(dettagli_agricoltore, 2 * [5.5 * cm], len(dettagli_agricoltore)  * [1 * cm], hAlign='LEFT')
    Story.append(t)
    Story.append(Spacer(2 * cm, 2 * cm))
    Story.append(Paragraph(
        "Dati inseriti nella domanda",
        styles['Heading1']))
    danno_inserito = [['Coltura',danno.coltura],
                      ['varietà',danno.varieta],
                      ['Tipologia di piante',danno.TipoPiante],
                      ['Polizza assicurativa',danno.polizza],
                      ['Azienda biologica',danno.biologica],
                      ['iban',danno.iban],
                      ['data inserimento domanda',str(danno.data_ins.day)+'/'+str(danno.data_ins.month)+'/'+str(danno.data_ins.year)]
                      ]
    t = Table(danno_inserito, 2 * [5.5 * cm], len(danno_inserito) * [1 * cm], hAlign='LEFT')
    Story.append(t)
    Story.append(PageBreak())

    Story.append(Paragraph(
        "Rilievo svolto da %s %s" %(danno.Rilevatore.first_name,danno.Rilevatore.last_name),
        styles['Heading1']))
    Story.append(Paragraph(
        "Anagrafica",
        styles['Heading2']))
    #prendo la firma
    img = utils.ImageReader(anagrafica.Firma.path)
    width = 5 * cm
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    Firma = Image(anagrafica.Firma.path, width=width, height=(width * aspect))
    anagrafica_tabella = [['mappale',anagrafica.mappa],
                          ['Rappresentante aziendale',anagrafica.Rapp_Az],
                          ['Documento rappresentante',anagrafica.Rapp_Az_documento],
                          ['Denominazione azienda',anagrafica.Az_Ag_denominazione],
                          ['Titolo di possesso',anagrafica.Az_Ag_possesso],
                          ['indirizzo',anagrafica.Az_Ag_indirizzo]
                          ]
    t = Table(anagrafica_tabella, 2 * [5.5 * cm], len(anagrafica_tabella) * [1 * cm], hAlign='LEFT')
    Story.append(t)
    Story.append(Paragraph(
        "Firma",
        styles['Normal']))
    Firma.hAlign = 'CENTER'
    Story.append(Firma)
    Story.append(Spacer(2 * cm, 2 * cm))

    Story.append(Paragraph(
        "Elenco dei rilievi singoli",
        styles['Heading2']))
    count=1
    for rilievo in rilievi:
        rilievo_data=[
                      ['Opere di prevenzione',rilievo.OperePrevenzione],
                      ['Comune',rilievo.comune],
                      ['coltura',rilievo.coltura],
                      ['Localizzazione fondo',rilievo.Localizzazione_fondo],
                      ['produzione media',rilievo.prod_media],
                      ['Superficie totale',rilievo.Sup_totale],
                      ['Prima specie',rilievo.Specie1],
                      ['Seconda specie',rilievo.Specie2],
                      ['Superficie danneggiata',rilievo.Sup_danneggiata],
                      ['Percentuale danno',rilievo.perc_danno],
                      ['particella', rilievo.particelle],
                      ['foglio',rilievo.foglio],
                    ['varietà',rilievo.varieta]
                      ]
        t = Table(rilievo_data, 2 * [5.5 * cm], len(rilievo_data) * [1 * cm], hAlign='LEFT')
        Story.append(Paragraph(
            "Rilievo %s" % count,
            styles['Heading4']))
        Story.append(HRFlowable(width=20*cm, thickness=0.2, color=colors.grey))

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
