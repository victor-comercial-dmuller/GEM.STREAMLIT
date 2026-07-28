import streamlit as st
import pandas as pd
from datetime import datetime
from config import supabase
from database.utils.database import (
    carregar_turmas,
    carregar_conteudos,
    carregar_professores,
    carregar_alunos,
)

# =====================================================
# VERIFICAÇÃO DE AUTENTICAÇÃO
# =====================================================

if "usuario" not in st.session_state or not st.session_state.usuario:
    st.info("Faça login para acessar esta página.")
    st.stop()

usuario_logado = st.session_state.usuario
perfil_logado = usuario_logado.get("perfil", "—")

# =====================================================
# CONFIGURAÇÃO
# =====================================================

st.title("📝 Avaliações")
st.caption("Registre e acompanhe o desempenho dos alunos")


# =====================================================
# FUNÇÕES
# =====================================================

@st.cache_data(ttl=60)
def carregar_alunos():
    try:
        resposta = (
            supabase
            .table("usuarios")
            .select("*")
            .eq("perfil", "ALUNO")
            .order("nome")
            .execute()
        )
        return resposta.data or []
    except Exception as e:
        st.error(f"Erro ao carregar alunos: {e}")
        return []


@st.cache_data(ttl=60)
def carregar_alunos_com_isolamento(id_turma=None):
    """Carrega alunos aplicando isolamento. Se id_turma fornecido, filtra por turma."""
    try:
        alunos = carregar_alunos()

        # filtra por turma quando informado
        if id_turma is not None:
            alunos = [a for a in alunos if a.get("turma_id") == id_turma or a.get("id_turma") == id_turma]

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


@st.cache_data(ttl=60)
def carregar_presencas():
    try:
        resposta = (
            supabase
            .table("alunos_aula")
            .select("id, id_aula, id_aluno, presenca, observacao")
            .execute()
        )
        return resposta.data
    except Exception as e:
        st.warning(f"Nenhuma presença registrada para avaliação ou o fluxo não foi alimentado ainda.")
        return []


