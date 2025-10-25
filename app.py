import pandas as pd
import streamlit as st
import io
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

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

@st.cache_data(ttl=600) # Cache de 10 minutos
def carregar_dados_sharepoint():
    """Baixa o arquivo do SharePoint e carrega no pandas."""
    try:
        # 1. Lê as credenciais seguras do Streamlit Secrets
        # O Streamlit vai buscar os valores que você colou no painel "Secrets"
        base_url = st.secrets["SHAREPOINT_URL"]
        site_url = base_url + st.secrets["SHAREPOINT_SITE"]
        file_url = st.secrets["SHAREPOINT_FILE_PATH"]
        user = st.secrets["SHAREPOINT_USER"]
        password = st.secrets["SHAREPOINT_PASS"]

        # 2. Autentica no SharePoint
        ctx = ClientContext(site_url).with_credentials(UserCredential(user, password))
        
        # 3. Baixa o arquivo em memória
        file_response = ctx.web.get_file_by_server_relative_url(file_url).download().execute_query()
        
        # 4. Lê o conteúdo do arquivo (bytes)
        file_bytes = file_response.content
        
        # 5. Carrega os bytes no pandas e retorna o DataFrame
        df = pd.read_excel(io.BytesIO(file_bytes))
        return df
        
    except Exception as e:
        # Se der erro, mostra uma mensagem clara
        st.error(f"Erro ao conectar ou ler o arquivo do SharePoint: {e}")
        st.error("Por favor, verifique se os 5 valores no Streamlit Secrets estão corretos (URL, Site, Caminho, Usuário e Senha).")
        return None

def buscar_status(df, nome_digitado):
    """Função de back-end para buscar o status do candidato."""
    if df is None:
        return None
        
    nome_digitado_lower = nome_digitado.strip().lower()
    candidato_encontrado_info = None
    
    # Procura o nome em todas as colunas de fase
    for fase in FASES_LIST:
        try:
            # Garante que estamos comparando strings
            matches = df[df[fase].astype(str).str.lower().str.contains(nome_digitado_lower)]
            if not matches.empty:
                # Se encontrar, salva a informação e para a busca
                candidato_encontrado_info = {
                    'nome': matches.iloc[0][fase],
                    'fase': fase
                }
                break # Para a busca assim que encontrar o primeiro
        except KeyError:
            # Se a coluna (ex: "3 FASE: APROVADOS") não existir no Excel, avisa e continua
            st.warning(f"Aviso: A coluna '{fase}' não foi encontrada na planilha Excel.")
            continue
            
    return candidato_encontrado_info

# --- INTERFACE GRÁFICA (FRONT-END) ---

# Configuração da página (nome na aba do navegador)
st.set_page_config(page_title="Status do Processo", layout="centered")

# Título principal
st.title("Consulta de Status do Candidato")

# Carrega os dados (do SharePoint)
df_candidatos = carregar_dados_sharepoint()

# Só executa o resto se os dados foram carregados com sucesso
if df_candidatos is not None:
    # Campo para digitar o nome
    nome_candidato = st.text_input("Digite o nome do Candidato:")
    
    # Botão de busca
    if st.button("Buscar"):
        if not nome_candidato:
            st.warning("Por favor, digite o nome de um candidato.")
        else:
            # Chama a função de busca
            resultado = buscar_status(df_candidatos, nome_candidato)
            
            if resultado:
                # Se achou, mostra os resultados
                fase_atual = resultado['fase']
                nome_oficial = resultado['nome']
                index_atual = FASES_LIST.index(fase_atual)

                st.header(f"Status para: {nome_oficial}")

                # Loop para criar a trilha de status (✔️ para concluído, ⚪ para pendente)
                for i, nome_fase in enumerate(FASES_LIST):
                    if i <= index_atual:
                        st.success(f"✔️ {nome_fase}")
                    else:
                        st.info(f"⚪ {nome_fase}")

                # Se estiver na última fase, mostra a mensagem de parabéns
                if fase_atual == FASES_LIST[-1]:
                    st.balloons() # Efeito de balões
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
                # Se não achou
                st.error("O candidato não foi encontrado na base de dados.")