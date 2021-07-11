#!/usr/bin/env python3
# try-example.py - import gsheets here and try example code w/ logging

import logging

from gsheets import Sheets

SHEET_ID = '1dR13B3Wi_KJGUJQ0BZa2frLAVxhZnbz0hpwCcWSvb20'

WORKSHEET_IDS = [0, 1747240182, 894548711]

WORKSHEET_NAMES = ['Tabellenblatt1', 'Tabellenblatt2', 'Tabellenblatt3']


logging.basicConfig(format='[%(levelname)s@%(name)s] %(message)s',
                    level=logging.INFO)


sheets = Sheets.from_files('~/client_secrets.json', '~/gsheets-storage.json')

print(sheets[SHEET_ID])

url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}'
s = sheets.get(url)
print(s)

print(s.find(WORKSHEET_NAMES[1]))

print(s.sheets[0]['A1'])

print(s[WORKSHEET_IDS[1]].at(row=1, col=1))

s.sheets[1].to_csv('Spam.csv', encoding='utf-8', dialect='excel')

csv_name = lambda infos: '%(title)s - %(sheet)s.csv' % infos
s.to_csv(make_filename=csv_name)

print(s.find(WORKSHEET_NAMES[1]).to_frame(index_col='spam'))
