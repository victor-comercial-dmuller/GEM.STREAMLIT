import streamlit as st
import pandas as pd
from datetime import datetime
from config import supabase

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
        return resposta.data
    except Exception as e:
        st.error(f"Erro ao carregar alunos: {e}")
        return []


@st.cache_data(ttl=60)
def carregar_alunos_com_isolamento():
    """Carrega alunos aplicando isolamento."""
    try:
        alunos = carregar_alunos()
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
            .select("""
                *,
                alunos_aula(
                    id,
                    id_aluno,
                    id_aula
                )
            """)
            .execute()
        )
        return resposta.data
    except Exception as e:
        st.warning(f"Nenhum histórico de avaliação encontrado ou o fluxo ainda não foi alimentado.")
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



# =====================================================
# NOVA AVALIAÇÃO
# =====================================================


with st.expander(
    "➕ Nova Avaliação",
    expanded=True
):


    alunos = carregar_alunos_com_isolamento()
    presencas = carregar_presencas()


    if not alunos:

        st.warning(
            "Nenhum aluno encontrado. Cadastre usuários de perfil ALUNO antes de registrar avaliações."
        )

        st.stop()

    if not presencas:
        st.info("Nenhuma presença de aula registrada no banco. Registre primeiro uma aula e a presença dos alunos.")
        st.stop()


    lista_alunos = {
        a["nome"]: a["id"]
        for a in alunos
        if a.get("nome")
    }

    id_aluno_aula = st.selectbox(
        "Presença vinculada *",
        options=[p["id"] for p in presencas],
        format_func=lambda x: f"ID presença {x}"
    )

    aluno_nome = st.selectbox(
        "Aluno *",
        list(lista_alunos.keys())
    )



    col1, col2, col3 = st.columns(3)


    with col1:

        tipo = st.selectbox(
            "Tipo Avaliação",
            [
                "Prática",
                "Teórica"
            ]
        )


    with col2:

        tipo_avaliacao = st.selectbox(
            "Tipo Avaliação",
            [
                "Prática",
                "Teórica"
            ]
        )


    with col3:

        data = st.date_input(
            "Data",
            datetime.today()
        )



    col4, col5 = st.columns(2)


    with col4:

        fase = st.text_input(
            "Fase / Lição"
        )


    with col5:

        nota = st.text_input(
            "Nota / Conceito *"
        )



    comentario = st.text_area(
        "Comentários"
    )



    if st.button(
        "💾 Salvar Avaliação",
        type="primary"
    ):


        if nota == "":

            st.warning(
                "Informe a nota."
            )

        else:

            usuario = st.session_state.get("usuario", {})
            avaliador_id = usuario.get("id")

            if not avaliador_id:
                st.warning("É necessário estar autenticado para registrar uma avaliação.")
                st.stop()

            dados = {

                "id_aluno_aula":
                    id_aluno_aula,

                "data_avaliacao":
                    str(data),

                "tipo_avaliacao":
                    tipo_avaliacao,

                "fase_licao":
                    fase,

                "nota":
                    nota,

                "comentarios":
                    comentario,

                "avaliador":
                    avaliador_id
            }


            if salvar_avaliacao(dados):

                st.success(
                    "Avaliação salva!"
                )

                st.cache_data.clear()

                st.rerun()



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


else:

    st.info(
        "Nenhuma avaliação cadastrada."
    )