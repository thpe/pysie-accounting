"""The PySIE module"""
import re
from datetime import datetime
import pandas as pd

def is_int(x):
    """ returns true if value is int """
    success = True
    try:
        int(x)
    except ValueError:
        success = False
    return success


class PySIE:
    """ class for handling SIE data """
    def __init__(self):
        """ init """
        self.lines = []
        self.flagga = 0
        self.program = "\"pysie-accounting\" 0.1"
        self.sietyp = 4
        self.format = 'PC8'
        self.orgnr = '1234'
        self.fnamn = 'AB'
        self.dftrans = None
        self.filename = None
        self.sru = None
        self.dfrar = None
        self.dfub = None
        self.dfib = None
        self.dfres = None
        self.verifikat = None
        self.sie_encoding = 'utf8'#"CP437"
#        self.sie_encoding = 'CP437'
        #self.gen = f'{datetime.now():%Y%m%d}u'

        self.kontoplan = 'BAS2014'
    def write_sie4(self, fname):
        """ writing a SIE4 file with the class content """
        with open(fname, 'w', encoding=self.sie_encoding) as fil:
            fil.write(f'#FLAGGA {self.flagga}\n')
            fil.write(f'#PROGRAM {self.program}\n')
            fil.write(f'#FORMAT {self.format}\n')
            fil.write(f'#GEN {datetime.now():%Y%m%d}\n')
            fil.write('#SIETYP 4\n')
            fil.write(f'#ORGNR {self.orgnr}\n')
            fil.write(f'#FNAMN "{self.fnamn}"\n')
            for row in self.dfrar.itertuples():
                year = row.Year
                start = int(row.Start)
                stop = int(row.Stop)
                fil.write(f'#RAR {year} {start} {stop}\n')
            fil.write(f'#KPTYP {self.kontoplan}\n')
            for row in self.sru.itertuples():
                konto = row[0]
                sru = row[1]
                name = row[2]
                fil.write(f'#KONTO {konto} "{name}"\n')
                fil.write(f'#SRU {konto} {sru}\n')
            for row in self.dfib.itertuples():
                year = row.Year
                konto = row.Konto
                balance = row.Balance
                fil.write(f'#IB {year} {konto} {balance:.2f}\n')
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
                fil.write(f'#VER "V" "{key}" {value[0]} "{value[1]}" {value[2]}\n')
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

    def open(self, filename):
        """ open and load SIE4 file """
        self.filename = filename

        with open(self.filename, encoding=self.sie_encoding) as fil:
            for row in fil:
                self.lines.append(row)

        re_orgnr  = re.compile(r'#ORGNR (\d+)')
        re_fnamn  = re.compile(r'#FNAMN "(.*)"')
        re_sru    = re.compile(r'#SRU (\d+) (\d+)')
        re_name   = re.compile(r'#KONTO (\d+) "(.*)"')
        re_rar    = re.compile(r'#RAR (-?\d+) (\d+) (\d+)')
        re_ib     = re.compile(r'#IB (-?\d+) (\d+) (-?\d+\.\d+)')
        re_ub     = re.compile(r'#UB (-?\d+) (\d+) (-?\d+\.\d+)')
        re_res    = re.compile(r'#RES (-?\d+) (\d+) (-?\d+\.\d+)')
        re_verif  = re.compile(r'#VER "(.*)" "(\d+)" (\d+) "(.*)" (\d+)')
        re_trans  = re.compile(r'#TRANS (\d+) {(.*)} (-?\d+.?\d*)')

        df1   = pd.DataFrame(columns=['Konto', 'SRU'])
        df2   = pd.DataFrame(columns=['Konto', 'Name'])
        dfrar = pd.DataFrame(columns=['Year', 'Start', 'Stop'])
        dfub  = pd.DataFrame(columns=['Year', 'Konto', 'Balance'])
        dfib  = pd.DataFrame(columns=['Year', 'Konto', 'Balance'])
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
                    dfrow = pd.DataFrame({'Konto': int(rematch.group(1)),
                                        'SRU': int(rematch.group(2))}, index=[0])
                    df1 = pd.concat([df1, dfrow], ignore_index=True)
                rematch = re_name.search(row)
                if rematch:
                    dfrow = pd.DataFrame({'Konto': int(rematch.group(1)),
                                        'Name': rematch.group(2)}, index=[0])
                    df2 = pd.concat([df2, dfrow], ignore_index=True)

                # years
                rematch = re_rar.search(row)
                if rematch:
                    dfrow = {'Year': rematch.group(1),
                           'Start': int(rematch.group(2)),
                           'Stop': float(rematch.group(3))}
                    dfrow = pd.DataFrame(dfrow, index=[0])
                    dfrar = pd.concat([dfrar, dfrow], ignore_index=True)

                # outgoing balance
                rematch = re_ub.search(row)
                if rematch:
                    dfrow = {'Year': rematch.group(1),
                           'Konto': int(rematch.group(2)),
                           'Balance': float(rematch.group(3))}
                    dfrow = pd.DataFrame(dfrow, index=[0])
                    dfub = pd.concat([dfub, dfrow], ignore_index=True)

                # incoming balance
                rematch = re_ib.search(row)
                if rematch:
                    dfrow = {'Year': rematch.group(1),
                           'Konto': int(rematch.group(2)),
                           'Balance': float(rematch.group(3))}
                    dfrow = pd.DataFrame(dfrow, index=[0])
                    dfib = pd.concat([dfib, dfrow], ignore_index=True)

                rematch = re_res.search(row)
                if rematch:
                    dfrow = {'Year': rematch.group(1),
                           'Konto': int(rematch.group(2)),
                           'Balance': float(rematch.group(3))}
                    dfrow = pd.DataFrame(dfrow, index=[0])
                    dfres = pd.concat([dfres, dfrow], ignore_index=True)
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
        self.sru = dfm.copy()
        # RAR
        self.dfrar = dfrar

        dfub = dfub.merge(right=dfm, on=['Konto'])
        dfub = dfub.merge(right=self.dftrans, on=['SRU'])
        self.dfub = dfub
        dfib = dfib.merge(right=dfm, on=['Konto'])
        dfib = dfib.merge(right=self.dftrans, on=['SRU'])
        self.dfib = dfib
        dfres = dfres.merge(right=dfm, on=['Konto'])
        dfres = dfres.merge(right=self.dftrans, on=['SRU'])
        self.dfres = dfres
    def shift_year(self, df):
        """ shfit the given dataframe by one year """
        rest = df.loc[df['Year'] == '0'].copy(deep=True)
        df['Year'] = df['Year'].apply(lambda x: int(x) - 1)
        df = pd.concat([rest, df], ignore_index=True)
        return df

    def new_year(self):
        """ initialize a new year """
        self.dfrar['Year'] = self.dfrar['Year'].apply(lambda x: int(x) - 1)
        self.dfrar.index = self.dfrar.index + 1
        self.dfrar = pd.concat([pd.DataFrame([[0,self.dfrar.loc[1]['Start']+10000,
                                                 self.dfrar.loc[1]['Stop'] +10000]],
                               columns=self.dfrar.columns), self.dfrar], ignore_index=True)
        self.dfub  = self.shift_year(self.dfub)
        self.dfib  = self.shift_year(self.dfib)
        self.dfres = self.shift_year(self.dfres)

        self.verifikat = {}

    def next_verifikat_number(self):
        vnr = 0
        for key,value in self.verifikat.items():
            if int(key) > vnr:
                vnr = int(key)
        vnr += 1
        return vnr

    def is_balance_account(self, kontonr):
        """ returns true if the kontonr is a balance account, balanskonto """
        return kontonr < 3000

    def is_result_account(self, kontonr):
        """ returns true if the kontonr is a result account, resultkonto """
        return not self.is_balance_account(kontonr)

    def update_account(self, kontonr, value):
        if self.is_balance_account(kontonr):
            self.update_balance(kontonr, value)
        else:
            self.update_result(kontonr, value)

    def update_balance(self, kontonr, value):
        """ add value to balance account with number kontonr """
        self.dfub.loc[(self.dfub['Year']== '0') & (self.dfub['Konto'] == kontonr), 'Balance'] += value
        return

    def update_result(self, kontonr, value):
        """ add value to result account with number kontonr """
        self.dfres.loc[(self.dfres['Year']== '0') & (self.dfres['Konto'] == kontonr), 'Balance'] += value
        return

    def add_verifikat(self, text, trans, date, series='V'):
        """ add a verifikat """
        vnr = self.next_verifikat_number()
        self.verifikat[vnr] = (date, text, datetime.now().strftime("%Y%m%d"),
                               trans)

        for t in trans:
            self.update_account(t[0], t[2])



    def sum_result(self):
        """ returns the sum of the result table """
        return self.dfres['Balance'].sum()

    def get_balance(self, kontonr, year = '0'):
        """ returns the balance of a account for a year """
        if self.is_balance_account(kontonr):
            return self.dfub.loc[(self.dfub['Year']== year) & (self.dfub['Konto'] == kontonr), 'Balance']
        return self.dfres.loc[(self.dfres['Year']== year) & (self.dfres['Konto'] == kontonr), 'Balance']
