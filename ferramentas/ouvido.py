import streamlit as st
import streamlit.components.v1 as components
import random


# =====================================================
# TREINADOR DE OUVIDO MUSICAL
# =====================================================

def renderizar_treinador_ouvido():

    st.subheader("🎧 Treinador de Ouvido Musical")


    notas = {

        "C": 261.63,
        "C#": 277.18,
        "D": 293.66,
        "D#": 311.13,
        "E": 329.63,
        "F": 349.23,
        "F#": 369.99,
        "G": 392.00,
        "G#": 415.30,
        "A": 440.00,
        "A#": 466.16,
        "B": 493.88

    }



    # ------------------------------
    # Sessão
    # ------------------------------

    if "nota_sorteada" not in st.session_state:

        st.session_state.nota_sorteada = None



    if "acertos" not in st.session_state:

        st.session_state.acertos = 0



    if "erros" not in st.session_state:

        st.session_state.erros = 0



    # ------------------------------
    # Dificuldade
    # ------------------------------

    dificuldade = st.selectbox(
        "🎯 Nível",
        [
            "Iniciante (Notas naturais)",
            "Intermediário (Sustenidos)",
            "Completo"
        ]
    )



    if dificuldade == "Iniciante (Notas naturais)":

        lista_notas = [
            "C",
            "D",
            "E",
            "F",
            "G",
            "A",
            "B"
        ]


    elif dificuldade == "Intermediário (Sustenidos)":

        lista_notas = [
            "C#",
            "D#",
            "F#",
            "G#",
            "A#"
        ]


    else:

        lista_notas = list(notas.keys())



    # ------------------------------
    # Gerar nova nota
    # ------------------------------

    if st.button(
        "🎵 Gerar Nota",
        use_container_width=True
    ):

        st.session_state.nota_sorteada = random.choice(
            lista_notas
        )



    nota = st.session_state.nota_sorteada



    if nota:


        frequencia = notas[nota]



        st.markdown(
            "### 🎧 Ouça e identifique"
        )


        # Áudio usando Web Audio API

        html = f"""

        <script>

        let ctx =
        new(window.AudioContext ||
        window.webkitAudioContext)();



        let osc =
        ctx.createOscillator();



        let gain =
        ctx.createGain();



        osc.frequency.value =
        {frequencia};



        osc.type =
        "sine";



        osc.connect(gain);

        gain.connect(
            ctx.destination
        );



        gain.gain.value =
        0.4;



        osc.start();



        gain.gain.exponentialRampToValueAtTime(
            0.001,
            ctx.currentTime + 8
        );



        osc.stop(
            ctx.currentTime + 5
        );


        </script>

        """



        components.html(
            html,
            height=80
        )



        opcoes = lista_notas.copy()


        random.shuffle(opcoes)



        resposta = st.radio(
            "Qual nota foi tocada?",
            opcoes
        )



        if st.button(
            "Responder",
            use_container_width=True
        ):



            if resposta == nota:


                st.success(
                    f"✅ Correto! Era {nota}"
                )


                st.session_state.acertos += 1



            else:


                st.error(
                    f"❌ Errado! Era {nota}"
                )


                st.session_state.erros += 1



            st.session_state.nota_sorteada = None



    # ------------------------------
    # Placar
    # ------------------------------

    st.divider()


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "✅ Acertos",
            st.session_state.acertos
        )


    with col2:

        st.metric(
            "❌ Erros",
            st.session_state.erros
        )


    with col3:

        total = (
            st.session_state.acertos +
            st.session_state.erros
        )


        aproveitamento = 0

        if total > 0:

            aproveitamento = (
                st.session_state.acertos /
                total
            ) * 100


        st.metric(
            "🎯 Aproveitamento",
            f"{aproveitamento:.0f}%"
        )