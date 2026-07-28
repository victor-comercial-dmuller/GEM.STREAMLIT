import streamlit as st


# =====================================================
# GERADOR DE ACORDES
# =====================================================

def renderizar_gerador_acordes():

    st.subheader("🎸 Gerador de Acordes")


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


    acordes = {

        "Maior":
            [0, 4, 7],

        "Menor":
            [0, 3, 7],

        "7":
            [0, 4, 7, 10],

        "Maj7":
            [0, 4, 7, 11],

        "Menor 7":
            [0, 3, 7, 10],

        "Sus2":
            [0, 2, 7],

        "Sus4":
            [0, 5, 7],

        "Diminuto":
            [0, 3, 6],

        "Aumentado":
            [0, 4, 8]

    }



    col1, col2 = st.columns(2)


    with col1:

        nota_base = st.selectbox(
            "🎵 Nota fundamental",
            notas
        )


    with col2:

        tipo_acorde = st.selectbox(
            "🎼 Tipo de acorde",
            list(acordes.keys())
        )



    if st.button(
        "Gerar Acorde",
        use_container_width=True
    ):


        intervalos = acordes[tipo_acorde]


        indice = notas.index(nota_base)


        resultado = []


        for intervalo in intervalos:

            nota = notas[
                (indice + intervalo) % 12
            ]

            resultado.append(nota)



        nome_acorde = nota_base + " " + tipo_acorde


        st.divider()


        st.success(
            f"Acorde: {nome_acorde}"
        )


        # ===========================
        # NOTAS DO ACORDE
        # ===========================

        st.markdown(
            "### 🎵 Notas que formam o acorde"
        )


        st.write(
            " → ".join(resultado)
        )



        # ===========================
        # GRAUS
        # ===========================

        st.markdown(
            "### 📚 Estrutura"
        )


        graus = [
            "Tônica",
            "Terça",
            "Quinta",
            "Sétima"
        ]


        tabela = []


        for i, nota in enumerate(resultado):

            tabela.append(
                {
                    "Função": graus[i],
                    "Nota": nota
                }
            )


        st.table(
            tabela
        )



        # ===========================
        # CAMPO VIOLÃO
        # ===========================

    


        st.info(
            mostrar_diagrama_acorde(nome_acorde)
        )

def mostrar_diagrama_acorde(nome_acorde):

    diagramas = {


        "C Maior": [
            "E |---X---",
            "A |---3---",
            "D |---2---",
            "G |---0---",
            "B |---1---",
            "e |---0---",
        ],


        "D Maior": [
            "E |---X---",
            "A |---X---",
            "D |---0---",
            "G |---2---",
            "B |---3---",
            "e |---2---",
        ],


        "E Maior": [
            "E |---0---",
            "A |---2---",
            "D |---2---",
            "G |---1---",
            "B |---0---",
            "e |---0---",
        ],


        "G Maior": [
            "E |---3---",
            "A |---2---",
            "D |---0---",
            "G |---0---",
            "B |---0---",
            "e |---3---",
        ],


        "A Maior": [
            "E |---X---",
            "A |---0---",
            "D |---2---",
            "G |---2---",
            "B |---2---",
            "e |---0---",
        ],


        "C Menor": [
            "E |---X---",
            "A |---3---",
            "D |---5---",
            "G |---5---",
            "B |---4---",
            "e |---3---",
        ],


        "E Menor": [
            "E |---0---",
            "A |---2---",
            "D |---2---",
            "G |---0---",
            "B |---0---",
            "e |---0---",
        ],


        "A Menor": [
            "E |---X---",
            "A |---0---",
            "D |---2---",
            "G |---2---",
            "B |---1---",
            "e |---0---",
        ],


    }


    if nome_acorde in diagramas:

        st.markdown(
            "### 🎸 Diagrama do Violão"
        )


        st.code(
            "\n".join(
                diagramas[nome_acorde]
            )
        )


    else:

        st.info(
            "Diagrama ainda não cadastrado para este acorde."
        )