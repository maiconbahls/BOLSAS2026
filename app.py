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
st.set_page_config(page_title="Status do Processo", layout="centered")
st.title("Consulta de Status do Candidato")

df_candidatos = carregar_dados_google()

if df_candidatos is not None:
    nome_candidato = st.text_input("Digite o nome do Candidato:")
    
    if st.button("Buscar"):
        if not nome_candidato:
            st.warning("Por favor, digite o nome de um candidato.")
        else:
            resultado = buscar_status(df_candidatos, nome_candidato)
            
            if resultado:
                fase_atual = resultado['fase']
                nome_oficial = resultado['nome']
                index_atual = FASES_LIST.index(fase_atual)
                st.header(f"Status para: {nome_oficial}")

                for i, nome_fase in enumerate(FASES_LIST):
                    if i <= index_atual:
                        st.success(f"✔️ {nome_fase}")
                    else:
                        st.info(f"⚪ {nome_fase}")

                if fase_atual == FASES_LIST[-1]:
                    st.balloons() 
                    st.markdown(
                        """
                        <div style="padding: 15px; border: 2px solid #00008B; border-radius: 10px; background-color: #F0F8FF;">
                        <h2 style="color: #00008B; text-align: center;">PARABÉNS!</h2>
                        <h3 style="color: #00008B; text-align: center;">VOCÊ É O NOVO BOLSISTA DO CICLO 2026</h3>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
            else:
                st.error("O candidato não foi encontrado na base de dados.")
