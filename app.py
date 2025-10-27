import pandas as pd
import streamlit as st
import io
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

# --- CONFIGURAÇÃO DAS FASES ---
FASES_LIST = [
    'INSCRIÇÃO: REALIZADA', 
    '1 FASE: DOCUMENTAÇÃO', 
    '2 FASE: REUNIAO GESTÃO', 
    '3 FASE: APROVADOS', 
    '4 FASE: ALINHAMENTO INICIO'
]

# --- FUNÇÕES DE BACK-END ---

@st.cache_data(ttl=600) # Cache de 10 minutos
def carregar_dados_sharepoint():
    """Baixa o arquivo do SharePoint e carrega no pandas."""
    try:
        # 1. Lê as credenciais seguras do Streamlit Secrets
        base_url = st.secrets["SHAREPOINT_URL"]
        site_url = base_url + st.secrets["SHAREPOINT_SITE"]
        file_url = st.secrets["SHAREPOINT_FILE_PATH"]
        user = st.secrets["SHAREPOINT_USER"]
        password = st.secrets["SHAREPOINT_PASS"]

        # 2. Autentica no SharePoint
        ctx = ClientContext(site_url).with_credentials(UserCredential(user, password))
        
        # --- INÍCIO DA CORREÇÃO DO BUG ---
        
        # 3. Cria um "arquivo em memória" (buffer) para receber os dados
        buffer = io.BytesIO() 
        
        # 4. Baixa o arquivo do SharePoint e salva DENTRO do buffer
        ctx.web.get_file_by_server_relative_url(file_url).download(buffer).execute_query()
        
        # 5. "Rebobina" o buffer para o início para que o pandas possa lê-lo
        buffer.seek(0)
        
        # 6. Carrega os bytes do buffer no pandas e retorna o DataFrame
        df = pd.read_excel(buffer) 
        return df
        
        # --- FIM DA CORREÇÃO DO BUG ---
        
    except Exception as e:
        # Se der erro, mostra uma mensagem clara
        st.error(f"Erro ao conectar ou ler o arquivo do SharePoint: {e}")
        st.error("Por favor, verifique se os 5 valores no Streamlit Secrets estão corretos (URL, Site, Caminho, Usuário e Senha). Se o erro persistir, o caminho do arquivo pode estar incorreto.")
        return None

def buscar_status(df, nome_digitado):
    """Função de back-end para buscar o status do candidato."""
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
# (O restante do código continua exatamente igual)

st.set_page_config(page_title="Status do Processo", layout="centered")
st.title("Consulta de Status do Candidato")

df_candidatos = carregar_dados_sharepoint()

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