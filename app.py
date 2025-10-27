import pandas as pd
import streamlit as st
import io

# --- CONFIGURAÇÃO DAS FASES ---
# Lista de fases para a interface
FASES_LIST = [
    'INSCRIÇÃO: REALIZADA', 
    '1 FASE: DOCUMENTAÇÃO', 
    '2 FASE: REUNIAO GESTÃO', 
    '3 FASE: APROVADOS', 
    '4 FASE: ALINHAMENTO INICIO'
]

# --- FUNÇÕES DE BACK-END ---

@st.cache_data(ttl=300) # Cache de 5 minutos
def carregar_dados_google():
    """Baixa o arquivo Excel do Google Drive e carrega no pandas."""
    try:
        # ID do arquivo extraído do NOVO link que você me enviou
        FILE_ID = "121rjo9tpryN6w9gXcigCTRkCwj7LXCEZ" # <--- ID ATUALIZADO
        
        # Constrói a URL de download direto
        download_url = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
        
        # Lê o arquivo Excel diretamente da URL
        df = pd.read_excel(download_url)
        return df
        
    except Exception as e:
        # Se der erro, avisa sobre a permissão de compartilhamento
        st.error(f"Erro ao conectar ou ler o arquivo do Google Drive: {e}")
        st.error("Verifique se o arquivo no Google Drive está com o compartilhamento 'Qualquer pessoa com o link pode ver'.")
        return None

def buscar_status(df, nome_digitado):
    """Função de back-end para buscar o status do candidato."""
    # Esta função continua EXATAMENTE igual
    if df is None:
        return None
        
    nome_digitado_lower = nome_digitado.strip().lower()
    candidato_encontrado_info = None
    
    for fase in FASES_LIST:
        try:
            matches = df[df[fase].astype(str).str.lower().str.contains(nome_digitado_lower)]
            if not matches.empty:
                candidato_encontrado_info = {
                    'nome': matches.iloc[0][fase],
                    'fase': fase
                }
                break 
        except KeyError:
            st.warning(f"Aviso: A coluna '{fase}' não foi encontrada na planilha Excel.")
            continue
            
    return candidato_encontrado_info

# --- INTERFACE GRÁFICA (FRONT-END) ---
st.set_page_config(page