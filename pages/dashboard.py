import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

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
        .limit(50)
        .execute()
    )

    return pd.DataFrame(resposta.data)


@st.cache_data(ttl=60)
def carregar_presencas():

    resposta = (
        supabase
        .table("alunos_aula")
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

    alunos = carregar_alunos_com_isolamento(usuario_logado)
    aulas = carregar_aulas()
    presencas = carregar_presencas()

    try:
        avaliacoes = carregar_avaliacoes()
    except Exception:
        avaliacoes = pd.DataFrame()



# =====================================================
# MÉTRICAS
# =====================================================


total_alunos = len(alunos)

total_aulas = len(aulas)


# últimos 30 dias

data_limite = datetime.now() - timedelta(days=30)


if not presencas.empty and "created_at" in presencas.columns:

    presencas["created_at"] = pd.to_datetime(
        presencas["created_at"], errors="coerce"
    )

    recentes = presencas[
        presencas["created_at"] >= data_limite
    ]

else:
    recentes = pd.DataFrame()


presenca_col = None
if not presencas.empty:
    if "presente" in presencas.columns:
        presenca_col = "presente"
    elif "presenca" in presencas.columns:
        presenca_col = "presenca"


if not recentes.empty and presenca_col:

    if presenca_col == "presente":
        presentes = len(
            recentes[
                recentes[presenca_col].astype(str).str.lower().isin(["true", "1", "presente", "present"])
            ]
        )
    else:
        presentes = len(
            recentes[
                recentes[presenca_col].astype(str).str.upper().isin(["PRESENTE", "TRUE", "1"])
            ]
        )

    taxa_presenca = round(
        presentes / len(recentes) * 100
    )

else:

    taxa_presenca = 0


if not presencas.empty and "status" in presencas.columns:

    atividades_ok = len(
        presencas[
            presencas["status"].astype(str).str.lower().isin(["concluido", "concluída", "concluida", "finalizado", "finalizada", "ok"])
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


    if not aulas.empty:


        mostrar = aulas.head(10)


        st.dataframe(
            mostrar,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Nenhuma aula cadastrada"
        )



    st.subheader(
        "🏅 Ranking de Alunos"
    )



    if not presencas.empty:


        ranking = (
            presencas
            .groupby("id_aluno")
            .agg(
                presencas=(
                    "presenca",
                    lambda x:
                    (x=="PRESENTE").sum()
                )
            )
            .reset_index()
            .sort_values(
                "presencas",
                ascending=False
            )
        )


        if not alunos.empty:

            ranking = ranking.merge(
                alunos[
                    ["id","nome"]
                ],
                left_on="id_aluno",
                right_on="id",
                how="left"
            )


        st.dataframe(
            ranking[
                ["nome","presencas"]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Sem dados de frequência"
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


