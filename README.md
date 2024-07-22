pysie-accounting
================
This package contains tools to parse and read SIE files.

Currently there is only support for SIE type 4.

SIE files
=========
These files are used in accounting within Sweden. The file format is published
by [SIE gruppen](https://sie.se). Type 1-4 are text based, type 5 is xml
based. The SIE4 file is coded with codepage 437.


Example
=======

```python

import pysie_accounting.pysie as pysie
import sys


# open SIE file
p = pysie.PySIE ()
p.open_trans (sys.argv[2])
p.open (sys.argv[1])

# create a new accounting year
p.new_year()

# add some verifikat

last_year = p.get_balance(2099)
p.add_verifikat("Omföring av årets resultat", [(2098, "", last_year), (2099, "", -last_year)], "20230101")

account_fee = 1234
p.add_verifikat("Bankavgifter", [(1930, "", -account_fee), (6570, "", account_fee)], "20230101")

sum_result = p.sum_result()
p.add_verifikat("Omföring av årets resultat", [(2099, "", sum_result), (8999, "", -sum_result)], "20231231")


# print a pivot based on SRU
pivot = p.dfres.pivot_table(index='SRU',columns='Year',values='Balance')
print(pivot)

# write the updated file
p.write_sie4("test.se")


```
