import pandas as pd
import re

def read_google_sheets(link):
    try:
        # Extrai o ID da planilha
        id_match = re.search(r"/d/([a-zA-Z0-9-_]+)", link)
        gid_match = re.search(r"gid=(\d+)", link)

        if not id_match:
            raise ValueError("❌ Não foi possível encontrar o ID da planilha no link.")

        sheet_id = id_match.group(1)
        gid = gid_match.group(1) if gid_match else "0"

        # Constrói o link de exportação CSV
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        
        # Lê a planilha
        df = pd.read_csv(csv_url)
        print("Validando dados de login")
        return df

    except Exception as e:
        print(f" Erro ao ler ao validar dados de login: {e}")
        return None


def login_manager(usuario,senha):
    try:
            df = read_google_sheets('https://docs.google.com/spreadsheets/d/1y1MwGwrjl6hNoeWadZyBPmZsJkTarjGpujwlEUq0uc0/edit?usp=sharing')

            if df is None:
                return {'error': 'Erro ao processar login, fale com o seu administrador'}

            usuario = usuario.lower()
            # Verifica se o usuario está na coluna 'usuario' (ajuste conforme o usuario da coluna na planilha)
            usuario = df[df['USUARIO'].str.lower() == usuario]
    
            # Se o usuario não for encontrado, retorna erro
            if usuario.empty:
                return {'result': False}

            # Verifica se a senha na coluna ao lado (por exemplo, 'senha') bate
            senha_correta = usuario['SENHA'].values[0]  # Ajuste 'senha' conforme o nome da coluna na planilha
            if senha == senha_correta:
                return {'result': True}
            else:
                return {'result': False}

    except Exception as e:
        return {'error': f'Erro ao processar login, fale com o seu administrador'}
    
    