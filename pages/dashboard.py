import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date

from config import supabase


# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Dashboard Musical",
    layout="wide"
)

# Verificar autenticação
if "usuario" not in st.session_state or not st.session_state.usuario:
    st.info("Faça login para acessar o dashboard.")
    st.stop()

usuario_logado = st.session_state.usuario
perfil_logado = usuario_logado.get("perfil", "—")


# =====================================================
# FUNÇÕES
# =====================================================


@st.cache_data(ttl=60)
def carregar_alunos():
    resposta = (
        supabase
        .table("usuarios")
        .select("*")
        .eq("perfil", "ALUNO")
        .execute()
    )
    return pd.DataFrame(resposta.data)


@st.cache_data(ttl=60)
def carregar_alunos_com_isolamento(usuario_logado):
    """Carrega alunos aplicando isolamento conforme perfil."""
    perfil = usuario_logado.get("perfil", "—")
    localidade_id = usuario_logado.get("localidade_id")
    regiao_id = usuario_logado.get("regiao_id")
    usuario_id = usuario_logado.get("id")

    resposta = (
        supabase
        .table("usuarios")
        .select("*")
        .eq("perfil", "ALUNO")
        .execute()
    )
    
    alunos = pd.DataFrame(resposta.data)

    if perfil in ["ADMIN", "TI"]:
        return alunos
    
    if perfil == "COORDENADOR REGIONAL":
        return alunos[alunos["regiao_id"] == regiao_id]
    
    if perfil == "COORDENADOR LOCAL":
        return alunos[alunos["localidade_id"] == localidade_id]
    
    if perfil == "PROFESSOR" or perfil == "AUXILIAR":
        # Professores e auxiliares veem alunos de sua localidade
        return alunos[alunos["localidade_id"] == localidade_id]
    
    if perfil == "ALUNO":
        # Aluno vê apenas a si próprio
        return alunos[alunos["id"] == usuario_id]
    
    return alunos


