""" tests for pysie """
import pysie_accounting.pysie as pysie

def test_read():
    """ test file read """
    p = pysie.PySIE()
    p.open_trans('data/trans.csv')
    p.open('data/data-utf.se')
