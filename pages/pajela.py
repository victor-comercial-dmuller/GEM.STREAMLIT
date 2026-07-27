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


def atualizar_relato(id_relato, descricao, medida, status):
    try:
        supabase\
            .table("relatos_dificuldades")\
            .update({
                "descricao": descricao,
                "medida_tomada": medida,
                "status": status
            })\
            .eq("id", id_relato)\
            .execute()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar relato: {e}")
        return False



# ==================================================
# TELA
# ==================================================

def renderizar_relatos():

    st.markdown("""
    <style>
    .relato-wrapper{max-width:1100px;margin-left:auto;margin-right:auto;padding:12px}
    .relato-save .stButton>button{background:#0b5ed7;color:white;border-radius:6px;padding:8px 14px}
    .relato-expander .stMarkdown{padding:6px}
    </style>
    <div class='relato-wrapper'>
    """, unsafe_allow_html=True)

    st.title("⚠️ Relatos de Dificuldades")
    st.caption("Registre e acompanhe dificuldades dos alunos.")


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

                    # sem rerun: continua a execução e a listagem abaixo será atualizada



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
        # buscar nomes dos alunos referenciados nos relatos
        ids_alunos = list({r.get('id_aluno') for r in relatos if r.get('id_aluno')})
        usuarios_map = {}
        if ids_alunos:
            ur = supabase.table('usuarios').select('id, nome').in_('id', ids_alunos).execute()
            for u in (ur.data or []):
                usuarios_map[u['id']] = u.get('nome')

        for r in relatos:
            aluno_nome = usuarios_map.get(r.get('id_aluno'), f"ID {r.get('id_aluno')}")
            data_fmt = ''
            try:
                data_fmt = datetime.strptime(r.get('data',''), '%Y-%m-%d').strftime('%d/%m/%Y')
            except Exception:
                data_fmt = r.get('data','')

            titulo = f"{aluno_nome} — {data_fmt}"
            with st.expander(titulo, expanded=False):
                st.markdown("**Problema**")
                st.error(r.get('descricao',''))
                st.markdown("**Medida tomada**")
                st.info(r.get('medida_tomada',''))

                # botão editar / formulário
                edit_key = f"edit_{r.get('id')}"
                if edit_key not in st.session_state:
                    st.session_state[edit_key] = False

                col_a, col_b = st.columns([1,1])
                with col_a:
                    if st.button("✏️ Editar", key=f"btn_edit_{r.get('id')}"):
                        st.session_state[edit_key] = True
                with col_b:
                    st.write("Status atual:")
                    status_label = r.get('status') or 'ABERTO'
                    icon = {'ABERTO':'🔴','EM ACOMPANHAMENTO':'🟡','FINALIZADO':'🟢'}.get(status_label,'🔴')
                    st.markdown(f"{icon} **{status_label}**")

                if st.session_state[edit_key]:
                    new_desc = st.text_area("Descrição", value=r.get('descricao',''), key=f"desc_{r.get('id')}")
                    new_medida = st.text_area("Medida tomada", value=r.get('medida_tomada',''), key=f"med_{r.get('id')}")
                    new_status = st.selectbox("Status", ["ABERTO","EM ACOMPANHAMENTO","FINALIZADO"], index=["ABERTO","EM ACOMPANHAMENTO","FINALIZADO"].index(r.get('status','ABERTO')), key=f"status_edit_{r.get('id')}")
                    btn_col1, btn_col2 = st.columns([1,1])
                    with btn_col1:
                        if st.button("💾 Salvar alterações", key=f"save_relato_{r.get('id')}"):
                            ok = atualizar_relato(r.get('id'), new_desc, new_medida, new_status)
                            if ok:
                                        st.success("Relato atualizado.")
                                        # atualizar objeto local para refletir mudanças sem reiniciar
                                        r['descricao'] = new_desc
                                        r['medida_tomada'] = new_medida
                                        r['status'] = new_status
                                        st.session_state[edit_key] = False
                    with btn_col2:
                        if st.button("Cancelar", key=f"cancel_relato_{r.get('id')}"):
                            st.session_state[edit_key] = False

                st.divider()
    # fechar wrapper
    st.markdown("</div>", unsafe_allow_html=True)



# ==================================================
# EXECUTA
# ==================================================

renderizar_relatos()