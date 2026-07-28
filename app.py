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
# FUNÇÃO PARA ESCONDER SIDEBAR
# ==========================

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
    ])

    with st.sidebar:

        st.success(f"Olá, {usuario['nome']}")

        st.write(f"Perfil: {usuario['perfil']}")

        st.markdown("---")

        st.subheader("FERRAMENTAS")

        st.markdown("---")

        if st.button(
            "🚪 Sair",
            use_container_width=True
        ):
            st.session_state.clear()
            st.rerun()

    pg.run()