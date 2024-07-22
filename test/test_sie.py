""" tests for pysie """
from pysie_accounting import pysie

def test_read():
    """ test file read """
    sie = pysie.PySIE()
    sie.open_trans('data/trans.csv')
    sie.open('data/data-utf.se')

def test_add_verifikat():
    """ test file read """
    sie = pysie.PySIE()
    sie.open_trans('data/trans.csv')
    sie.open('data/data-utf.se')
    sie.add_verifikat("Bankavgifter", [(1930, "", -1234), (6570, "", 1234)], "20220101")

    assert sie.sum_result() == 1234

def test_new_year():
    """ test file read """
    sie = pysie.PySIE()
    sie.open_trans('data/trans.csv')
    sie.open('data/data-utf.se')
    sie.add_verifikat("Bankavgifter", [(1930, "", -1234), (6570, "", 1234)], "20220101")

    sie.new_year()
    print(sie.dfres)
    assert sie.sum_result() == 0
