import re
import numpy as np
import pandas as pd
from datetime import datetime


class PySIE:
    def __init__(self):
        print('init')
        self.lines = []
        self.flagga = 0
        self.program = "\"pysie-accounting\" 0.1"
        self.sietyp = 4
        self.rar_nr = 0
        self.rar_start = 0
        self.rar_stop = 0
        self.format = 'PC8'
        self.orgnr = '1234'
        self.fnamn = 'AB'
        #self.gen = f'{datetime.now():%Y%m%d}u'

        self.kontoplan = 'BAS2014'
    def writeSIE4(self, fname):
        f = open(fname, 'w')
        f.write(f'#FLAGGA {self.flagga}\n')
        f.write(f'#PROGRAM {self.program}\n')
        f.write(f'#FORMAT {self.format}\n')
        f.write(f'#GEN {datetime.now():%Y%m%d}\n')
        f.write(f'#SIETYP 4\n')
        f.write(f'#ORGNR {self.orgnr}\n')
        f.write(f'#FNAMN "{self.fnamn}"\n')
        f.write(f'#RAR {self.rar_nr} {self.rar_start} {self.rar_stop}\n')
        f.write(f'#KPTYP {self.kontoplan}\n')
        for r in self.sru.itertuples():
            k = r[0]
            s = r[1]
            n = r[2]
            f.write(f'#KONTO {k} "{n}"\n')
            f.write(f'#SRU {k} {s}\n')
        for r in self.dfub.itertuples():
            y = r.Year
            k = r.Konto
            b = r.Balance
            f.write(f'#UB {y} {k} {b}\n')
        for r in self.dfres.itertuples():
            y = r.Year
            k = r.Konto
            b = r.Balance
            f.write(f'#RES {y} {k} {b}\n')
        f.close()

    def open_trans(self, filename):
        self.dftrans = pd.read_csv(filename, dtype={'SRU': int,
                                                    'Ink2': str})
        self.dftrans = self.dftrans[['SRU', 'Ink2']]
        print('external matching')
        print(self.dftrans)

    def open(self, filename):
        self.filename = filename

        with open(self.filename) as f:
            for r in f:
                self.lines.append(r)

        re_orgnr  = re.compile(r'#ORGNR (\d+)')
        re_fnamn  = re.compile(r'#FNAMN "(.*)"')
        re_sru  = re.compile(r'#SRU (\d+) (\d+)')
        re_name = re.compile(r'#KONTO (\d+) "(.*)"')
        re_ub   = re.compile(r'#UB (-?\d+) (\d+) (-?\d+\.\d+)')
        re_res  = re.compile(r'#RES (-?\d+) (\d+) (-?\d+\.\d+)')

        df1   = pd.DataFrame(columns=['Konto', 'SRU'])
        df2   = pd.DataFrame(columns=['Konto', 'Name'])
        dfub  = pd.DataFrame(columns=['Year', 'Konto', 'Balance'])
        dfres = pd.DataFrame(columns=['Year', 'Konto', 'Balance'])
        for r in self.lines:
            m = re_orgnr.search(r)
            if m:
                self.orgnr = m.group(1)
            m = re_fnamn.search(r)
            if m:
                self.fnamn = m.group(1)
            m = re_sru.search(r)
            if m:
                row = pd.DataFrame({'Konto': int(m.group(1)), 'SRU': int(m.group(2))}, index=[0])
                df1 = pd.concat([df1, row], ignore_index=True)
            m = re_name.search(r)
            if m:
                row = pd.DataFrame({'Konto': int(m.group(1)), 'Name': m.group(2)}, index=[0])
                df2 = pd.concat([df2, row], ignore_index=True)
            m = re_ub.search(r)
            if m:
                row = {'Year': m.group(1),
                       'Konto': int(m.group(2)),
                       'Balance': float(m.group(3))}
                row = pd.DataFrame(row, index=[0])
                dfub = pd.concat([dfub, row], ignore_index=True)
            m = re_res.search(r)
            if m:
                row = {'Year': m.group(1),
                       'Konto': int(m.group(2)),
                       'Balance': float(m.group(3))}
                row = pd.DataFrame(row, index=[0])
                dfres = pd.concat([dfres, row], ignore_index=True)

        # df1 = df1.set_index('Konto')
        # df2 = df2.set_index('Konto')

        df = df1.merge(df2)
        df = df.convert_dtypes()
#        dfub = dfub.convert_dtypes()
#        dfres = dfres.convert_dtypes()
        df = df.set_index('Konto')
        print('SIE matching')
        print(df)
        self.sru = df.copy()
        dfub = dfub.merge(right=df, on=['Konto'])
        dfub = dfub.merge(right=self.dftrans, on=['SRU'])
        print(dfub)
        self.dfub = dfub
        dfres = dfres.merge(right=df, on=['Konto'])
        dfres = dfres.merge(right=self.dftrans, on=['SRU'])
        print(dfres)
        self.dfres = dfres
