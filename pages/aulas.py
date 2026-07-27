import streamlit as st
import pandas as pd
from datetime import date
from config import supabase

# ================================
# VERIFICAÇÃO DE AUTENTICAÇÃO
# ================================

if "usuario" not in st.session_state or not st.session_state.usuario:
    st.info("Faça login para acessar esta página.")
    st.stop()

usuario_logado = st.session_state.usuario
perfil_logado = usuario_logado.get("perfil", "—")

# ================================
# FUNÇÕES SUPABASE
# ================================

def listar_turmas_supabase():
    try:
        resposta = (
            supabase
            .table("turmas")
            .select("""
                id,
                nome,
                professor:usuarios!professor_id(nome)
            """)
            .order("nome")
            .execute()
        )
        return resposta.data
    except Exception as e:
        st.error(f"Erro ao carregar turmas: {e}")
        return []


def listar_turmas_com_isolamento():
    """Carrega turmas do usuário aplicando isolamento."""
    try:
        turmas = listar_turmas_supabase()
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
            usuario_id = usuario_logado.get("id")
            resposta = (
                supabase
                .table("turmas")
                .select("id, nome, professor:usuarios!professor_id(nome)")
                .eq("professor_id", usuario_id)
                .execute()
            )
            return resposta.data

        if perfil == "AUXILIAR":
            # Auxiliar vê apenas as turmas em que é auxiliar
            usuario_id = usuario_logado.get("id")
            resposta = (
                supabase
                .table("turmas")
                .select("id, nome, professor:usuarios!professor_id(nome)")
                .eq("auxiliar_id", usuario_id)
                .execute()
            )
            return resposta.data

        if perfil == "ALUNO":
            # Aluno vê apenas as turmas em que participa
            usuario_id = usuario_logado.get("id")
            resposta = (
                supabase
                .table("alunos_aula")
                .select("aulas(turma_id)")
                .eq("aluno_id", usuario_id)
                .execute()
            )
            turma_ids = [item["aulas"]["turma_id"] for item in resposta.data if item.get("aulas")]
            if turma_ids:
                return [t for t in turmas if t.get("id") in turma_ids]
            return []

        return turmas
    except Exception as e:
        st.error(f"Erro ao listar turmas com isolamento: {e}")
        return []


def listar_alunos():
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


def listar_conteudos():
    try:
        resposta = (
            supabase
            .table("conteudos")
            .select("*")
            .order("categoria")
            .order("fase")
            .order("titulo")
            .execute()
        )
        return resposta.data
    except Exception as e:
        st.error(f"Erro ao carregar conteúdos: {e}")
        return []


def criar_aula(dados):
    try:
        resposta = supabase.table("aulas").insert(dados).execute()
        return resposta.data[0]["id"] if resposta.data else None
    except Exception as e:
        st.error(f"Erro ao criar aula: {e}")
        return None


def registrar_presenca(dados_presenca):
    try:
        if isinstance(dados_presenca, list):
            supabase.table("alunos_aula").insert(dados_presenca).execute()
        else:
            supabase.table("alunos_aula").insert(dados_presenca).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao registrar presença: {e}")
        return False


# ================================
# SESSION STATE
# ================================

if "presenca" not in st.session_state:
    st.session_state.presenca = {}


# ================================
# CABEÇALHO
# ================================

st.title("🎼 Nova Aula")
st.caption("Registro de aulas e presença dos alunos")

# ================================
# DADOS DA AULA
# ================================

st.subheader("📚 Dados da Aula")

turmas = listar_turmas_com_isolamento()

if not turmas:
    st.warning("Nenhuma turma cadastrada. Crie uma turma primeiro para registrar uma aula.")
    st.stop()

lista_turmas = {t["nome"]: t for t in turmas if t.get("nome")}

if not lista_turmas:
    st.warning("Nenhuma turma válida foi encontrada no banco. Verifique os cadastros e tente novamente.")
    st.stop()

c1, c2, c3 = st.columns(3)

with c1:
    data = st.date_input(
        "Data",
        date.today()
    )

with c2:
    turma_nome = st.selectbox(
        "Turma",
        list(lista_turmas.keys())
    )
    turma_selecionada = lista_turmas[turma_nome]
    id_turma = turma_selecionada["id"]

with c3:
    professor_nome = turma_selecionada.get("professor", {}).get("nome", "—") if turma_selecionada.get("professor") else "—"
    st.text_input(
        "Professor",
        professor_nome,
        disabled=True
    )

c1, c2, c3 = st.columns(3)

with c1:
    tipo = st.selectbox(
        "Tipo",
        [
            "Prática",
            "Teórica",
            "Prática de Conjunto"
        ]
    )

with c2:
    conteudos = listar_conteudos()
    if conteudos:
        lista_conteudos = {f"{c['categoria']} - {c['titulo']}": c["id"] for c in conteudos if c.get("categoria") and c.get("titulo")}
        if lista_conteudos:
            conteudo_selecionado = st.selectbox(
                "Conteúdo",
                list(lista_conteudos.keys())
            )
            id_conteudo = lista_conteudos[conteudo_selecionado]
        else:
            st.info("Nenhum conteúdo válido cadastrado.")
            id_conteudo = None
    else:
        st.info("Nenhum conteúdo cadastrado.")
        id_conteudo = None

