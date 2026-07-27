import streamlit as st

from login import tela_login
from boas_vindas import tela_boas_vindas


st.set_page_config(
    page_title="Gestão de Turmas e Aulas",
    layout="wide"
)

if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.boas_vindas_vista = False

if not st.session_state.logado:
    tela_login()

elif not st.session_state.get("boas_vindas_vista", False):
    tela_boas_vindas()

else:

    ds_usu =usuario = st.session_state.usuario

    st.sidebar.success(f"Olá, {usuario['nome']}")
    st.sidebar.write(f"Perfil: {usuario['perfil']}")

    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

    pg = st.navigation([
        st.Page("pages/cadastros.py", title="Cadastros", icon="📋"),
        st.Page("pages/aulas.py", title="Aulas", icon="📚"),
        st.Page("pages/metronomo.py", title="Metronomo", icon="🎚️"),
        st.Page("pages/planejamento.py", title="Planejamento", icon="📍"),
        st.Page("pages/pajela.py", title="Pajela", icon="📝"),
        st.Page("pages/avaliacoes.py", title="Avaliações", icon="📝"),
        st.Page("pages/dashboard.py", title="Dashboard", icon="📊"),
        st.Page("pages/p_minimo.py", title="Programa mínimo", icon="📝"),
    ])

    pg.run()
