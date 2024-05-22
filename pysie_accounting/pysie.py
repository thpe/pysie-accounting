"""The PySIE module"""
import re
from datetime import datetime
import pandas as pd


class PySIE:
    """ class for handling SIE data """
    def __init__(self):
        """ init """
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
        self.dftrans = None
        self.filename = None
        self.sru = None
        self.dfub = None
        self.dfres = None
        self.verifikat = None
        #self.gen = f'{datetime.now():%Y%m%d}u'

        self.kontoplan = 'BAS2014'
    def write_sie4(self, fname):
        """ writing a SIE4 file with the class content """
        with open(fname, 'w', encoding='utf8') as fil:
            fil.write(f'#FLAGGA {self.flagga}\n')
            fil.write(f'#PROGRAM {self.program}\n')
            fil.write(f'#FORMAT {self.format}\n')
            fil.write(f'#GEN {datetime.now():%Y%m%d}\n')
            fil.write('#SIETYP 4\n')
            fil.write(f'#ORGNR {self.orgnr}\n')
            fil.write(f'#FNAMN "{self.fnamn}"\n')
            fil.write(f'#RAR {self.rar_nr} {self.rar_start} {self.rar_stop}\n')
            fil.write(f'#KPTYP {self.kontoplan}\n')
            for row in self.sru.itertuples():
                konto = row[0]
                sru = row[1]
                name = row[2]
                fil.write(f'#KONTO {konto} "{name}"\n')
                fil.write(f'#SRU {konto} {sru}\n')
            for row in self.dfub.itertuples():
                year = row.Year
                konto = row.Konto
                balance = row.Balance
                fil.write(f'#UB {year} {konto} {balance:.2f}\n')
            for row in self.dfres.itertuples():
                year = row.Year
                konto = row.Konto
                balance = row.Balance
                fil.write(f'#RES {year} {konto} {balance:.2f}\n')
            for key,value in self.verifikat.items():
                fil.write(f'#VER "V" "{key}" {value[0]} {value[1]} {value[2]}\n')
                fil.write('{\n')
                for line in value[3]:
                    fil.write(f'\t#TRANS {line[0]} ')
                    fil.write('{')
                    fil.write(f'{line[1]}')
                    fil.write('}')
                    fil.write(f' {float(line[2]):.2f}\n')
                fil.write('}\n')
            fil.close()

    def open_trans(self, filename):
        """ open a translation file """
        self.dftrans = pd.read_csv(filename, dtype={'SRU': int,
                                                    'Ink2': str})
        self.dftrans = self.dftrans[['SRU', 'Ink2']]
        print('external matching')
        print(self.dftrans)

    def open(self, filename):
        """ open and load SIE4 file """
        self.filename = filename

        with open(self.filename, encoding='utf8') as fil:
            for row in fil:
                self.lines.append(row)

        re_orgnr  = re.compile(r'#ORGNR (\d+)')
        re_fnamn  = re.compile(r'#FNAMN "(.*)"')
        re_sru  = re.compile(r'#SRU (\d+) (\d+)')
        re_name = re.compile(r'#KONTO (\d+) "(.*)"')
        re_ub   = re.compile(r'#UB (-?\d+) (\d+) (-?\d+\.\d+)')
        re_res  = re.compile(r'#RES (-?\d+) (\d+) (-?\d+\.\d+)')
        re_verif  = re.compile(r'#VER "(.*)" "(\d+)" (\d+) "(.*)" (\d+)')
        re_trans  = re.compile(r'#TRANS (\d+) {(.*)} (-?\d+.?\d*)')

        df1   = pd.DataFrame(columns=['Konto', 'SRU'])
        df2   = pd.DataFrame(columns=['Konto', 'Name'])
        dfub  = pd.DataFrame(columns=['Year', 'Konto', 'Balance'])
        dfres = pd.DataFrame(columns=['Year', 'Konto', 'Balance'])
        self.verifikat = {}
        state_trans = False
        vnr = 0
        for row in self.lines:
            if not state_trans:
                rematch = re_orgnr.search(row)
                if rematch:
                    self.orgnr = rematch.group(1)
                rematch = re_fnamn.search(row)
                if rematch:
                    self.fnamn = rematch.group(1)
                rematch = re_sru.search(row)
                if rematch:
                    row = pd.DataFrame({'Konto': int(rematch.group(1)),
                                        'SRU': int(rematch.group(2))}, index=[0])
                    df1 = pd.concat([df1, row], ignore_index=True)
                rematch = re_name.search(row)
                if rematch:
                    row = pd.DataFrame({'Konto': int(rematch.group(1)),
                                        'Name': rematch.group(2)}, index=[0])
                    df2 = pd.concat([df2, row], ignore_index=True)
                rematch = re_ub.search(row)
                if rematch:
                    row = {'Year': rematch.group(1),
                           'Konto': int(rematch.group(2)),
                           'Balance': float(rematch.group(3))}
                    row = pd.DataFrame(row, index=[0])
                    dfub = pd.concat([dfub, row], ignore_index=True)
                rematch = re_res.search(row)
                if rematch:
                    row = {'Year': rematch.group(1),
                           'Konto': int(rematch.group(2)),
                           'Balance': float(rematch.group(3))}
                    row = pd.DataFrame(row, index=[0])
                    dfres = pd.concat([dfres, row], ignore_index=True)
                rematch = re_verif.search(row)
                if rematch:
                    #ser = rematch.group(1)
                    lnr = rematch.group(2)
                    date = rematch.group(3)
                    text = rematch.group(4)
                    date1 = rematch.group(5)

                    self.verifikat[lnr] = (date, text, date1, [])
                    vnr = lnr
                    state_trans = True
            else:
                if row[0] == '}':
                    state_trans = False
                    continue
                rematch = re_trans.search(row)
                if rematch:
                    konto = rematch.group(1)
                    links = rematch.group(2)
                    amount = rematch.group(3)
                    self.verifikat[vnr][3].append((konto,links,amount))



        # df1 = df1.set_index('Konto')
        # df2 = df2.set_index('Konto')

        dfm = df1.merge(df2)
        dfm = dfm.convert_dtypes()
#        dfub = dfub.convert_dtypes()
#        dfres = dfres.convert_dtypes()
        dfm = dfm.set_index('Konto')
        print('SIE matching')
        print(dfm)
        self.sru = dfm.copy()
        dfub = dfub.merge(right=dfm, on=['Konto'])
        dfub = dfub.merge(right=self.dftrans, on=['SRU'])
        print(dfub)
        self.dfub = dfub
        dfres = dfres.merge(right=dfm, on=['Konto'])
        dfres = dfres.merge(right=self.dftrans, on=['SRU'])
        print(dfres)
        self.dfres = dfres
        print(self.verifikat)
