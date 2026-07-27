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
            .select("id, id_turma, id_professor, periodo, data_inicio, data_fim, conteudo, objetivo, materiais, referencias, observacoes, status, created_at")
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
            .select("id, id_turma, id_professor, periodo, data_inicio, data_fim, conteudo, objetivo, materiais, referencias, observacoes, status, created_at")
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


def atualizar_planejamento(id, dados):
    try:
        supabase.table("planejamentos").update(dados).eq("id", id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar planejamento: {e}")
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
        # buscar professor da turma selecionada
        turma_obj = next((t for t in turmas if t.get('id') == id_turma), None)
        professor_id = turma_obj.get('professor_id') if turma_obj else None
        professor_nome = None
        if professor_id:
            resp_prof = supabase.table('usuarios').select('id, nome').eq('id', professor_id).execute()
            if resp_prof.data:
                professor_nome = resp_prof.data[0].get('nome')

        col_a, col_b = st.columns(2)
        with col_a:
            turma_display = st.text_input('Turma selecionada', value=turma_nome, disabled=True)
        with col_b:
            st.text_input('Professor', value=professor_nome or '—', disabled=True)

        periodo = st.text_input('Período (ex: 1º bimestre)')
        data_inicio = st.date_input('Data início')
        data_fim = st.date_input('Data fim')
        conteudo = st.text_area('Conteúdo planejado')
        objetivo = st.text_area('Objetivo')
        materiais = st.text_area('Materiais')
        referencias = st.text_area('Referências')
        observacoes = st.text_area('Observações gerais')
        status_planejamento = st.selectbox('Status', ['RASCUNHO', 'ENVIADO', 'APROVADO'])

        if st.button('💾 Salvar Planejamento', type='primary'):
            usuario = st.session_state.get('usuario', {})
            usuario_id = usuario.get('id') if usuario else None
            if not usuario_id:
                st.warning('É necessário estar autenticado para salvar um planejamento.')
            else:
                dados = {
                    'id_turma': id_turma,
                    'id_professor': professor_id or usuario_id,
                    'periodo': periodo,
                    'data_inicio': str(data_inicio),
                    'data_fim': str(data_fim),
                    'conteudo': conteudo,
                    'objetivo': objetivo,
                    'materiais': materiais,
                    'referencias': referencias,
                    'observacoes': observacoes,
                    'status': status_planejamento
                }
                ok = criar_planejamento(dados)
                if ok:
                    st.success('Planejamento criado!')
                    # atualizar listagem imediatamente
                    planejamentos = listar_planejamentos()


    st.divider()




    # ----------------------------------------------
    # LISTAGEM
    # ----------------------------------------------


    st.subheader(
        "📅 Planejamentos Futuros"
    )


    planejamentos = listar_planejamentos()
    turmas_all = listar_turmas()


    if not planejamentos:

        st.info(
            "Nenhum planejamento encontrado."
        )

    else:

        for p in planejamentos:

            # localizar turma e professor para exibição amigável
            turma_obj = next((t for t in turmas_all if t.get('id') == p.get('id_turma')), None)
            turma_nome = turma_obj.get('nome') if turma_obj else f"ID: {p.get('id_turma', '—')}"

            professor_nome = None
            professor_id = p.get('id_professor') or (turma_obj.get('professor_id') if turma_obj else None)
            if professor_id:
                resp_prof = supabase.table('usuarios').select('id, nome').eq('id', professor_id).execute()
                if resp_prof.data:
                    professor_nome = resp_prof.data[0].get('nome')

            periodo_exib = p.get('periodo', '—')

            with st.expander(f"Planejamento #{p['id']} — {turma_nome} — {periodo_exib}", expanded=False):

                colA, colB = st.columns([3,1])
                with colA:
                    st.markdown(f"**Período:** {periodo_exib}")
                    st.markdown(f"**Professor:** {professor_nome or '—'}")
                    st.markdown(f"**Status:** {p.get('status', '—')}")
                    st.markdown("---")
                    st.markdown("**Conteúdo planejado:**")
                    st.write(p.get('conteudo', ''))
                    st.markdown("**Objetivo:**")
                    st.write(p.get('objetivo', ''))
                    st.markdown("**Materiais:**")
                    st.write(p.get('materiais', ''))
                    st.markdown("**Referências:**")
                    st.write(p.get('referencias', ''))
                    st.markdown("**Observações:**")
                    st.write(p.get('observacoes', ''))

                with colB:
                    if st.button("🗑️", key=f"del_{p['id']}"):
                        excluir_planejamento(p['id'])
                        st.success("Planejamento excluído.")

                st.markdown("---")

                # Formulário de edição
                st.subheader("Editar Planejamento")

                key_prefix = f"pl_{p['id']}_"
                # campos com keys únicos
                periodo_new = st.text_input('Período', value=p.get('periodo',''), key=key_prefix+'periodo')
                data_inicio_new = st.date_input('Data início', value=datetime.strptime(p.get('data_inicio'), '%Y-%m-%d').date() if p.get('data_inicio') else datetime.today().date(), key=key_prefix+'data_inicio')
                data_fim_new = st.date_input('Data fim', value=datetime.strptime(p.get('data_fim'), '%Y-%m-%d').date() if p.get('data_fim') else datetime.today().date(), key=key_prefix+'data_fim')
                conteudo_new = st.text_area('Conteúdo planejado', value=p.get('conteudo',''), key=key_prefix+'conteudo')
                objetivo_new = st.text_area('Objetivo', value=p.get('objetivo',''), key=key_prefix+'objetivo')
                materiais_new = st.text_area('Materiais', value=p.get('materiais',''), key=key_prefix+'materiais')
                referencias_new = st.text_area('Referências', value=p.get('referencias',''), key=key_prefix+'referencias')
                observacoes_new = st.text_area('Observações gerais', value=p.get('observacoes',''), key=key_prefix+'observacoes')
                status_new = st.selectbox('Status', ['RASCUNHO', 'ENVIADO', 'APROVADO'], index=['RASCUNHO','ENVIADO','APROVADO'].index(p.get('status','RASCUNHO')), key=key_prefix+'status')

                col_save, col_cancel = st.columns([1,1])
                with col_save:
                    if st.button('💾 Salvar alterações', key=key_prefix+'save'):
                        dados_atual = {
                            'periodo': periodo_new,
                            'data_inicio': str(data_inicio_new),
                            'data_fim': str(data_fim_new),
                            'conteudo': conteudo_new,
                            'objetivo': objetivo_new,
                            'materiais': materiais_new,
                            'referencias': referencias_new,
                            'observacoes': observacoes_new,
                            'status': status_new
                        }
                        ok = atualizar_planejamento(p['id'], dados_atual)
                        if ok:
                            st.success('Planejamento atualizado.')

                with col_cancel:
                    if st.button('Cancelar', key=key_prefix+'cancel'):
                        st.info('Edição cancelada.')

                st.divider()


# ==================================================
# EXECUÇÃO
# ==================================================

renderizar_planejamento()