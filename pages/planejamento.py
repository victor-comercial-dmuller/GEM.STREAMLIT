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

def listar_turmas():
    try:
        resposta = (
            supabase
            .table("turmas")
            .select("id, nome, regiao_id, localidade_id, professor_id, auxiliar_id")
            .order("nome")
            .execute()
        )
        return resposta.data
    except Exception as e:
        st.error(f"Erro ao listar turmas: {e}")
        return []


def listar_turmas_com_isolamento():
    """Lista turmas aplicando isolamento conforme perfil."""
    try:
        turmas = listar_turmas()
        perfil = usuario_logado.get("perfil", "—")
        localidade_id = usuario_logado.get("localidade_id")
        regiao_id = usuario_logado.get("regiao_id")
        usuario_id = usuario_logado.get("id")

        if perfil in ["ADMIN", "TI"]:
            return turmas

        if perfil == "COORDENADOR REGIONAL":
            return [t for t in turmas if t.get("regiao_id") == regiao_id]

        if perfil == "COORDENADOR LOCAL":
            return [t for t in turmas if t.get("localidade_id") == localidade_id]

        if perfil == "PROFESSOR":
            # Professor vê apenas as turmas em que é professor
            return [t for t in turmas if t.get("professor_id") == usuario_id]

        if perfil == "AUXILIAR":
            # Auxiliar vê apenas as turmas em que é auxiliar
            return [t for t in turmas if t.get("auxiliar_id") == usuario_id]

        if perfil == "ALUNO":
            # Aluno não tem acesso a planejamento
            return []

        return turmas
    except Exception as e:
        st.error(f"Erro ao listar turmas com isolamento: {e}")
        return []


def listar_planejamentos():
    try:
        resposta = (
            supabase
            .table("planejamentos")
            .select("id, id_turma, id_professor, observacoes, status, created_at")
            .order("created_at", desc=True)
            .execute()
        )
        return resposta.data
    except Exception as e:
        st.error(f"Erro ao listar planejamentos: {e}")
        return []


def criar_planejamento(dados):
    try:
        supabase.table("planejamentos").insert(dados).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao criar planejamento: {e}")
        return False


def excluir_planejamento(id):
    try:
        supabase\
            .table("planejamentos")\
            .delete()\
            .eq("id", id)\
            .execute()
        return True
    except Exception as e:
        st.error(f"Erro ao excluir planejamento: {e}")
        return False


# ==================================================
# PÁGINA
# ==================================================

def renderizar_planejamento():

    st.title("📋 Planejamento de Aulas")

    st.caption(
        "Organize suas futuras aulas e atividades."
    )


    # ----------------------------------------------
    # NOVO PLANEJAMENTO
    # ----------------------------------------------

    with st.expander(
        "➕ Novo Planejamento",
        expanded=True
    ):

        turmas = listar_turmas_com_isolamento()

        if not turmas:
            st.info("Cadastre uma turma antes de criar um planejamento.")
            st.stop()

        lista_turmas = {
            t["nome"]: t["id"]
            for t in turmas
            if t.get("nome")
        }

        turma_nome = st.selectbox(
            "Turma",
            list(lista_turmas.keys())
        )

        id_turma = lista_turmas[turma_nome]

        status_planejamento = st.selectbox(
            "Status",
            ["RASCUNHO", "ENVIADO", "APROVADO"]
        )

        observacoes = st.text_area(
            "Anotações, objetivos, materiais necessários..."
        )


        if st.button(
            "💾 Salvar Planejamento",
            type="primary"
        ):

            if not observacoes:
                st.warning(
                    "Informe as anotações."
                )

            else:

                usuario = st.session_state.get("usuario", {})
                usuario_id = usuario.get("id") if usuario else None

                if not usuario_id:
                    st.warning("É necessário estar autenticado para salvar um planejamento.")
                    st.stop()

                dados = {

                    "id_turma": id_turma,

                    "id_professor": usuario_id,

                    "status": status_planejamento,

                    "observacoes": observacoes

                }


                if criar_planejamento(dados):

                    st.success(
                        "Planejamento criado!"
                    )

                    st.rerun()



    st.divider()



    # ----------------------------------------------
    # LISTAGEM
    # ----------------------------------------------


    st.subheader(
        "📅 Planejamentos Futuros"
    )


    planejamentos = listar_planejamentos()


    if not planejamentos:

        st.info(
            "Nenhum planejamento encontrado."
        )

    else:


        for p in planejamentos:


            with st.container():

                col1, col2 = st.columns(
                    [5,1]
                )


                with col1:


                    turma_nome = f"ID: {p.get('id_turma', '—')}"

                    st.markdown(
                    f"""
                    ### Planejamento #{p['id']}

                    🧾 **Status:** {p.get('status', '—')}

                    👥 **Turma:** {turma_nome}

                    """
                    )

                    st.write(
                        p.get("observacoes", "")
                    )



                with col2:

                    if st.button(
                        "🗑️",
                        key=f"del_{p['id']}"
                    ):

                        excluir_planejamento(
                            p["id"]
                        )

                        st.rerun()



                st.divider()



# ==================================================
# EXECUÇÃO
# ==================================================

renderizar_planejamento()