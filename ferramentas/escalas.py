import streamlit as st


# =====================================================
# GERADOR DE ESCALAS
# =====================================================

def renderizar_gerador_escalas():

    st.subheader("🎼 Gerador de Escalas Musicais")


    notas = [
        "C",
        "C#",
        "D",
        "D#",
        "E",
        "F",
        "F#",
        "G",
        "G#",
        "A",
        "A#",
        "B"
    ]


    escalas = {

        "Maior":
            [0,2,4,5,7,9,11],

        "Menor Natural":
            [0,2,3,5,7,8,10],

        "Menor Harmônica":
            [0,2,3,5,7,8,11],

        "Pentatônica Maior":
            [0,2,4,7,9],

        "Pentatônica Menor":
            [0,3,5,7,10],

        "Blues":
            [0,3,5,6,7,10],

        "Dórica":
            [0,2,3,5,7,9,10],

        "Mixolídia":
            [0,2,4,5,7,9,10]

    }


    col1, col2 = st.columns(2)


    with col1:

        nota_base = st.selectbox(
            "Escolha a tonalidade",
            notas
        )


    with col2:

        tipo_escala = st.selectbox(
            "Tipo de escala",
            list(escalas.keys())
        )


    if st.button(
        "🎵 Gerar Escala",
        key="gerar_escala"
    ):


        indice = notas.index(nota_base)


        resultado = []


        for grau in escalas[tipo_escala]:

            nota = notas[
                (indice + grau) % 12
            ]

            resultado.append(nota)



        st.success(
            f"Escala {nota_base} {tipo_escala}"
        )


        st.write(
            " → ".join(resultado)
        )


        st.divider()


        st.write("### Graus")


        graus = [
            "I",
            "II",
            "III",
            "IV",
            "V",
            "VI",
            "VII"
        ]


        for i, nota in enumerate(resultado):

            st.write(
                f"{graus[i]} - {nota}"
            )