@st.cache_data(ttl=60)
def carregar_aulas():

    resposta = (
        supabase
        .table("aulas")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return pd.DataFrame(resposta.data)


@st.cache_data(ttl=60)
def carregar_turmas():
    resposta = (
        supabase
        .table("turmas")
        .select("*")
        .execute()
    )
    return pd.DataFrame(resposta.data)


@st.cache_data(ttl=60)
def carregar_turmas_com_isolamento(usuario_logado):
    perfil = usuario_logado.get("perfil", "—")
    localidade_id = usuario_logado.get("localidade_id")
    regiao_id = usuario_logado.get("regiao_id")
    usuario_id = usuario_logado.get("id")

    consulta = supabase.table("turmas").select("*")

    if perfil == "ADMIN" or perfil == "TI":
        resposta = consulta.execute()
        return pd.DataFrame(resposta.data)

    if perfil == "COORDENADOR REGIONAL":
        resposta = consulta.eq("regiao_id", regiao_id).execute()
        return pd.DataFrame(resposta.data)

    if perfil == "COORDENADOR LOCAL":
        resposta = consulta.eq("localidade_id", localidade_id).execute()
        return pd.DataFrame(resposta.data)

    if perfil == "PROFESSOR":
        resposta = consulta.eq("professor_id", usuario_id).execute()
        return pd.DataFrame(resposta.data)

    if perfil == "AUXILIAR":
        resposta = consulta.eq("auxiliar_id", usuario_id).execute()
        return pd.DataFrame(resposta.data)

    # Aluno não precisa carregar turmas diretamente aqui.
    resposta = consulta.execute()
    return pd.DataFrame(resposta.data)


@st.cache_data(ttl=60)
def carregar_presencas():

    resposta = (
        supabase
        .table("presencas")
        .select("*")
        .execute()
    )

    return pd.DataFrame(resposta.data)


@st.cache_data(ttl=60)
def carregar_avaliacoes():

    resposta = (
        supabase
        .table("avaliacoes")
        .select("*")
        .execute()
    )

    return pd.DataFrame(resposta.data)



# =====================================================
# CARREGAMENTO
# =====================================================


with st.spinner("Carregando dashboard..."):

    turmas = carregar_turmas_com_isolamento(usuario_logado)
    alunos = carregar_alunos_com_isolamento(usuario_logado)
    aulas = carregar_aulas()
    presencas = carregar_presencas()

    try:
        avaliacoes = carregar_avaliacoes()
    except Exception:
        avaliacoes = pd.DataFrame()



# =====================================================
# FILTROS E MÉTRICAS
# =====================================================

filtro_turma = None
filtro_avaliacao = None


def _filtrar_por_turma(df, turma_id):
    if df.empty or turma_id is None:
        return df
    if "id_turma" in df.columns:
        return df[df["id_turma"] == turma_id]
    if "turma_id" in df.columns:
        return df[df["turma_id"] == turma_id]
    return df


def _filtrar_por_data(df, coluna_data, inicio, fim):
    if df.empty or coluna_data not in df.columns:
        return df
    df = df.copy()
    df[coluna_data] = pd.to_datetime(df[coluna_data], errors="coerce")
    return df[(df[coluna_data] >= pd.to_datetime(inicio)) & (df[coluna_data] <= pd.to_datetime(fim))]


def _presentes(df, coluna):
    if df.empty or coluna not in df.columns:
        return pd.Series([], dtype="bool")
    valores = df[coluna].astype(str).str.strip().str.lower()
    return valores.isin(["true", "1", "presente", "present", "sim", "s"])


with st.expander("Filtros de dashboard", expanded=True):
    col1, col2, col3 = st.columns([3, 3, 4])

    turma_map = {}
    turma_opcoes = ["Todas as turmas"]
    if not turmas.empty and "id" in turmas.columns and "nome" in turmas.columns:
        for _, linha in turmas.sort_values("nome").iterrows():
            label = f"{linha['nome']} ({linha['id']})"
            turma_opcoes.append(label)
            turma_map[label] = linha["id"]

    selecionado_turma = col1.selectbox(
        "Filtrar por turma",
        turma_opcoes,
        index=0,
        help="Escolha uma turma para filtrar métricas e rankings"
    )
    if selecionado_turma != "Todas as turmas":
        filtro_turma = turma_map.get(selecionado_turma)

    avaliacao_map = {}
    avaliacao_opcoes = ["Todas as avaliações"]
    if not avaliacoes.empty and "id_avaliacao" in avaliacoes.columns:
        for id_av, grupo in avaliacoes.groupby("id_avaliacao", sort=False):
            nome = None
            if "nome_avaliacao" in grupo.columns:
                nome_serie = grupo["nome_avaliacao"].dropna().astype(str)
                if not nome_serie.empty:
                    nome = nome_serie.iloc[0]
            titulo = nome if nome else f"Avaliação {id_av}"
            label = f"{titulo} ({id_av})"
            avaliacao_opcoes.append(label)
            avaliacao_map[label] = id_av

    selecionado_avaliacao = col2.selectbox(
        "Filtrar por avaliação",
        avaliacao_opcoes,
        index=0,
        help="Opcional: limite gráficos e métricas a uma avaliação específica"
    )
    if selecionado_avaliacao != "Todas as avaliações":
        filtro_avaliacao = avaliacao_map.get(selecionado_avaliacao)

    data_inicial = col3.date_input(
        "Data inicial",
        value=date.today() - timedelta(days=30),
        key="dashboard_data_inicial"
    )
    data_final = col3.date_input(
        "Data final",
        value=date.today(),
        key="dashboard_data_final"
    )

    if data_inicial > data_final:
        st.warning("A data inicial não pode ser posterior à data final.")


alunos_filtrados = _filtrar_por_turma(alunos, filtro_turma)
if filtro_avaliacao is not None and not avaliacoes.empty and "id_aluno" in avaliacoes.columns:
    ids_alunos_avaliacao = avaliacoes.loc[avaliacoes["id_avaliacao"] == filtro_avaliacao, "id_aluno"].dropna().unique().tolist()
    if ids_alunos_avaliacao and "id" in alunos_filtrados.columns:
        alunos_filtrados = alunos_filtrados[alunos_filtrados["id"].isin(ids_alunos_avaliacao)]

alunos_ids_disponiveis = []
if not alunos_filtrados.empty and "id" in alunos_filtrados.columns:
    alunos_ids_disponiveis = alunos_filtrados["id"].dropna().unique().tolist()


aulas_filtradas = pd.DataFrame()
if not aulas.empty:
    aulas_filtradas = aulas.copy()
    if "data_aula" in aulas_filtradas.columns:
        aulas_filtradas = _filtrar_por_data(aulas_filtradas, "data_aula", data_inicial, data_final)
    elif "created_at" in aulas_filtradas.columns:
        aulas_filtradas = _filtrar_por_data(aulas_filtradas, "created_at", data_inicial, data_final)
    aulas_filtradas = _filtrar_por_turma(aulas_filtradas, filtro_turma)


presencas_filtradas = presencas.copy()
if "id_aula" in presencas_filtradas.columns and not aulas.empty:

    aula_info = aulas[
        ["id", "id_turma", "data_aula"]
    ].copy()

    aula_info = aula_info.rename(
        columns={
            "id": "id_aula",
            "data_aula": "aula_data"
        }
    )

    presencas_filtradas = presencas_filtradas.merge(
        aula_info,
        on="id_aula",
        how="left"
    )
    if alunos_ids_disponiveis and "id_aluno" in presencas_filtradas.columns:
        presencas_filtradas = presencas_filtradas[
            presencas_filtradas["id_aluno"].isin(alunos_ids_disponiveis)
        ]

    if filtro_turma is not None and "id_turma" in presencas_filtradas.columns:
        presencas_filtradas = presencas_filtradas[
            presencas_filtradas["id_turma"] == filtro_turma
        ]
    if "created_at" in presencas_filtradas.columns:
        presencas_filtradas = _filtrar_por_data(presencas_filtradas, "created_at", data_inicial, data_final)
    elif "aula_data" in presencas_filtradas.columns:
        presencas_filtradas = _filtrar_por_data(presencas_filtradas, "aula_data", data_inicial, data_final)


avaliacoes_filtradas = avaliacoes.copy()
# Converter nota para número
if "nota" in avaliacoes_filtradas.columns:

    avaliacoes_filtradas["nota"] = (
        avaliacoes_filtradas["nota"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )

    avaliacoes_filtradas["nota"] = pd.to_numeric(
        avaliacoes_filtradas["nota"],
        errors="coerce"
    )

if not avaliacoes_filtradas.empty:
    if alunos_ids_disponiveis and "id_aluno" in avaliacoes_filtradas.columns:
        avaliacoes_filtradas = avaliacoes_filtradas[avaliacoes_filtradas["id_aluno"].isin(alunos_ids_disponiveis)]
    avaliacoes_filtradas = _filtrar_por_turma(avaliacoes_filtradas, filtro_turma)
    if filtro_avaliacao is not None:
        avaliacoes_filtradas = avaliacoes_filtradas[avaliacoes_filtradas["id_avaliacao"] == filtro_avaliacao]
    if "data_avaliacao" in avaliacoes_filtradas.columns:
        avaliacoes_filtradas = _filtrar_por_data(avaliacoes_filtradas, "data_avaliacao", data_inicial, data_final)


total_alunos = len(alunos_filtrados["id"].unique())

total_aulas = len(aulas_filtradas)

presenca_col = None
if not presencas_filtradas.empty:
    if "presente" in presencas_filtradas.columns:
        presenca_col = "presente"
    elif "presenca" in presencas_filtradas.columns:
        presenca_col = "presenca"

if presenca_col is not None and not presencas_filtradas.empty:
    presentes = _presentes(presencas_filtradas, presenca_col).sum()
    taxa_presenca = round(presentes / len(presencas_filtradas)) if len(presencas_filtradas) else 0
else:
    taxa_presenca = 0

if not presencas_filtradas.empty and "status" in presencas_filtradas.columns:
    atividades_ok = len(
        presencas_filtradas[
            presencas_filtradas["status"].astype(str).str.lower().isin(["concluido", "concluída", "concluida", "finalizado", "finalizada", "ok"])
        ]
    )
else:
    atividades_ok = 0


# =====================================================
# HEADER
# =====================================================


st.title("🎵 Dashboard Musical")

st.caption(
    "Visão geral do Harmony Hub"
)



col1,col2,col3,col4 = st.columns(4)


with col1:

    st.metric(
        "👥 Total de Alunos",
        total_alunos,
        "+2 este mês"
    )


with col2:

    st.metric(
        "📚 Aulas Ministradas",
        total_aulas,
        "Últimas semanas"
    )


with col3:

    st.metric(
        "📈 Taxa de Presença",
        f"{taxa_presenca}%",
        "Últimos 30 dias"
    )


with col4:

    st.metric(
        "🏆 Atividades OK",
        atividades_ok,
        "Total concluídas"
    )



st.divider()



# =====================================================
# CONTEÚDO PRINCIPAL
# =====================================================


col_esq, col_dir = st.columns([2,1])



# -----------------------------------------------------
# ATIVIDADES RECENTES
# -----------------------------------------------------

with col_esq:


    st.subheader(
        "🕒 Atividades Recentes"
    )


    if not aulas_filtradas.empty:


        mostrar = aulas_filtradas.head(10)


        st.dataframe(
            mostrar,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Nenhuma aula cadastrada para os filtros aplicados"
        )



    st.subheader(
        "🏅 Ranking de Alunos"
    )


    
    if not presencas_filtradas.empty:

        presencas_filtradas["presente_bool"] = (
            presencas_filtradas["presenca"]
            .astype(str)
            .str.strip()
            .str.lower()
            .isin(["true", "1", "presente", "sim", "s"])
        )

        ranking = (
            presencas_filtradas
            .groupby("id_aluno")
            .agg(
                presencas=("presente_bool", "sum")
            )
            .reset_index()
            .sort_values(
                "presencas",
                ascending=False
            )
        )

        if not alunos_filtrados.empty:

            ranking = ranking.merge(
                alunos_filtrados[
                    ["id","nome"]
                ].rename(columns={"id":"id_aluno"}),
                on="id_aluno",
                how="left"
            )

        st.dataframe(
            ranking[["nome","presencas"]],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Sem dados de frequência para os filtros aplicados"
        )


    if not avaliacoes_filtradas.empty and "nota" in avaliacoes_filtradas.columns and "nota_maxima" in avaliacoes_filtradas.columns:

        st.subheader(
            "📊 Ranking de Avaliações"
        )

        notas = avaliacoes_filtradas.copy()
        notas["nota"] = pd.to_numeric(notas["nota"], errors="coerce")
        notas["nota_maxima"] = pd.to_numeric(notas["nota_maxima"], errors="coerce")
        notas = notas.dropna(subset=["nota", "nota_maxima"])

        if not notas.empty:
            ranking_avaliacoes = (
                notas
                .groupby("id_aluno")
                .agg(total_nota=("nota", "sum"), total_max=("nota_maxima", "sum"))
                .assign(media=lambda df: (df["total_nota"] / df["total_max"]))
                .reset_index()
                .sort_values(
                    "media",
                    ascending=False
                )
            )

            if not alunos_filtrados.empty:
                ranking_avaliacoes = ranking_avaliacoes.merge(
                    alunos_filtrados[["id", "nome"]],
                    left_on="id_aluno",
                    right_on="id",
                    how="left"
                )

            st.dataframe(
                ranking_avaliacoes[["nome", "media"]].rename(columns={"media": "Média (%)"}),
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info(
                "Não há notas válidas nas avaliações filtradas"
            )



# -----------------------------------------------------
# RESUMO TURMAS
# -----------------------------------------------------

with col_dir:


    st.subheader(
        "🏫 Resumo das Turmas"
    )


    if not alunos.empty and "id_turma" in alunos:


        resumo = (
            alunos
            .groupby("id_turma")
            .size()
            .reset_index(
                name="Alunos"
            )
        )


        st.dataframe(
            resumo,
            use_container_width=True,
            hide_index=True
        )


    else:

        st.info(
            "Sem informações de turma"
        )


