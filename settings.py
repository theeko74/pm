"""
Settings of the library pmlib.py
"""

import os

PROGRESS_CHR = 'x'
#PROGRESS_CHR = '\u25CF'

PROGRESS = {
	'Start': PROGRESS_CHR * 1,
	'Progr': PROGRESS_CHR * 2,
	'Budge': PROGRESS_CHR * 3,
	'Contr': PROGRESS_CHR * 4,
	'Sign': PROGRESS_CHR * 5,
	'Done': PROGRESS_CHR * 6
}

TYPE_OF_CONTRACTS = ['R&D', 'aR&D', 'Lic', 'aLic', 'MTA']

WIDTH = 85

WARN_TIME = 7

DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = 'db.json'
DATABASE_PATH = DIR + '/database/' + DATABASE_FILE

WORD_TEMPLATE = 'Templates/Report_template.docx'

WORD_COLOR_CELL = 'd7e2f7'

MAX_LEN_NAME = 15

