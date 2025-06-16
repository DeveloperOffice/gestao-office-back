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
        return df

    except Exception as e:
        print(f" Erro ao ler ao validar dados de login: {e}")
        return None

def login_manager(usuario, senha):
    try:
        df = read_google_sheets(
            "https://docs.google.com/spreadsheets/d/1y1MwGwrjl6hNoeWadZyBPmZsJkTarjGpujwlEUq0uc0/edit?usp=sharing"
        )

        if df is None:
            return {"error": "Erro ao processar login, fale com o seu administrador"}

        usuario = usuario.lower()
        usuario_row = df[df["USUARIO"].str.lower() == usuario]

        if usuario_row.empty:
            return {"result": False}

        senha_correta = usuario_row["SENHA"].values[0]
        if senha == senha_correta:
            # Extrai os dados desejados
            user_data = {
                "USUARIO": str(usuario_row["USUARIO"].values[0]),
                "NOME": str(usuario_row["NOME"].values[0]),
                "EMAIL": str(usuario_row["EMAIL"].values[0]),
                "ID": int(usuario_row["ID"].values[0]),
            }
            return {"result": True, "user": user_data}
        else:
            return {"result": False}

    except Exception as e:
        return {"error": "Erro ao processar login, fale com o seu administrador"}
