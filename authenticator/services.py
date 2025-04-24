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
        print("✅ Planilha carregada com sucesso!")
        return df

    except Exception as e:
        print(f"❌ Erro ao ler a planilha: {e}")
        return None
