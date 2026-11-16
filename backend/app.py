import os
import webview

class API:
    def ping(self):
        return 'pong'

    def sair(self):
        for janela in webview.windows:
            janela.destroy()

if __name__ == '__main__':
    api = API()
    
    # 1. Pega o diretório onde o app.py está salvo (backend/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Sobe um nível para a raiz do projeto e aponta para o frontend/home.html
    html_path = os.path.normpath(os.path.join(current_dir, '..', 'frontend', 'home.html'))
    
    # Verificação opcional para depuração no console
    print(f"Procurando HTML em: {html_path}")

    # 3. Cria a janela convertendo o caminho para uma URI de arquivo válida
    window = webview.create_window(
        title='Quimativa',
        url=f'file:///{html_path.replace(os.sep, "/")}',
        js_api=api,
        width=1280,
        height=720,
        resizable=True
    )
    
    webview.start()