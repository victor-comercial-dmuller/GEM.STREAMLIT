import streamlit as st


# =====================================================
# CAMPO HARMÔNICO
# =====================================================

def renderizar_campo_harmonico():

    st.subheader("🎹 Campo Harmônico")


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


    col1, col2 = st.columns(2)


    with col1:

        tonalidade = st.selectbox(
            "🎵 Escolha o tom",
            notas
        )


    with col2:

        modo = st.selectbox(
            "Escala",
            [
                "Maior",
                "Menor Natural"
            ]
        )



    if st.button(
        "Gerar Campo Harmônico",
        use_container_width=True
    ):


        # Escala maior
        escala_maior = [
            0,
            2,
            4,
            5,
            7,
            9,
            11
        ]


        # Escala menor natural
        escala_menor = [
            0,
            2,
            3,
            5,
            7,
            8,
            10
        ]



        intervalos = (
            escala_maior
            if modo == "Maior"
            else escala_menor
        )



        acordes_maior = [
            "Maior",
            "Menor",
            "Menor",
            "Maior",
            "Maior",
            "Menor",
            "Diminuto"
        ]


        acordes_menor = [
            "Menor",
            "Diminuto",
            "Maior",
            "Menor",
            "Menor",
            "Maior",
            "Maior"
        ]



        tipos = (
            acordes_maior
            if modo == "Maior"
            else acordes_menor
        )



        graus = [
            "I",
            "II",
            "III",
            "IV",
            "V",
            "VI",
            "VII"
        ]



        tabela = []


        indice = notas.index(tonalidade)



        for i, intervalo in enumerate(intervalos):


            nota = notas[
                (indice + intervalo) % 12
            ]


            simbolo = nota


            if tipos[i] == "Menor":

                simbolo += "m"


            elif tipos[i] == "Diminuto":

                simbolo += "°"



            tabela.append(
                {
                    "Grau": graus[i],
                    "Acorde": simbolo,
                    "Tipo": tipos[i]
                }
            )



        st.divider()


        st.success(
            f"Campo Harmônico de {tonalidade} {modo}"
        )


        st.table(
            tabela
        )



        st.markdown(
            "### 🎶 Progressões famosas"
        )


        if modo == "Maior":

            st.write(
                f"I - V - VI - IV  → {tonalidade} / Música Pop"
            )

            st.write(
                "I - IV - V → Blues e Rock"
            )


        else:

            st.write(
                "i - VI - III - VII"
            )