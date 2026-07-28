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
    # manter formulário aberto entre reruns
    st.session_state.show_novo_programa = True



# =====================================================
# FORMULÁRIO
# =====================================================


if "editar" not in st.session_state:
    st.session_state.editar=None



if st.session_state.get('show_novo_programa') or st.session_state.editar:


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
                cat_id = int(cat_row["id"].iloc[0])
                cat_nome = cat_row["categoria"].iloc[0]
                conteudo_inicio = int(cat_row["licao_inicial"].iloc[0])
                conteudo_fim = int(cat_row["licao_final"].iloc[0])
            else:
                conteudo_inicio = 1
                conteudo_fim = 1
        else:
            conteudo_inicio = 1
            conteudo_fim = 1

        c1,c2 = st.columns(2)

        with c1:

            inicio = st.number_input(
                "Lição Inicial",
                min_value=conteudo_inicio,
                max_value=conteudo_fim,
                value=max(conteudo_inicio, int(atv.get("licao_inicial", conteudo_inicio))),
                key=f"inicio{i}"
            )

        with c2:

            fim = st.number_input(
                "Lição Final",
                min_value=inicio,
                max_value=conteudo_fim,
                value=max(inicio, int(atv.get("licao_final", conteudo_inicio))),
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

        validacao_erro = None
        atividades_para_salvar = []

        for idx, atividade in enumerate(atividades_novas):
            if not atividade["categoria_id"]:
                validacao_erro = f"Selecione uma categoria para a atividade {idx+1}."
                break

            conteudo_row = categorias[categorias["id"] == atividade["categoria_id"]]
            if conteudo_row.empty:
                validacao_erro = f"Conteúdo não encontrado para a atividade {idx+1}."
                break

            conteudo_inicio = int(conteudo_row["licao_inicial"].iloc[0])
            conteudo_fim = int(conteudo_row["licao_final"].iloc[0])
            inicio_atv = int(atividade["licao_inicial"])
            fim_atv = int(atividade["licao_final"])

            if inicio_atv < conteudo_inicio:
                validacao_erro = (
                    f"A lição inicial da atividade {idx+1} não pode ser menor que {conteudo_inicio}."
                )
                break
            if fim_atv > conteudo_fim:
                validacao_erro = (
                    f"A lição final da atividade {idx+1} não pode ser maior que {conteudo_fim}."
                )
                break
            if inicio_atv > fim_atv:
                validacao_erro = (
                    f"A lição inicial da atividade {idx+1} não pode ser maior que a lição final."
                )
                break

            atividades_para_salvar.append({
                "categoria_id": int(atividade["categoria_id"]),
                "categoria_nome": atividade["categoria_nome"],
                "licao_inicial": inicio_atv,
                "licao_final": fim_atv
            })

        if validacao_erro:
            st.error(validacao_erro)
        else:
            if programa_edit:
                primeiro = atividades_para_salvar[0]
                dados = {
                    "nome": nome,
                    "ordem": int(ordem),
                    "ativo": bool(ativo),
                    "atividade_inicial": str(primeiro["licao_inicial"]),
                    "atividade_final": str(primeiro["licao_final"])
                }
                supabase.table(
                    "programas_minimos"
                ).update(
                    dados
                ).eq(
                    "id",
                    programa_edit["id"]
                ).execute()

                if len(atividades_para_salvar) > 1:
                    extras = []
                    for atividade in atividades_para_salvar[1:]:
                        extras.append({
                            "nome": nome,
                            "ordem": int(ordem),
                            "ativo": bool(ativo),
                            "atividade_inicial": str(atividade["licao_inicial"]),
                            "atividade_final": str(atividade["licao_final"])
                        })
                    supabase.table("programas_minimos").insert(extras).execute()
            else:
                rows_to_insert = []
                for atividade in atividades_para_salvar:
                    rows_to_insert.append({
                        "nome": nome,
                        "ordem": int(ordem),
                        "ativo": bool(ativo),
                        "atividade_inicial": str(atividade["licao_inicial"]),
                        "atividade_final": str(atividade["licao_final"])
                    })
                if rows_to_insert:
                    supabase.table(
                        "programas_minimos"
                    ).insert(
                        rows_to_insert
                    ).execute()



        st.success(
            "Programa salvo!"
        )

        # fechar formulário e atualizar listagem
        st.session_state.show_novo_programa = False
        st.cache_data.clear()
        st.rerun()



    if cancelar:
        st.session_state.editar=None
        st.session_state.show_novo_programa = False
        st.rerun()



# =====================================================
# LISTAGEM
# =====================================================


st.divider()

st.subheader(
    "📋 Programas cadastrados"
)



if programas.empty:
    st.info("Nenhum programa mínimo cadastrado.")
else:
    grouped = programas.groupby(["nome", "ordem", "ativo"], sort=False)
    for (nome, ordem, ativo), grupo in grouped:
        status = "Ativo" if ativo else "Inativo"
        label = f"{nome} — Ordem {ordem} — {status}"

        with st.expander(label, expanded=False):
            st.markdown(f"**Status:** {status}")
            st.markdown(f"**Ordem:** {ordem}")
            st.markdown(f"**Conteúdos:** {len(grupo)}")
            st.divider()

            for _, row in grupo.iterrows():
                conteudo_nome = 'Conteúdo'
                if not categorias.empty:
                    match = categorias[
                        (categorias["licao_inicial"].astype(int) == int(row["atividade_inicial"])) &
                        (categorias["licao_final"].astype(int) == int(row["atividade_final"]))
                    ]
                    if not match.empty:
                        conteudo_nome = match.iloc[0]["titulo"]

                st.markdown(
                    f"- {conteudo_nome} — Lição {row['atividade_inicial']} até {row['atividade_final']}"
                )

                col_a, col_b = st.columns([4,1])
                with col_b:
                    if st.button("✏️", key=f"edit_{row['id']}"):
                        st.session_state.editar = row.to_dict()
                        st.rerun()
                    if st.button("🗑️", key=f"del_{row['id']}"):
                        supabase.table(
                            "programas_minimos"
                        ).delete().eq(
                            "id",
                            int(row["id"])
                        ).execute()
                        st.cache_data.clear()
                        st.rerun()