with c3:
    duracao = st.number_input(
        "Duração (min)",
        15,
        180,
        60
    )

obs = st.text_area(
    "Observações Gerais"
)

st.divider()

# ================================
# ================================
# ALUNOS
# ================================

st.subheader("👨‍🎓 Alunos")

alunos = listar_alunos_com_isolamento()

if not alunos:
    st.info("Nenhum aluno cadastrado. Cadastre usuários de perfil ALUNO para continuar.")
    st.stop()

alunos_na_turma = alunos
lista_alunos = {a["nome"]: a["id"] for a in alunos_na_turma if a.get("nome")}

if not lista_alunos:
    st.warning("Nenhum aluno válido foi encontrado para registrar presença.")
    st.stop()

status_opcoes = [
    "Pendente",
    "Em andamento",
    "Concluído"
]

# Aplicação global
st.subheader("⚙ Aplicação Global")

c_global1, c_global2, c_global3 = st.columns([2, 2, 1])

with c_global1:
    status_global = st.selectbox(
        "Status",
        status_opcoes
    )

with c_global2:
    especificacao_global = st.text_input(
        "Especificação"
    )

with c_global3:
    aplicar = st.button(
        "Aplicar"
    )

if aplicar:
    for nome_aluno in lista_alunos.keys():
        st.session_state.presenca[nome_aluno] = {
            "presente": True,
            "status": status_global,
            "especificacao": especificacao_global
        }

st.divider()

# Lista individual de alunos
for nome_aluno in lista_alunos.keys():

    if nome_aluno not in st.session_state.presenca:
        st.session_state.presenca[nome_aluno] = {
            "presente": True,
            "status": "Pendente",
            "especificacao": ""
        }

    with st.container(border=True):

        col1, col2, col3, col4, col5 = st.columns([3, 1.5, 2, 2, 1])

        with col1:
            st.markdown(f"### {nome_aluno}")

        with col2:
            presente = st.checkbox(
                "Presente",
                st.session_state.presenca[nome_aluno]["presente"],
                key=f"presente_{nome_aluno}"
            )

        with col3:
            status_individual = st.selectbox(
                "Status",
                status_opcoes,
                index=status_opcoes.index(
                    st.session_state.presenca[nome_aluno]["status"]
                ),
                key=f"status_{nome_aluno}"
            )

        with col4:
            st.text_input(
                "Especificação",
                st.session_state.presenca[nome_aluno]["especificacao"],
                key=f"esp_{nome_aluno}"
            )

        with col5:
            if st.button(
                "📖",
                key=f"licao_{nome_aluno}"
            ):
                st.session_state.aluno = nome_aluno

# ================================
# PAINEL DE LIÇÕES
# ================================

if "aluno" in st.session_state:

    st.divider()

    st.subheader(
        f"📖 Lições - {st.session_state.aluno}"
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        if conteudos:
            categorias_lista = sorted(set(c["categoria"] for c in conteudos))
            categoria_licao = st.selectbox(
                "Categoria",
                categorias_lista,
                key="categoria"
            )
        else:
            st.info("Nenhuma categoria disponível")

    with c2:
        licao = st.text_input(
            "Lição",
            key="licao"
        )

    with c3:
        situacao = st.selectbox(
            "Situação",
            status_opcoes,
            key="situacao"
        )

    st.text_area(
        "Observações",
        key="obs_licao"
    )

    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        st.button("➕ Adicionar Lição")

    with col_btn2:
        if st.button("❌ Fechar"):
            del st.session_state.aluno
            st.rerun()

st.divider()

# ================================
# BOTÃO SALVAR
# ================================

col_salvar, col_vazio = st.columns([6, 2])

with col_salvar:
    if st.button(
        "💾 Salvar Aula",
        use_container_width=True,
        type="primary"
    ):

        if not id_conteudo:
            st.warning("Selecione um conteúdo válido para a aula antes de salvar.")
        else:
            # 1. Criar a aula
            dados_aula = {
                "id_turma": id_turma,
                "id_conteudo": id_conteudo,
                "data_aula": str(data),
                "tipo": tipo,
                "duracao": duracao,
                "observacoes": obs
            }

            id_aula = criar_aula(dados_aula)

            if id_aula:
                # 2. Registrar presença de cada aluno
                presencas_para_inserir = []
                for nome_aluno, id_aluno in lista_alunos.items():
                    presenca = st.session_state.presenca.get(nome_aluno, {})
                    observacao = f"Status: {presenca.get('status', 'Pendente')} | Especificação: {presenca.get('especificacao', '')}".strip()
                    presencas_para_inserir.append({
                        "id_aula": id_aula,
                        "id_aluno": id_aluno,
                        "presenca": bool(presenca.get("presente", True)),
                        "observacao": observacao
                    })

                if presencas_para_inserir:
                    sucesso = registrar_presenca(presencas_para_inserir)
                    if sucesso:
                        st.success("Aula e presenças salvas com sucesso!")
                        st.session_state.presenca = {}
                        st.rerun()