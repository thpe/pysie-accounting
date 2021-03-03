import re
import pandas as pd

class PySIE:
    def __init__ (self):
        print ('init')
        self.lines = []
    def open (self, filename):
        self.filename = filename

        with open (self.filename) as f:
            for l in f:
                self.lines.append (l)

        re_sru  = re.compile ('#SRU (\d+) (\d+)')
        re_name = re.compile ('#KONTO (\d+) "(.*)"')
        re_ub   = re.compile ('#UB (-?\d+) (\d+) (-?\d+\.\d+)')
        re_res  = re.compile ('#RES (-?\d+) (\d+) (-?\d+\.\d+)')

        df1   = pd.DataFrame (columns=['Konto', 'SRU'])
        df2   = pd.DataFrame (columns=['Konto', 'Name'])
        dfub  = pd.DataFrame (columns=['Year', 'Konto', 'Balance'])
        dfres = pd.DataFrame (columns=['Year', 'Konto', 'Balance'])
        for l in self.lines:
            m = re_sru.search (l)
            if m:
                row = {'Konto':m.group(1), 'SRU':m.group(2)}
                df1 = df1.append(row, ignore_index=True)
            m = re_name.search (l)
            if m:
                row = {'Konto':m.group(1), 'Name':m.group(2)}
                df2 = df2.append(row, ignore_index=True)
            m = re_ub.search (l)
            if m:
                row = {'Year':m.group(1), 'Konto':m.group(2), 'Balance':m.group(3)}
                dfub = dfub.append(row, ignore_index=True)
            m = re_res.search (l)
            if m:
                row = {'Year':m.group(1), 'Konto':m.group(2), 'Balance':m.group(3)}
                dfres = dfres.append(row, ignore_index=True)

        #df1 = df1.set_index('Konto')
        #df2 = df2.set_index('Konto')

        df = df1.merge(df2)
        df = df.set_index('Konto')
        print (df)
        print (dfub)
        print (dfres)


