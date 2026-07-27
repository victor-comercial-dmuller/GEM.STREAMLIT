import streamlit as st


def tela_boas_vindas():

    usuario = st.session_state.usuario
    nome = usuario.get("nome", "Usuário")
    perfil = usuario.get("perfil", "—")


    col_esq, col_centro, col_dir = st.columns([1, 2, 1])


    with col_centro:

        st.title(
            f"🎉 Bem-vindo(a), {nome}!"
        )

        st.divider()


        st.markdown(
            f"""
            ### 👤 Perfil
            {perfil}

            ### 📚 Sistema
            Você está conectado ao sistema de Gestão de Turmas e Aulas.
            """
        )


        st.divider()


        if st.button(
            "🚀 Ir para o Dashboard",
            use_container_width=True,
            type="primary"
        ):

            st.session_state.boas_vindas_vista = True
            st.rerun()