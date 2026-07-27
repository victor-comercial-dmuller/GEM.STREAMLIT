import streamlit as st
import pandas as pd

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
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Programa Mínimo",
    layout="wide"
)



# =====================================================
# FUNÇÕES
# =====================================================


@st.cache_data(ttl=60)
def carregar_programas():

    resp = (
        supabase
        .table("programas_minimos")
        .select("*")
        .order("ordem")
        .execute()
    )

    return pd.DataFrame(resp.data)



@st.cache_data(ttl=60)
def carregar_categorias():

    resp = (
        supabase
        .table("conteudos")
        .select("*")
        .order("categoria")
        .order("fase")
        .order("titulo")
        .execute()
    )

    return pd.DataFrame(resp.data)



def limpar_form():

    st.session_state.nome = ""
    st.session_state.ordem = 1
    st.session_state.ativo = True
    st.session_state.atividades = []



# =====================================================
# LOAD
# =====================================================


programas = carregar_programas()

categorias = carregar_categorias()

categorias_disponiveis = []
if not categorias.empty:
    categorias_disponiveis = sorted(
        set(
            f"{row['categoria']} - {row['titulo']}"
            for _, row in categorias.iterrows()
            if row.get("categoria")
        )
    )


# =====================================================
# HEADER
# =====================================================


col1,col2 = st.columns([3,1])


with col1:

    st.title("🎓 Programa Mínimo")

    st.caption(
        "Configure os programas mínimos usando categorias cadastradas"
    )


with col2:

    novo = st.button(
        "➕ Novo Programa",
        use_container_width=True
    )



if novo:

    limpar_form()

    st.session_state.editar = None



# =====================================================
# FORMULÁRIO
# =====================================================


if "editar" not in st.session_state:
    st.session_state.editar=None



if novo or st.session_state.editar:


    st.divider()

    if st.session_state.editar:

        programa_edit = st.session_state.editar

        titulo="Editar Programa"

    else:

        programa_edit=None
        titulo="Novo Programa"



    st.subheader(
        titulo
    )



    nome = st.text_input(
        "Nome do Programa",
        value=
        programa_edit["nome"]
        if programa_edit else ""
    )


    ordem = st.number_input(
        "Ordem de Progressão",
        min_value=1,
        value=
        programa_edit["ordem"]
        if programa_edit else 1
    )


    ativo = st.toggle(
        "Programa Ativo",
        value=
        programa_edit["ativo"]
        if programa_edit else True
    )


    st.subheader(
        "📚 Atividades Obrigatórias"
    )


    if "atividades" not in st.session_state:

        if programa_edit:

            st.session_state.atividades = (
                programa_edit["atividades"]
            )

        else:

            st.session_state.atividades=[]


    if not categorias_disponiveis:
        st.warning("Cadastre conteúdos na tabela de conteúdos antes de montar um programa mínimo.")


    if st.button("➕ Adicionar atividade"):

        st.session_state.atividades.append(
            {
            "categoria_id":"",
            "categoria_nome":"",
            "licao_inicial":1,
            "licao_final":1
            }
        )



    atividades_novas=[]



    for i,atv in enumerate(
        st.session_state.atividades
    ):


        st.markdown(
            f"### Atividade {i+1}"
        )


        cat = st.selectbox(
            "Categoria",
            categorias_disponiveis,
            key=f"cat_{i}"
        )

        cat_id = None
        cat_nome = cat

        if categorias_disponiveis:
            cat_row = categorias[categorias["categoria"].fillna("").astype(str) + " - " + categorias["titulo"].fillna("").astype(str) == cat]
            if not cat_row.empty:
                cat_id = cat_row["id"].iloc[0]
                cat_nome = cat_row["categoria"].iloc[0]


        c1,c2=st.columns(2)


        with c1:

            inicio=st.number_input(
                "Lição Inicial",
                min_value=1,
                value=int(
                    atv.get(
                    "licao_inicial",1)
                ),
                key=f"inicio{i}"
            )


        with c2:

            fim=st.number_input(
                "Lição Final",
                min_value=1,
                value=int(
                    atv.get(
                    "licao_final",1)
                ),
                key=f"fim{i}"
            )


        atividades_novas.append(

            {
            "categoria_id":cat_id,
            "categoria_nome":cat_nome,
            "licao_inicial":inicio,
            "licao_final":fim
            }

        )



    c1,c2=st.columns(2)


    with c1:

        salvar = st.button(
            "💾 Salvar"
        )


    with c2:

        cancelar = st.button(
            "❌ Cancelar"
        )



    if salvar:


        dados={

            "nome":nome,

            "ordem":ordem,

            "ativo":ativo,

            "atividades":atividades_novas

        }


        if programa_edit:


            supabase.table(
                "programas_minimos"
            ).update(
                dados
            ).eq(
                "id",
                programa_edit["id"]
            ).execute()


        else:


            supabase.table(
                "programas_minimos"
            ).insert(
                dados
            ).execute()



        st.success(
            "Programa salvo!"
        )

        st.cache_data.clear()

        st.rerun()



    if cancelar:

        st.session_state.editar=None

        st.rerun()



# =====================================================
# LISTAGEM
# =====================================================


st.divider()

st.subheader(
    "📋 Programas cadastrados"
)



for _,p in programas.iterrows():


    with st.container(border=True):


        col1,col2,col3 = st.columns(
            [1,4,1]
        )


        with col1:

            st.markdown(
                f"## {p.ordem}"
            )


        with col2:

            st.subheader(
                p.nome
            )


            if p.ativo:

                st.success(
                    "Ativo"
                )

            else:

                st.warning(
                    "Inativo"
                )


            for a in p.atividades:

                st.info(
                    f"""
                    {a['categoria_nome']}  
                    Lição {a['licao_inicial']} até {a['licao_final']}
                    """
                )



        with col3:


            if st.button(
                "✏️",
                key=f"edit{p.id}"
            ):

                st.session_state.editar=p.to_dict()

                st.rerun()



            if st.button(
                "🗑️",
                key=f"del{p.id}"
            ):


                supabase.table(
                    "programas_minimos"
                ).delete().eq(
                    "id",
                    p.id
                ).execute()


                st.cache_data.clear()

                st.rerun()


