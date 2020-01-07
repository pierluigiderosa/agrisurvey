# -*- coding: utf-8 -*-
import os
from django.contrib.gis.utils import LayerMapping
from .models import CatastaleSmall, catastale_new, quadranti,quandranti_livorno

catastale_small_mapping = {
    'part' : 'PART',
    'sub' : 'SUB',
    'foglio' : 'FOGLIO',
    'idseq' : 'IDSEQ',
    'mpoly' : 'MULTIPOLYGON',
}

catastale_new_mapping = {
    'part' : 'PART',
    'foglio' : 'FOGLIO',
    'comune' : 'comune',
    'mpoly' : 'MULTIPOLYGON',
}


quadranti_mapping = {
    'fid' : 'fid',
    'left' : 'left',
    'top' : 'top',
    'right' : 'right',
    'bottom' : 'bottom',
    'mpoly' : 'MULTIPOLYGON',
}

imagery_mapping = {
    'location' : 'location',
    'num' : 'num',
    'geom' : 'MULTIPOLYGON',
}



catastale_shp = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'catastale_small.shp'))
catastale_shp_new = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'catastale_new.shp'))
quadranti_shp =  os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'quadranti.shp'))
quadranti_livorno_shp = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'imagery.shp'))

def run(verbose=True):
    lm = LayerMapping(CatastaleSmall, catastale_shp, catastale_small_mapping,
                      transform=False, encoding='iso-8859-1')

    lm.save(strict=True, verbose=verbose)

def run_new(verbose=True):
    #path on server
    #datadir='/home/ucavini/LIVORNO_CATASTALE'
    datadir='/media/pierluigi/LENOVO/lavori/63_agrisurvey/LIVORNO_CATASTALE'
    shp_firenze = ['a564','a632','a633','b036','b406','b507','B626','b684','B794','b962','c101','c529','c540','d299','d403','d575','d583']
    shp = ['A852','B509','B553','B669','B685','C044','C415','C869','E625','E680','E930','E931','G687','G912','H297','H305','H570','I390','I454','L019']
    for i in range(len(shp)):
        catastale_shp_new = os.path.join(datadir,shp[i]+'.shp')
        lm = LayerMapping(catastale_new, catastale_shp_new, catastale_new_mapping,
                          transform=False, encoding='iso-8859-1')

        lm.save(strict=True, verbose=verbose)


def run_quadranti(verbose=True):
    lm = LayerMapping(quadranti, quadranti_shp, quadranti_mapping,
                      transform=False, encoding='iso-8859-1')

    lm.save(strict=True, verbose=verbose)


def run_quadranti_livorno(verbose=True):
    lm = LayerMapping(quandranti_livorno, quadranti_livorno_shp, imagery_mapping,
                      transform=False, encoding='iso-8859-1')

    lm.save(strict=True, verbose=verbose)