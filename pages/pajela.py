import streamlit as st
from datetime import datetime
from config import supabase

# ==================================================
# VERIFICAÇÃO DE AUTENTICAÇÃO
# ==================================================

if "usuario" not in st.session_state or not st.session_state.usuario:
    st.info("Faça login para acessar esta página.")
    st.stop()

usuario_logado = st.session_state.usuario
perfil_logado = usuario_logado.get("perfil", "—")

# ==================================================
# FUNÇÕES
# ==================================================


def listar_alunos():
    try:
        resposta = (
            supabase
            .table("usuarios")
            .select("*")
            .order("nome")
            .execute()
        )
        return resposta.data
    except Exception as e:
        st.error(f"Erro ao listar alunos: {e}")
        return []


def listar_alunos_com_isolamento():
    """Carrega alunos aplicando isolamento."""
    try:
        alunos = listar_alunos()
        perfil = usuario_logado.get("perfil", "—")
        localidade_id = usuario_logado.get("localidade_id")
        regiao_id = usuario_logado.get("regiao_id")
        usuario_id = usuario_logado.get("id")

        if perfil in ["ADMIN", "TI"]:
            return alunos

        if perfil == "COORDENADOR REGIONAL":
            return [a for a in alunos if a.get("regiao_id") == regiao_id]

        if perfil == "COORDENADOR LOCAL":
            return [a for a in alunos if a.get("localidade_id") == localidade_id]

        if perfil == "PROFESSOR" or perfil == "AUXILIAR":
            # Vê alunos de sua localidade
            return [a for a in alunos if a.get("localidade_id") == localidade_id]

        if perfil == "ALUNO":
            # Aluno vê apenas a si próprio
            return [a for a in alunos if a.get("id") == usuario_id]

        return alunos
    except Exception as e:
        st.error(f"Erro ao listar alunos com isolamento: {e}")
        return []



def listar_relatos():
    try:
        resposta = (
            supabase
            .table("relatos_dificuldades")
            .select("*")
            .order("data", desc=True)
            .execute()
        )
        return resposta.data
    except Exception as e:
        st.error(f"Erro ao listar relatos: {e}")
        return []



def criar_relato(dados):
    try:
        supabase\
            .table("relatos_dificuldades")\
            .insert(dados)\
            .execute()
        return True
    except Exception as e:
        st.error(f"Erro ao criar relato: {e}")
        return False



def atualizar_status(id_relato, status):
    try:
        supabase\
            .table("relatos_dificuldades")\
            .update({
                "status": status
            })\
            .eq("id", id_relato)\
            .execute()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar status: {e}")
        return False



# ==================================================
# TELA
# ==================================================

def renderizar_relatos():


    st.title(
        "⚠️ Relatos de Dificuldades"
    )


    st.caption(
        "Registre e acompanhe dificuldades dos alunos."
    )


    # ----------------------------
    # NOVO RELATO
    # ----------------------------


    with st.expander(
        "➕ Novo Relato",
        expanded=True
    ):


        alunos = listar_alunos_com_isolamento()


        lista_alunos = {
            a["nome"]: a["id"]
            for a in alunos
        }


        aluno_nome = st.selectbox(
            "Aluno",
            list(lista_alunos.keys())
        )


        id_aluno = lista_alunos[aluno_nome]


        data = st.date_input(
            "Data",
            datetime.now()
        )


        descricao = st.text_area(
            "Descrição do problema ou dificuldade"
        )


        medida = st.text_area(
            "Medida a ser tomada"
        )


        status_relato = st.selectbox(
            "Status",
            [
                "ABERTO",
                "EM ACOMPANHAMENTO",
                "FINALIZADO"
            ],
            format_func=lambda x:
                {
                    "ABERTO": "🔴 Aberto",
                    "EM ACOMPANHAMENTO": "🟡 Em Acompanhamento",
                    "FINALIZADO": "🟢 Finalizado"
                }[x]
        )



        if st.button(
            "💾 Salvar Relato",
            type="primary"
        ):


            if not descricao or not medida:

                st.warning(
                    "Preencha todos os campos."
                )


            else:

                usuario = st.session_state.get("usuario", {})
                usuario_id = usuario.get("id")

                dados = {

                    "id_aluno": id_aluno,

                    "id_professor": usuario_id,

                    "data": str(data),

                    "descricao": descricao,

                    "medida_tomada": medida,

                    "status": status_relato

                }


                if criar_relato(dados):

                    st.success(
                        "Relato salvo!"
                    )

                    st.rerun()



    st.divider()


    # ----------------------------
    # LISTAGEM
    # ----------------------------


    st.subheader(
        "📋 Relatos Registrados"
    )


    relatos = listar_relatos()


    if not relatos:


        st.info(
            "Nenhum relato registrado."
        )


    else:


        for r in relatos:


            with st.container():


                col1, col2 = st.columns(
                    [5,1]
                )


                with col1:


                    st.markdown(
                    f"""
### 👤 Aluno ID: {r['id_aluno']}

📅 {datetime.strptime(
r['data'],
'%Y-%m-%d'
).strftime('%d/%m/%Y')}

"""
                    )


                    st.write(
                        "### Problema"
                    )

                    st.error(
                        r["descricao"]
                    )


                    st.write(
                        "### Medida tomada"
                    )


                    st.info(
                        r["medida_tomada"]
                    )



                with col2:


                    novo_status = st.selectbox(

                        "Status",

                        [
                            "ABERTO",
                            "EM ACOMPANHAMENTO",
                            "FINALIZADO"
                        ],

                        index=[
                            "ABERTO",
                            "EM ACOMPANHAMENTO",
                            "FINALIZADO"
                        ].index(
                            r["status"]
                        ),

                        key=f"status_{r['id']}",

                        format_func=lambda x:
                        {
                            "ABERTO": "🔴",
                            "EM ACOMPANHAMENTO": "🟡",
                            "FINALIZADO": "🟢"
                        }[x]

                    )


                    if novo_status != r["status"]:


                        atualizar_status(
                            r["id"],
                            novo_status
                        )


                        st.rerun()


                st.divider()



# ==================================================
# EXECUTA
# ==================================================

renderizar_relatos()