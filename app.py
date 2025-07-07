#pip install extra-streamlit-components

import os
import pyodbc
import streamlit as st
from datetime import datetime, timedelta
from extra_streamlit_components import CookieManager

# Inicializa o gerenciador de cookies
cookie_manager = CookieManager()


# Configuração do CSS externo
def load_css():
    try:
        # Tenta carregar o arquivo CSS local
        with open("w3s.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback para um CSS online baseado no W3Schools se o arquivo local não existir
        w3schools_css = """
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f4f4;
            }
            h1, h2, h3 {
                color: #4CAF50;
            }
            .stButton>button {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
            }
            .stTextInput>div>div>input {
                padding: 10px;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
            /* Adicione mais estilos conforme necessário */
        </style>
        """
        st.markdown(w3schools_css, unsafe_allow_html=True)


# Configuração do CSS personalizado
def load_css1():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Configuração da conexão com o SQL Server (mantida igual)
def get_db_connection():
    server = '192.168.0.10'
    database = 'DB_DEV'
    username = 'CTRL'
    password = 'Cury@CA2kV4*!'
    
    try:
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password}'
        )
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Autenticação (mantida igual)
def authenticate_user(username, password):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM Users WHERE Username = ? AND Password = ?", 
                (username, password)
            )
            user = cursor.fetchone()
            conn.close()
            return user is not None
        except Exception as e:
            st.error(f"Erro ao autenticar usuário: {e}")
            return False
    return False

# Verifica se o usuário está autenticado via cookies/session state
def check_authentication():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    # Verifica o cookie primeiro
    auth_cookie = cookie_manager.get(cookie='auth')
    if auth_cookie and not st.session_state['authenticated']:
        st.session_state['authenticated'] = True
        st.session_state['username'] = auth_cookie['username']
        st.rerun()

# Página de Login atualizada
def login_page():
    st.title("Sistema de Controle - Login")
    
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if authenticate_user(username, password):
                # Define cookie de autenticação (validade de 1 dia)
                cookie_manager.set(
                    'auth',
                    {'username': username},
                    expires_at=datetime.now() + timedelta(days=1)
                )
                
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos")

# Logout atualizado
def logout():
    cookie_manager.delete('auth')
    st.session_state['authenticated'] = False
    st.session_state['username'] = None
    st.rerun()



# Página do Menu Principal
def main_menu():
    st.title(f"Bem-vindo, {st.session_state['username']}!")
    st.sidebar.title("Menu")
    
    # Opções do menu
    menu_options = {
        "Dashboard": dashboard_page,
        "Processos": processos_page,
        "Itens": itens_page,
        "Relatórios": relatorios_page,
        "Configurações": configuracoes_page
    }
    
    # Criar menu na sidebar
    selected_option = st.sidebar.radio("Navegação", list(menu_options.keys()))
    
    # Mostrar página selecionada
    menu_options[selected_option]()

# Páginas de conteúdo
def dashboard_page():
    st.header("Dashboard")
    st.write("Visão geral do sistema")
    
    # Exemplo de consulta ao banco de dados
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Users")
            user_count = cursor.fetchone()[0]
            st.metric("Total de Usuários", user_count)
            
            cursor.execute("SELECT COUNT(*) FROM Processes")
            process_count = cursor.fetchone()[0]
            st.metric("Total de Processos", process_count)
            
            conn.close()
        except Exception as e:
            st.error(f"Erro ao consultar dados: {e}")

def processos_page():
    st.header("Gerenciamento de Processos")
    
    # Abas para diferentes operações
    tab1, tab2, tab3 = st.tabs(["Listar", "Adicionar", "Editar"])
    
    with tab1:
        st.subheader("Lista de Processos")
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT ProcessID, ProcessName, Status FROM Processes")
                processes = cursor.fetchall()
                
                if processes:
                    st.table(processes)
                else:
                    st.info("Nenhum processo encontrado")
                
                conn.close()
            except Exception as e:
                st.error(f"Erro ao listar processos: {e}")
    
    with tab2:
        st.subheader("Adicionar Novo Processo")
        with st.form("add_process"):
            process_name = st.text_input("Nome do Processo")
            process_desc = st.text_area("Descrição")
            submit = st.form_submit_button("Salvar")
            
            if submit:
                if process_name:
                    conn = get_db_connection()
                    if conn:
                        try:
                            cursor = conn.cursor()
                            cursor.execute(
                                "INSERT INTO Processes (ProcessName, Description, CreatedBy) VALUES (?, ?, ?)",
                                (process_name, process_desc, st.session_state['username'])
                            )
                            conn.commit()
                            st.success("Processo adicionado com sucesso!")
                            conn.close()
                        except Exception as e:
                            st.error(f"Erro ao adicionar processo: {e}")
                else:
                    st.warning("Nome do processo é obrigatório")

def itens_page():
    st.header("Gerenciamento de Itens")
    st.write("Funcionalidade de gerenciamento de itens será implementada aqui")

def relatorios_page():
    st.header("Relatórios")
    st.write("Funcionalidade de relatórios será implementada aqui")

def configuracoes_page():
    st.header("Configurações do Sistema")
    st.write("Configurações do sistema serão implementadas aqui")



# Estrutura principal atualizada
def main():
    st.set_page_config(
        page_title="Sistema de Controle",
        page_icon=":gear:",
        layout="wide"
    )

    load_css()
    check_authentication()  # Verifica autenticação antes de renderizar
    
    if st.session_state.get('authenticated'):
        main_menu()
    else:
        login_page()

if __name__ == "__main__":
    # Inicializa o cookie manager antes de tudo
    cookie_manager = CookieManager(key='auth_manager')
    main()

    #streamlit run app.py