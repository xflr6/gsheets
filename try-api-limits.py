#!/usr/bin/env python3
# try-api-limits.py - investigate api limits with larger sheets

from __future__ import print_function

import logging

from gsheets import Sheets

SHEET_ID = '1lnDyc-Elf_y6_Bz22_9AgTKu4aJCFUoBuPCaxyAFMkA'


logging.basicConfig(format='[%(levelname)s@%(name)s] %(message)s',
                    level=logging.DEBUG)


sheets = Sheets.from_files('~/client_secrets.json', '~/gsheets-storage.json')

s = sheets[SHEET_ID]

for w in s.sheets:
    print(w.title, w.nrows, w.ncols, sep='\t')