def carregar_avaliacoes():
    try:
        resposta = (
            supabase
            .table("avaliacoes")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return resposta.data or []
    except Exception as e:
        st.error(f"Erro ao carregar avaliações: {e}")
        return []


def salvar_avaliacao(dados):
    try:
        supabase \
        .table("avaliacoes") \
        .insert(dados) \
        .execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar avaliação: {e}")
        return False



# Reescreve o bloco de Nova Avaliação para suportar múltiplas questões com alternativas
with st.expander("➕ Nova Avaliação", expanded=True):

    # carregamentos
    turmas = carregar_turmas()
    conteudos = carregar_conteudos()
    alunos_full = carregar_alunos_com_isolamento(id_turma=None)

    if not turmas:
        st.warning("Nenhuma turma ativa encontrada. Cadastre turmas antes de prosseguir.")
        st.stop()

    if not conteudos:
        st.info("Nenhum conteúdo cadastrado. Cadastre conteúdos para vincular à avaliação.")

    # mapas
    mapa_turmas = {t.get("nome", f"Turma {t.get('id')}"): t.get("id") for t in turmas}
    mapa_conteudos = {c.get("titulo", f"Conteúdo {c.get('id')}"): c.get("id") for c in conteudos}

    # seleção básica
    nome_avaliacao = st.text_input("Nome da avaliação", key="nome_avaliacao")
    tipo_avaliacao = st.selectbox("Tipo de avaliação", ["Prática", "Teórica"])
    conteudo_sel = st.selectbox("Conteúdo", options=list(mapa_conteudos.keys())) if mapa_conteudos else None
    turma_sel = st.selectbox("Turma", options=list(mapa_turmas.keys()))
    id_turma = mapa_turmas.get(turma_sel)

    # escolha o escopo da avaliação: Aluno ou Turma inteira
    escopo = st.radio("Aplicar avaliação para", ("Aluno", "Turma inteira"))

    # busca alunos já filtrados por turma e isolamento
    alunos_por_turma = carregar_alunos_com_isolamento(id_turma=id_turma)
    if not alunos_por_turma:
        alunos_por_turma = carregar_alunos_com_isolamento(id_turma=None)

    mapa_alunos = {a.get("nome", f"Aluno {a.get('id')}"): a.get("id") for a in alunos_por_turma}

    id_aluno = None
    if escopo == "Aluno":
        aluno_nome = st.selectbox("Aluno", options=list(mapa_alunos.keys()))
        id_aluno = mapa_alunos.get(aluno_nome)

    data = st.date_input("Data", datetime.today())

    usuario = st.session_state.get("usuario", {})
    avaliador_id = usuario.get("id")
    st.markdown(f"**Avaliador:** {usuario.get('nome','-')} (ID {avaliador_id})")

    # sessão para armazenar questões temporariamente
    if "nova_avaliacao_questoes" not in st.session_state:
        st.session_state["nova_avaliacao_questoes"] = []

    st.subheader("Questões da avaliação")

    # área para adicionar uma nova questão (usa callback para atualizar session_state com segurança)
    with st.container():
        st.text_input("Enunciado da questão", key="q_texto")
        st.text_area("Alternativas (uma por linha)", key="q_alts")
        alternativas = [a.strip() for a in st.session_state.get("q_alts", "").splitlines() if a.strip()]
        if alternativas:
            st.selectbox("Alternativa correta", options=list(range(len(alternativas))), format_func=lambda i: alternativas[i], key="q_correta")

        st.number_input("Peso (nota máxima)", min_value=0, value=1, step=1, key="q_peso")

        def _adicionar_questao_callback():
            texto = st.session_state.get("q_texto", "").strip()
            alts = [a.strip() for a in st.session_state.get("q_alts", "").splitlines() if a.strip()]
            if not texto:
                st.warning("Informe o enunciado da questão antes de adicionar.")
                return
            if not alts:
                st.warning("Adicione ao menos uma alternativa.")
                return
            correta_idx = st.session_state.get("q_correta")
            if correta_idx is None:
                st.warning("Selecione a alternativa correta.")
                return
            peso = int(st.session_state.get("q_peso", 1))
            seq = len(st.session_state["nova_avaliacao_questoes"]) + 1
            quest = {
                "sequencia": seq,
                "questao_avaliada": texto,
                "alternativas": alts,
                "questao_certa": alts[correta_idx],
                "nota_maxima": peso,
            }
            st.session_state["nova_avaliacao_questoes"].append(quest)
            # limpar campos via session_state (seguro dentro de callback)
            st.session_state["q_texto"] = ""
            st.session_state["q_alts"] = ""
            st.session_state["q_peso"] = 1
            # remover seleção de correta (se existir)
            if "q_correta" in st.session_state:
                del st.session_state["q_correta"]

        st.button("➕ Nova Questão Avaliativa", on_click=_adicionar_questao_callback)

    # mostra questões adicionadas
    if st.session_state["nova_avaliacao_questoes"]:
        total_max = sum(q["nota_maxima"] for q in st.session_state["nova_avaliacao_questoes"])
        st.info(f"Total de pontos nesta avaliação: {total_max}")

        for q in st.session_state["nova_avaliacao_questoes"]:
            st.markdown(f"**{q['sequencia']}.** {q['questao_avaliada']} — Peso: {q['nota_maxima']}")
            for i, alt in enumerate(q["alternativas"], start=1):
                marc = "(correta)" if alt == q["questao_certa"] else ""
                st.write(f"- {i}) {alt} {marc}")

        if st.button("💾 Salvar Avaliação (todas as questões)"):
            if not avaliador_id:
                st.warning("É necessário estar autenticado para registrar uma avaliação.")
                st.stop()
            registros = []

            if escopo == "Aluno":
                # salvar apenas para o aluno selecionado
                id_avaliacao_group = int(datetime.timestamp(datetime.now()) * 1000)
                for q in st.session_state["nova_avaliacao_questoes"]:
                    registros.append({
                        "data_avaliacao": str(data),
                        "nome_avaliacao": nome_avaliacao,
                        "tipo_avaliacao": tipo_avaliacao,
                        "questao_avaliada": q["questao_avaliada"],
                        "nota": None,
                        "comentarios": None,
                        "avaliador": avaliador_id,
                        "id_aluno": id_aluno,
                        "sequencia": q["sequencia"],
                        "nota_maxima": q["nota_maxima"],
                        "id_turma": id_turma,
                        "questoes": q["alternativas"],
                        "questao_certa": q["questao_certa"],
                        "id_avaliacao": id_avaliacao_group,
                        "acertividade": None,
                    })

                try:
                    supabase.table("avaliacoes").insert(registros).execute()
                    st.success("Avaliação registrada com sucesso para o aluno.")
                    st.session_state["nova_avaliacao_questoes"] = []
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar avaliação: {e}")

            else:
                # salvar para toda a turma: cria avaliação (com id_avaliacao próprio) para cada aluno
                alunos_turma = carregar_alunos_com_isolamento(id_turma=id_turma)
                if not alunos_turma:
                    st.warning("Nenhum aluno encontrado na turma para salvar a avaliação.")
                else:
                    todos_registros = []
                    base_ts = int(datetime.timestamp(datetime.now()) * 1000)
                    for idx, aluno in enumerate(alunos_turma):
                        id_aluno_local = aluno.get("id")
                        id_avaliacao_group = base_ts + idx
                        for q in st.session_state["nova_avaliacao_questoes"]:
                            todos_registros.append({
                                "data_avaliacao": str(data),
                                "nome_avaliacao": nome_avaliacao,
                                "tipo_avaliacao": tipo_avaliacao,
                                "questao_avaliada": q["questao_avaliada"],
                                "nota": None,
                                "comentarios": None,
                                "avaliador": avaliador_id,
                                "id_aluno": id_aluno_local,
                                "sequencia": q["sequencia"],
                                "nota_maxima": q["nota_maxima"],
                                "id_turma": id_turma,
                                "questoes": q["alternativas"],
                                "questao_certa": q["questao_certa"],
                                "id_avaliacao": id_avaliacao_group,
                                "acertividade": None,
                            })

                    try:
                        supabase.table("avaliacoes").insert(todos_registros).execute()
                        st.success("Avaliação registrada com sucesso para a turma.")
                        st.session_state["nova_avaliacao_questoes"] = []
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar avaliação para a turma: {e}")


# =====================================================
# LISTAGEM
# =====================================================


st.divider()


st.subheader(
    "📋 Histórico de Avaliações"
)


dados = carregar_avaliacoes()



if dados:


    df = pd.DataFrame(
        dados
    )


    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # --- duplicação de avaliação ---
    st.divider()
    st.subheader("🔁 Duplicar avaliação")

    # agrupa por id_avaliacao
    grupos = {}
    for item in dados:
        key = item.get("id_avaliacao")
        if key is None:
            continue
        grupos.setdefault(key, []).append(item)

    if grupos:
        display_map = {}
        opcoes = []
        def encontrar_nome_grupo(items):
            for it in items:
                if it.get("nome_avaliacao"):
                    return it.get("nome_avaliacao")
                if it.get("nome_avalicao"):
                    return it.get("nome_avalicao")
            return None

        for k, v in grupos.items():
            nomeg = encontrar_nome_grupo(v) or "Sem nome"
            datag = v[0].get("data_avaliacao", "?")
            label = f"{k} — {nomeg} — {len(v)} questões — {datag}"
            display_map[label] = k
            opcoes.append(label)

        escolha = st.selectbox("Selecionar avaliação para duplicar", opcoes)
        if escolha:
            id_sel = display_map.get(escolha)
            if st.button("Duplicar como nova avaliação"):
                itens = grupos.get(id_sel, [])
                if not itens:
                    st.warning("Avaliação não encontrada para duplicação.")
                else:
                    # monta questões no formato esperado
                    copia = []
                    for it in sorted(itens, key=lambda x: x.get("sequencia") or 0):
                        copia.append({
                            "sequencia": it.get("sequencia"),
                            "questao_avaliada": it.get("questao_avaliada"),
                            "alternativas": it.get("questoes") or [],
                            "questao_certa": it.get("questao_certa"),
                            "nota_maxima": it.get("nota_maxima") or 1,
                        })
                    st.session_state["nova_avaliacao_questoes"] = copia
                    st.success("Avaliação copiada para Nova Avaliação. Edite os campos acima e salve como nova.")
                    st.rerun()
    else:
        st.info("Nenhuma avaliação com id de grupo disponível para duplicação.")


else:
    st.info(
        "Nenhuma avaliação cadastrada."
    )

    if st.button("🔍 Debug: buscar avaliações brutas"):
        try:
            resp = supabase.table("avaliacoes").select("*").order("created_at", desc=True).execute()
            st.write("Status:", getattr(resp, 'status_code', 'n/a'))
            st.write("Dados (primeiros 20):", resp.data[:20] if getattr(resp, 'data', None) else [])
            if getattr(resp, 'error', None):
                st.error(f"Erro da API: {resp.error}")
        except Exception as e:
            st.error(f"Erro ao executar consulta de debug: {e}")