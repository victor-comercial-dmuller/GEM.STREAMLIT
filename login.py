import streamlit as st
from database.usuarios import validar_login


def tela_login():

    # ==========================
    # CSS
    # ==========================
    st.markdown("""
    <style>

    .block-container{
        padding-top:2rem;
        padding-bottom:2rem;
        padding-left:2rem;
        padding-right:2rem;
        max-width:1400px;
    }

    [data-testid="stImage"] img{
        width:100%;
        height:650px;
        object-fit:cover;
        border-radius:12px;
    }

    </style>
    """, unsafe_allow_html=True)

    # ==========================
    # CENTRALIZA O CARD
    # ==========================
    from PIL import Image

    @st.cache_resource
    def carregar_imagem():
        return Image.open("imagens/Imagem2.jpg")
    esp_esq, centro, esp_dir = st.columns([1, 8, 1])

    with centro:

        with st.container(border=True):

            lado_1, lado_2 = st.columns([1, 1], gap="large")

            # ===================================
            # LADO ESQUERDO
            # ===================================

            with lado_1:

                st.image(carregar_imagem(), use_container_width=True)

            # ===================================
            # LADO DIREITO
            # ===================================

            with lado_2:

                st.markdown("<br><br><br><br>", unsafe_allow_html=True)

                st.markdown(
                    "<h1 style='text-align:center;'> MeuGem</h1>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    "<p style='text-align:center;color:gray;'>Sistema de Gestão Musical</p>",
                    unsafe_allow_html=True
                )

                st.markdown("<br>", unsafe_allow_html=True)

                login = st.text_input("Usuário")

                senha = st.text_input(
                    "Senha",
                    type="password"
                )

                st.markdown("<br>", unsafe_allow_html=True)

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

                    # Fallback admin local
                    if (
                        not usuario
                        and login == "admin"
                        and senha == "admin123"
                    ):

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