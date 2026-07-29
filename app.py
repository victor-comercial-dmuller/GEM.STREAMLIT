import streamlit as st

from login import tela_login
from boas_vindas import tela_boas_vindas

st.set_page_config(
    page_title="Gestão de Turmas e Aulas",
    layout="wide"
)


# ==========================
# ESTADO DA SESSÃO
# ==========================

if "logado" not in st.session_state:
    st.session_state.logado = False

if "boas_vindas_vista" not in st.session_state:
    st.session_state.boas_vindas_vista = False


# ==========================
# FUNÇÃO PARA ESCONDER SIDEBAR/ESTILIZAR
# ==========================
# ==========================
# ESTILO MENU LATERAL
# ==========================

def estilizar_menu():

    st.markdown(
        """
        <style>

        /* Fundo da sidebar */
        [data-testid="stSidebar"] {

            background: linear-gradient(
                180deg,
                #0F4C81 0%,
                #2563EB 100%
            );

        }


        /* Texto geral da sidebar */
        [data-testid="stSidebar"] * {

            color: white;

        }


        /* Botões da sidebar */
        [data-testid="stSidebar"] button {

            background-color: rgba(255,255,255,0.12);

            border-radius: 12px;

            border: none;

            transition: 0.3s;

        }


        /* Hover dos botões */
        [data-testid="stSidebar"] button:hover {

            background-color: rgba(255,255,255,0.25);

        }


        /* Títulos */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {

            color: white;

        }


        </style>
        """,
        unsafe_allow_html=True
    )


def esconder_sidebar():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }

        [data-testid="collapsedControl"] {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ==========================
# LOGIN
# ==========================

if not st.session_state.logado:

    esconder_sidebar()
    tela_login()


# ==========================
# BOAS-VINDAS
# ==========================

elif not st.session_state.boas_vindas_vista:

    esconder_sidebar()
    tela_boas_vindas()


# ==========================
# SISTEMA
# ==========================

else:

    usuario = st.session_state.usuario

    # aplica o estilo do menu
    estilizar_menu()


    # A navegação só existe depois do login
    pg = st.navigation([
        st.Page("pages/cadastros.py", title="Cadastros", icon="📋"),
        st.Page("pages/planejamento.py", title="Planejamento", icon="📍"),
        st.Page("pages/aulas.py", title="Aulas", icon="📚"),
        st.Page("pages/metronomo.py", title="Metrônomo", icon="🎚️"),
        st.Page("pages/afinador.py", title="Afinador", icon="🔊"),
        st.Page("pages/pajela.py", title="Pajela", icon="📝"),
        st.Page("pages/p_minimo.py", title="Programa mínimo", icon="📖"),
        st.Page("pages/avaliacoes.py", title="Avaliações", icon="✅"),
        st.Page("pages/dashboard.py", title="Dashboard", icon="📊"),
        st.Page("pages/ferramentas.py", title="Ferramentas", icon="🛠️"),
    ])


    with st.sidebar:

        

        st.warning(f"Olá, {usuario['nome']}")

        st.success(f"             Perfil: {usuario['perfil']}")

        st.markdown("---")


        if st.button(
            "🚪 Sair",
            use_container_width=True
        ):
            st.session_state.clear()
            st.rerun()


    pg.run()
