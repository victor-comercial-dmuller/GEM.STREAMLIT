import streamlit as st


def tela_boas_vindas():

    usuario = st.session_state.usuario
    nome = usuario.get("nome", "Usuário")
    perfil = usuario.get("perfil", "—")


    st.markdown(
        """
        <style>

        .block-container {
            padding-top: 80px;
        }


        div[data-testid="stVerticalBlockBorderWrapper"] {

            border-radius: 20px;

            padding: 40px;

            box-shadow: 0 5px 25px rgba(0,0,0,0.08);

            background-color: white;

        }

        </style>
        """,
        unsafe_allow_html=True
    )


    col1, col2, col3 = st.columns([1,2,1])


    with col2:

        with st.container(border=True):

            st.markdown(
                "<h1 style='text-align:center;'>🎵 Meu GEM</h1>",
                unsafe_allow_html=True
            )


            st.markdown(
                f"""
                <h2 style='text-align:center;'>
                Bem-vindo(a), {nome}!
                </h2>
                """,
                unsafe_allow_html=True
            )


            st.write("")


            st.markdown(
                f"""
                <div style="text-align:center; font-size:18px;">

                👤 <b>Perfil:</b><br>
                {perfil}


                📚 <b>Sistema:</b><br>
                Gestão de Ensinos Musicais

                </div>
                """,
                unsafe_allow_html=True
            )


            if st.button(
                "🚀 Acessar APP",
                use_container_width=True,
                type="primary"
            ):

                st.session_state.boas_vindas_vista = True
                st.rerun()