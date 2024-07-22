""" tests for pysie """
from pysie_accounting import pysie

def test_read():
    """ test file read """
    p = pysie.PySIE()
    p.open_trans('data/trans.csv')
    p.open('data/data-utf.se')

def test_add_verifikat():
    """ test file read """
    p = pysie.PySIE()
    p.open_trans('data/trans.csv')
    p.open('data/data-utf.se')
    p.add_verifikat("Bankavgifter", [(1930, "", -1234), (6570, "", 1234)], "20220101")

    assert p.sum_result() == 1234

def test_new_year():
    """ test file read """
    p = pysie.PySIE()
    p.open_trans('data/trans.csv')
    p.open('data/data-utf.se')
    p.add_verifikat("Bankavgifter", [(1930, "", -1234), (6570, "", 1234)], "20220101")

    p.new_year()
    print(p.dfres)
    assert p.sum_result() == 0
