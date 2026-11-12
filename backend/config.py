import os
import sys
from pathlib import Path

NOME_APP = 'Quimativa'

# Quando empacotado pelo PyInstaller, os arquivos ficam em sys._MEIPASS
# (o frontend deve ser incluÃ­do no build como a pasta "frontend").
EMPACOTADO = getattr(sys, 'frozen', False)

if EMPACOTADO:
    BASE_DIR = Path(sys._MEIPASS)
    FRONTEND_DIR = BASE_DIR / 'frontend'
else:
    BASE_DIR = Path(__file__).resolve().parent
    FRONTEND_DIR = BASE_DIR.parent / 'frontend'

# Dados do usuÃ¡rio (banco SQLite) ficam fora do executÃ¡vel para nÃ£o se perderem
DATA_DIR = Path(os.environ.get('APPDATA', Path.home())) / NOME_APP
DB_PATH = DATA_DIR / 'quimativa.db'


def garantir_diretorios():
    DATA_DIR.mkdir(parents=True, exist_ok=True)