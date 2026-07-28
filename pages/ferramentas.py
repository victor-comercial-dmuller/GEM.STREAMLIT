import streamlit as st

from ferramentas.escalas import (
    renderizar_gerador_escalas
)

from ferramentas.acordes import (
    renderizar_gerador_acordes
)

from ferramentas.harmonia import (
    renderizar_campo_harmonico
)

from ferramentas.ouvido import (
    renderizar_treinador_ouvido
)

from ferramentas.braco import (
    renderizar_braco_violao
)


from ferramentas.piano import renderizar_piano_virtual

st.set_page_config(
    page_title="Outras Ferramentas",
    page_icon="🎵",
    layout="wide"
)


st.title(
    "Outras Ferramentas Musicais"
)



tab1, tab2, tab3, tab4 ,tab5, tab6= st.tabs(
    [
        "🎼 Escalas",
        "🎸 Acordes",
        "🎹 Harmonia",
        "🎧 Ouvido",
        "🎹 Piano Virtual",
        "🎸 Violão virtual"
    ]
)



with tab1:

    renderizar_gerador_escalas()



with tab2:

    st.info(
        renderizar_gerador_acordes()
    )



with tab3:

    st.info(
        renderizar_campo_harmonico()
    )



with tab4:

    st.info(
        renderizar_treinador_ouvido()
    )

with tab5:
    st.info(
    renderizar_piano_virtual())

with tab6:
    st.info(
    renderizar_braco_violao())