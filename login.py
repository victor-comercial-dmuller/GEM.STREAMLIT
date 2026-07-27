import streamlit as st

from database.usuarios import validar_login


def tela_login():

    # Criando espaço lateral para centralizar
    col_esq, col_login, col_dir = st.columns([1, 2, 1])


    with col_login:

        st.title("🔐 Login")

        st.caption("Acesso para o painel de gestão de turmas e aulas.")


        login = st.text_input("Usuário")

        senha = st.text_input(
            "Senha",
            type="password"
        )


        if st.button(
            "Entrar",
            use_container_width=True
        ):

            if not login or not senha:

                st.warning(
                    "Por favor, preencha usuário e senha."
                )

                return


            try:

                usuario = validar_login(
                    login,
                    senha
                )

            except Exception as e:

                st.error(
                    f"Erro de conexão com o banco de dados: {e}"
                )

                return


            # Fallback admin local (caso banco esteja vazio)
            if not usuario and login == "admin" and senha == "admin123":

                usuario = {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "nome": "Administrador",
                    "perfil": "ADMIN",
                    "login": "admin",
                    "status": "ATIVO"
                }


            if usuario:

                st.session_state.usuario = usuario
                st.session_state.logado = True
                st.session_state.boas_vindas_vista = False

                st.success(
                    "Login realizado com sucesso!"
                )

                st.rerun()


            else:

                st.error(
                    "Usuário ou senha inválidos."
                )