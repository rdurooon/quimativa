"""Configuração central do Quimativa: caminhos e constantes do aplicativo."""
import os
import sys
from pathlib import Path

from platformdirs import user_data_path

NOME_APP = 'Quimativa'
NOME_BANCO = 'quimativa.db'

# Variável de ambiente para trocar a pasta de dados (usada nos testes).
VAR_DATA_DIR = 'QUIMATIVA_DATA_DIR'

# Quando empacotado pelo PyInstaller (onefile), os arquivos do app são extraídos
# em sys._MEIPASS, uma pasta TEMPORÁRIA apagada ao fechar o programa.
# Por isso, nada que o usuário precise guardar (como o banco) pode ficar lá.
EMPACOTADO = getattr(sys, 'frozen', False)

if EMPACOTADO:
    BASE_DIR = Path(sys._MEIPASS)
    BACKEND_DIR = BASE_DIR / 'backend'
    FRONTEND_DIR = BASE_DIR / 'frontend'
else:
    BACKEND_DIR = Path(__file__).resolve().parent
    BASE_DIR = BACKEND_DIR.parent
    FRONTEND_DIR = BASE_DIR / 'frontend'

# Conteúdo oficial (questões-base) distribuído com o software: somente leitura.
PACOTE_BASE_PATH = BACKEND_DIR / 'questoes' / 'dados' / 'pacote_base.json'
ASSETS_BASE_DIR = BACKEND_DIR / 'questoes' / 'assets' / 'base'


def obter_data_dir() -> Path:
    r"""Pasta de dados persistentes do usuário.

    No Windows: C:\Users\<usuario>\AppData\Local\Quimativa
    Pode ser trocada pela variável de ambiente QUIMATIVA_DATA_DIR.
    """
    personalizada = os.environ.get(VAR_DATA_DIR)
    if personalizada:
        return Path(personalizada)
    return user_data_path(NOME_APP, appauthor=False, roaming=False)


def obter_caminho_banco() -> Path:
    """Caminho completo do arquivo SQLite."""
    return obter_data_dir() / NOME_BANCO


def obter_url_banco() -> str:
    """URL de conexão no formato do SQLAlchemy."""
    return f'sqlite:///{obter_caminho_banco().as_posix()}'


def garantir_diretorios() -> Path:
    """Cria a pasta de dados se ainda não existir e devolve o caminho."""
    data_dir = obter_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def obter_assets_dir(origem: str) -> Path:
    """Pasta dos SVGs de cada origem de questão.

    - base: dentro do app (somente leitura);
    - local/remote: na pasta de dados do usuário.
    """
    if origem == 'base':
        return ASSETS_BASE_DIR
    if origem in ('local', 'remote'):
        return obter_data_dir() / 'assets' / origem
    raise ValueError(f'Origem desconhecida: {origem}')
