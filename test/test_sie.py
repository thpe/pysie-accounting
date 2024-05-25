""" tests for pysie """
from pysie_accounting import pysie

def test_read():
    """ test file read """
    p = pysie.PySIE()
    p.open_trans('data/trans.csv')
    p.open('data/data-utf.se')
