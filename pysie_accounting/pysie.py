import re
import numpy as np
import pandas as pd


class PySIE:
    def __init__(self):
        print('init')
        self.lines = []

    def open_trans(self, filename):
        self.dftrans = pd.read_csv(filename, dtype={'SRU': int,
                                                    'Ink2': str})
        self.dftrans = self.dftrans[['SRU', 'Ink2']]
        print(self.dftrans)

    def open(self, filename):
        self.filename = filename

        with open(self.filename) as f:
            for r in f:
                self.lines.append(r)

        re_sru  = re.compile(r'#SRU (\d+) (\d+)')
        re_name = re.compile(r'#KONTO (\d+) "(.*)"')
        re_ub   = re.compile(r'#UB (-?\d+) (\d+) (-?\d+\.\d+)')
        re_res  = re.compile(r'#RES (-?\d+) (\d+) (-?\d+\.\d+)')

        df1   = pd.DataFrame(columns=['Konto', 'SRU'])
        df2   = pd.DataFrame(columns=['Konto', 'Name'])
        dfub  = pd.DataFrame(columns=['Year', 'Konto', 'Balance'])
        dfres = pd.DataFrame(columns=['Year', 'Konto', 'Balance'])
        for r in self.lines:
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
        print(df)
        dfub = dfub.merge(right=df, on=['Konto'])
        dfub = dfub.merge(right=self.dftrans, on=['SRU'])
        print(dfub)
        self.dfub = dfub
        dfres = dfres.merge(right=df, on=['Konto'])
        dfres = dfres.merge(right=self.dftrans, on=['SRU'])
        print(dfres)
        self.dfres = dfres
