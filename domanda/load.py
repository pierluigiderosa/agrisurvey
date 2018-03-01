# -*- coding: utf-8 -*-
import os
from django.contrib.gis.utils import LayerMapping
from .models import CatastaleSmall, catastale_new, quadranti

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


catastale_shp = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'catastale_small.shp'))
catastale_shp_new = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'catastale_new.shp'))
quadranti_shp =  os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'quadranti.shp'))

def run(verbose=True):
    lm = LayerMapping(CatastaleSmall, catastale_shp, catastale_small_mapping,
                      transform=False, encoding='iso-8859-1')

    lm.save(strict=True, verbose=verbose)

def run_new(verbose=True):
    datadir='/media/pierluigi/LENOVO1/lavori/63_agrisurvey/CATASTO_VETT'
    shp = ['a564','a632','a633','b036','b406','b507','B626','b684','B794','b962','c101','c529','c540','d299','d403','d575','d583']
    for i in range(len(shp)):
        catastale_shp_new = os.path.join(datadir,shp[i]+'.shp')
        lm = LayerMapping(catastale_new, catastale_shp_new, catastale_new_mapping,
                          transform=False, encoding='iso-8859-1')

        lm.save(strict=True, verbose=verbose)


def run_quadranti(verbose=True):
    lm = LayerMapping(quadranti, quadranti_shp, quadranti_mapping,
                      transform=False, encoding='iso-8859-1')

    lm.save(strict=True, verbose=verbose)
