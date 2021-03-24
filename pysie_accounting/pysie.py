import re
import numpy as np
import pandas as pd


class PySIE:
    def __init__(self):
        print('init')
        self.lines = []

    def open_trans(self, filename):
        self.dftrans = pd.read_csv(filename, dtype={'SRU': np.int,
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
                row = {'Konto': int(m.group(1)), 'SRU': int(m.group(2))}
                df1 = df1.append(row, ignore_index=True)
            m = re_name.search(l)
            if m:
                row = {'Konto': int(m.group(1)), 'Name': m.group(2)}
                df2 = df2.append(row, ignore_index=True)
            m = re_ub.search(l)
            if m:
                row = {'Year': m.group(1),
                       'Konto': int(m.group(2)),
                       'Balance': m.group(3)}
                dfub = dfub.append(row, ignore_index=True)
            m = re_res.search(l)
            if m:
                row = {'Year': m.group(1),
                       'Konto': int(m.group(2)),
                       'Balance': m.group(3)}
                dfres = dfres.append(row, ignore_index=True)

        # df1 = df1.set_index('Konto')
        # df2 = df2.set_index('Konto')

        df = df1.merge(df2)
        df = df.convert_dtypes()
        dfub = dfub.convert_dtypes()
        dfres = dfres.convert_dtypes()
        df = df.set_index('Konto')
        print(df)
        dfub = dfub.merge(right=df, on=['Konto'])
        dfub = dfub.merge(right=self.dftrans, on=['SRU'])
        print(dfub)
        dfres = dfres.merge(right=df, on=['Konto'])
        dfres = dfres.merge(right=self.dftrans, on=['SRU'])
        print(dfres)
