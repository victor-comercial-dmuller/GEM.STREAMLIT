import streamlit as st
import pandas as pd
import json
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

@st.cache_data(ttl=60)
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
            resposta = (
                supabase
                .table("turmas")
                .select("id, nome, professor:usuarios!professor_id(nome)")
                .eq("professor_id", usuario_id)
                .execute()
            )
            return resposta.data

        if perfil == "AUXILIAR":
            resposta = (
                supabase
                .table("turmas")
                .select("id, nome, professor:usuarios!professor_id(nome)")
                .eq("auxiliar_id", usuario_id)
                .execute()
            )
            return resposta.data

        if perfil == "ALUNO":
            resposta = (
                supabase
                .table("alunos_aula")
                .select("aulas(id_turma)")
                .eq("aluno_id", usuario_id)
                .execute()
            )
            turma_ids = [item["aulas"]["id_turma"] for item in resposta.data if item.get("aulas")]
            if turma_ids:
                return [t for t in turmas if t.get("id") in turma_ids]
            return []

        return turmas
    except Exception as e:
        st.error(f"Erro ao listar turmas com isolamento: {e}")
        return []


@st.cache_data(ttl=60)
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


def listar_alunos_com_isolamento(id_turma=None):
    """Carrega alunos aplicando isolamento. Se id_turma for fornecido, filtra alunos dessa turma."""
    try:
        alunos = listar_alunos()

        # Filtra por usuarios.turma_id quando informado
        if id_turma is not None:
            alunos = [a for a in alunos if a.get("turma_id") == id_turma]

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

        if perfil in ["PROFESSOR", "AUXILIAR"]:
            # Vê alunos de sua localidade
            return [a for a in alunos if a.get("localidade_id") == localidade_id]

        if perfil == "ALUNO":
            return [a for a in alunos if a.get("id") == usuario_id]

        return alunos
    except Exception as e:
        st.error(f"Erro ao listar alunos com isolamento: {e}")
        return []


@st.cache_data(ttl=60)
def listar_conteudos():
    try:
        resposta = (
            supabase
            .table("conteudos")
            .select("*")
            .eq("ativo", True)
            .order("categoria")
            .order("titulo")
            .execute()
        )
        return resposta.data
    except Exception as e:
        st.error(f"Erro ao carregar conteúdos: {e}")
        return []


@st.cache_data(ttl=60)
def listar_aulas(id_turma):
    try:
        resposta = (
            supabase
            .table("aulas")
            .select("*")
            .eq("id_turma", id_turma)
            .order("data_aula")
            .execute()
        )
        return resposta.data
    except Exception as e:
        st.error(f"Erro ao carregar aulas: {e}")
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
        # aceita lista ou dict
        if isinstance(dados_presenca, list):
            resposta = supabase.table("alunos_aula").insert(dados_presenca).execute()
        else:
            resposta = supabase.table("alunos_aula").insert(dados_presenca).execute()
        # checar erros simples
        if getattr(resposta, 'error', None):
            st.error(f"Erro ao inserir lições: {resposta.error}")
            return False
        return True
    except Exception as e:
        st.error(f"Erro ao registrar lições: {e}")
        return False


def registrar_presencas(dados_presencas):
    try:
        if isinstance(dados_presencas, list):
            resposta = supabase.table("presencas").insert(dados_presencas).execute()
        else:
            resposta = supabase.table("presencas").insert(dados_presencas).execute()
        if getattr(resposta, 'error', None):
            st.error(f"Erro ao inserir presenças: {resposta.error}")
            return False
        return True
    except Exception as e:
        st.error(f"Erro ao registrar presenças: {e}")
        return False


# ================================
# SESSION STATE
# ================================

if "presenca" not in st.session_state:
    st.session_state.presenca = {}

if "licoes_status" not in st.session_state:
    st.session_state.licoes_status = {}

if "global_licoes_status" not in st.session_state:
    st.session_state.global_licoes_status = {}

NORMAL_STATUS = ["PENDENTE", "EM ANDAMENTO", "CONCLUÍDO"]

for _nome, info in list(st.session_state.presenca.items()):
    s = info.get("status", "PENDENTE")
    if isinstance(s, str):
        s_norm = s.strip().upper()
        if s_norm not in NORMAL_STATUS:
            s_norm = "PENDENTE"
        st.session_state.presenca[_nome]["status"] = s_norm

for _nome, mapa in list(st.session_state.licoes_status.items()):
    for k, v in list(mapa.items()):
        if isinstance(v, str):
            vv = v.strip().upper()
            if vv not in NORMAL_STATUS:
                vv = "PENDENTE"
            st.session_state.licoes_status[_nome][k] = vv

# ================================
# CABEÇALHO
# ================================

st.title("🎼 Nova Aula")
st.caption("Registro de aulas, presença e lições aplicadas")
st.markdown("""
<style>
/* Layout centralizado e botões mais bonitos */
.aulas-wrapper{max-width:1100px;margin-left:auto;margin-right:auto;padding:12px}
.aula-save-btn .stButton>button{background:#0b5ed7;color:white;border-radius:6px;padding:10px 18px}
.badge-presenca{font-weight:600;padding:3px 8px;border-radius:5px}
.presente{background:#d4edda;color:#155724}
.ausente{background:#f8d7da;color:#721c24}
.licao-badge{padding:4px 8px;border-radius:6px;border:1px solid #e9ecef;background:#fff}
</style>
<div class='aulas-wrapper'>
""", unsafe_allow_html=True)

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
    data = st.date_input("Data", date.today())

with c2:
    turma_nome = st.selectbox("Turma", list(lista_turmas.keys()))
    turma_selecionada = lista_turmas[turma_nome]
    id_turma = turma_selecionada["id"]

with c3:
    professor_nome = turma_selecionada.get("professor", {}).get("nome", "—") if turma_selecionada.get("professor") else "—"
    st.text_input("Professor", professor_nome, disabled=True)

c1, c2, c3 = st.columns(3)

# Carregar conteúdos e categorias
if "cache_conteudos" not in st.session_state:
    st.session_state.cache_conteudos = listar_conteudos()
conteudos = st.session_state.cache_conteudos
categorias = sorted({c.get("categoria") for c in conteudos if c.get("categoria")}) if conteudos else []

with c1:
    if categorias:
        tipo = st.selectbox("Tipo", categorias)
    else:
        st.info("Nenhuma categoria disponível")
        tipo = None

with c2:
    id_conteudo = None
    conteudo_selecionado = None
    if conteudos and tipo:
        conteudos_filtrados = sorted([c for c in conteudos if c.get("categoria") == tipo], key=lambda x: x.get("titulo",""))
        lista_conteudos = {f"{c['titulo']}": c["id"] for c in conteudos_filtrados if c.get("titulo")}
        if lista_conteudos:
            escolha = st.selectbox("Conteúdo", list(lista_conteudos.keys()))
            id_conteudo = lista_conteudos[escolha]
            conteudo_selecionado = next((c for c in conteudos_filtrados if c["id"] == id_conteudo), None)
        else:
            st.info("Nenhum conteúdo ativo para o tipo selecionado.")
    else:
        st.info("Selecione um Tipo para ver conteúdos.")

with c3:
    duracao = st.number_input("Duração (min)", 15, 180, 60)

obs = st.text_area("Observações Gerais")

st.divider()

st.markdown("<div style='max-width:1100px; margin-left:auto; margin-right:auto;'>", unsafe_allow_html=True)

# ================================
# ALUNOS
# ================================

st.subheader("👨‍🎓 Alunos")

alunos_na_turma = listar_alunos_com_isolamento(id_turma)

if not alunos_na_turma:
    st.info("Nenhum aluno cadastrado nesta turma.")
    st.stop()

lista_alunos = {a["nome"]: a["id"] for a in alunos_na_turma if a.get("nome")}

if not lista_alunos:
    st.warning("Nenhum aluno válido foi encontrado para registrar presença.")
    st.stop()

# Status padrão — não usar listas fixas em outros lugares, mas estes são os valores exigidos
status_opcoes = ["PENDENTE", "EM ANDAMENTO", "CONCLUÍDO"]

# Inicializar novos estados de lições
default_presenca = {
    "presente": False,
    "status": "PENDENTE",
    "especificacao": "",
    "justificativa": "",
    "tipo": "Usar geral",
    "id_conteudo": None
}

if "licoes_status" not in st.session_state:
    st.session_state.licoes_status = {}

if "presenca" not in st.session_state:
    st.session_state.presenca = {}

if "global_licoes_status" not in st.session_state:
    st.session_state.global_licoes_status = {"_conteudo_id": None}

if "global_presenca" not in st.session_state:
    st.session_state.global_presenca = False

emoji_map = {"PENDENTE": "⚪", "EM ANDAMENTO": "🟡", "CONCLUÍDO": "🟢"}

st.subheader("⚙ Aplicação Global")
with st.expander("Global", expanded=True):
    st.write("Use este painel para aplicar mudanças de status a todos os alunos marcados como presentes.")
    if st.button("Confirmar presença para todos", key="btn_global_presenca", use_container_width=True):
        st.session_state.global_presenca = not st.session_state.global_presenca
        for nome_aluno in lista_alunos.keys():
            st.session_state.presenca.setdefault(nome_aluno, default_presenca.copy())
            st.session_state.presenca[nome_aluno]["presente"] = st.session_state.global_presenca

    st.write("**Presença geral:**", "Sim" if st.session_state.global_presenca else "Não")

    with st.expander("Lições", expanded=True):
        if not conteudo_selecionado:
            st.info("Selecione um conteúdo para ver as lições.")
        else:
            inicio = int(conteudo_selecionado.get("licao_inicial", 1) or 1)
            fim = int(conteudo_selecionado.get("licao_final", inicio) or inicio)
            if st.session_state.global_licoes_status.get("_conteudo_id") != id_conteudo:
                st.session_state.global_licoes_status = {"_conteudo_id": id_conteudo}
                for n in range(inicio, fim + 1):
                    st.session_state.global_licoes_status[str(n)] = "PENDENTE"

            total = fim - inicio + 1
            per_row = 8
            rows = (total + per_row - 1) // per_row
            for r in range(rows):
                cols = st.columns(per_row)
                for i in range(per_row):
                    idx = inicio + r * per_row + i
                    if idx > fim:
                        cols[i].write("")
                        continue
                    status_atual = st.session_state.global_licoes_status.get(str(idx), "PENDENTE")
                    status_norm = status_atual.strip().upper() if isinstance(status_atual, str) else "PENDENTE"
                    current_index = status_opcoes.index(status_norm) if status_norm in status_opcoes else 0
                    next_status = status_opcoes[(current_index + 1) % len(status_opcoes)]
                    emoji = emoji_map.get(status_norm, "⚪")
                    label = f"{idx} — {emoji} {status_norm}"
                    if cols[i].button(label, key=f"btn_global_licao_{idx}", use_container_width=True):
                        st.session_state.global_licoes_status[str(idx)] = next_status
                        for nome_aluno in lista_alunos.keys():
                            if st.session_state.presenca.get(nome_aluno, default_presenca)["presente"]:
                                aluno_tipo = st.session_state.presenca[nome_aluno].get("tipo", "Usar geral")
                                aluno_id_conteudo = st.session_state.presenca[nome_aluno].get("id_conteudo")
                                if not aluno_id_conteudo or aluno_tipo == "Usar geral":
                                    aluno_id_conteudo = id_conteudo
                                if aluno_id_conteudo:
                                    st.session_state.licoes_status.setdefault(nome_aluno, {"_conteudo_id": aluno_id_conteudo})
                                    st.session_state.licoes_status[nome_aluno]["_conteudo_id"] = aluno_id_conteudo
                                    st.session_state.licoes_status[nome_aluno][str(idx)] = next_status

    st.write("**Status global atual:**")
    status_labels = [f"{k}: {v}" for k, v in st.session_state.global_licoes_status.items() if k != "_conteudo_id"]
    if status_labels:
        st.write(", ".join(status_labels))
    else:
        st.write("Nenhuma lição configurada ainda.")

st.divider()

# Lista individual de alunos em expander
for nome_aluno, id_aluno in lista_alunos.items():

    if nome_aluno not in st.session_state.presenca:
        st.session_state.presenca[nome_aluno] = {
            "presente": False,
            "status": "PENDENTE",
            "especificacao": "",
            "justificativa": "",
            "tipo": "Usar geral",
            "id_conteudo": None
        }

    st.session_state.licoes_status.setdefault(nome_aluno, {})

    with st.expander(nome_aluno, expanded=False):
        st.write("### ", nome_aluno)
        if st.button(
            "Confirmar presença",
            key=f"btn_presenca_{nome_aluno}",
            use_container_width=True
        ):
            st.session_state.presenca[nome_aluno]["presente"] = not st.session_state.presenca[nome_aluno]["presente"]

        st.write("**Presença:**", "Sim" if st.session_state.presenca[nome_aluno]["presente"] else "Não")

        tipo_opcoes_aluno = ["Usar geral"] + categorias if categorias else ["Usar geral"]
        tipo_aluno = st.selectbox(
            "Tipo do aluno",
            tipo_opcoes_aluno,
            index=tipo_opcoes_aluno.index(st.session_state.presenca[nome_aluno].get("tipo", "Usar geral")) if st.session_state.presenca[nome_aluno].get("tipo", "Usar geral") in tipo_opcoes_aluno else 0,
            key=f"tipo_aluno_{id_aluno}"
        )
        st.session_state.presenca[nome_aluno]["tipo"] = tipo_aluno

        aluno_conteudo_id = st.session_state.presenca[nome_aluno].get("id_conteudo")
        conteudo_selecionado_aluno = None
        if tipo_aluno != "Usar geral":
            conteudos_filtrados_aluno = sorted([c for c in conteudos if c.get("categoria") == tipo_aluno], key=lambda x: x.get("titulo", ""))
            lista_conteudos_aluno = {f"{c['titulo']}": c["id"] for c in conteudos_filtrados_aluno if c.get("titulo")}
            if lista_conteudos_aluno:
                conteudo_nomes = list(lista_conteudos_aluno.keys())
                selected_index = 0
                if aluno_conteudo_id and any(v == aluno_conteudo_id for v in lista_conteudos_aluno.values()):
                    selected_name = next((k for k, v in lista_conteudos_aluno.items() if v == aluno_conteudo_id), None)
                    if selected_name and selected_name in conteudo_nomes:
                        selected_index = conteudo_nomes.index(selected_name)
                conteudo_nome_aluno = st.selectbox(
                    "Conteúdo do aluno",
                    conteudo_nomes,
                    index=selected_index,
                    key=f"conteudo_aluno_{id_aluno}"
                )
                aluno_conteudo_id = lista_conteudos_aluno[conteudo_nome_aluno]
                conteudo_selecionado_aluno = next((c for c in conteudos_filtrados_aluno if c.get("id") == aluno_conteudo_id), None)
            else:
                st.info("Nenhum conteúdo ativo para o tipo selecionado deste aluno.")
                aluno_conteudo_id = None
        else:
            aluno_conteudo_id = id_conteudo
            conteudo_selecionado_aluno = conteudo_selecionado
            st.info("Usando tipo e conteúdo gerais da aula.")

        st.session_state.presenca[nome_aluno]["id_conteudo"] = aluno_conteudo_id

        justificativa = st.text_area(
            "Justificativa",
            value=st.session_state.presenca[nome_aluno].get("justificativa", ""),
            key=f"justificativa_{id_aluno}",
            height=80
        )
        st.session_state.presenca[nome_aluno]["justificativa"] = justificativa

        with st.expander("Lições", expanded=False):
            if not conteudo_selecionado_aluno:
                st.info("Selecione um conteúdo válido para ver as lições deste aluno.")
            else:
                inicio = int(conteudo_selecionado_aluno.get("licao_inicial", 1) or 1)
                fim = int(conteudo_selecionado_aluno.get("licao_final", inicio) or inicio)
                total = fim - inicio + 1
                per_row = 8
                rows = (total + per_row - 1) // per_row

                if st.session_state.licoes_status[nome_aluno].get("_conteudo_id") != aluno_conteudo_id:
                    st.session_state.licoes_status[nome_aluno] = {"_conteudo_id": aluno_conteudo_id}
                    for n in range(inicio, fim + 1):
                        st.session_state.licoes_status[nome_aluno].setdefault(str(n), "PENDENTE")

                for r in range(rows):
                    cols = st.columns(per_row)
                    for i in range(per_row):
                        idx = inicio + r * per_row + i
                        if idx > fim:
                            cols[i].write("")
                            continue
                        status_atual = st.session_state.licoes_status[nome_aluno].get(str(idx), "PENDENTE")
                        status_norm = status_atual.strip().upper() if isinstance(status_atual, str) else "PENDENTE"
                        current_index = status_opcoes.index(status_norm) if status_norm in status_opcoes else 0
                        next_status = status_opcoes[(current_index + 1) % len(status_opcoes)]
                        emoji = emoji_map.get(status_norm, "⚪")
                        label = f"{idx} — {emoji} {status_norm}"
                        if cols[i].button(label, key=f"btn_licao_{nome_aluno}_{idx}", use_container_width=True):
                            st.session_state.licoes_status[nome_aluno][str(idx)] = next_status
                            if not st.session_state.presenca[nome_aluno]["presente"]:
                                st.session_state.presenca[nome_aluno]["presente"] = True

        # ================================
        # BOTÃO SALVAR
        # ================================

cols_center = st.columns([1, 2, 1])
with cols_center[1]:
    st.markdown("<div style='text-align:center' class='aula-save-btn'>", unsafe_allow_html=True)
    if st.button("💾 Salvar Aula", use_container_width=True, type="primary"):
        if not id_conteudo:
            st.warning("Selecione um conteúdo válido para a aula antes de salvar.")
        else:
            dados_aula = {
                "id_turma": id_turma,
                "id_conteudo": id_conteudo,
                "data_aula": str(data),
                "tipo": tipo,
                "duracao": duracao,
                "observacoes": obs
            }
            id_aula = criar_aula(dados_aula)
            if not id_aula:
                st.error("Falha ao criar a aula.")
            else:
                registros_presencas = []
                registros_aulas = []
                for nome_aluno, id_aluno in lista_alunos.items():
                    presente = st.session_state.presenca.get(nome_aluno, {}).get("presente", False)
                    justificativa = st.session_state.presenca.get(nome_aluno, {}).get("justificativa", "") or ""
                    registros_presencas.append({
                        "id_aula": id_aula,
                        "id_aluno": id_aluno,
                        "presenca": presente,
                        "justificativa": justificativa.strip()
                    })

                    aluno_tipo_selecionado = st.session_state.presenca[nome_aluno].get("tipo", "Usar geral")
                    aluno_conteudo_id = st.session_state.presenca[nome_aluno].get("id_conteudo")
                    if aluno_tipo_selecionado == "Usar geral":
                        aluno_tipo_selecionado = tipo
                        aluno_conteudo_id = id_conteudo

                    if not presente or not aluno_conteudo_id:
                        continue

                    conteudo_selecionado_aluno = next((c for c in conteudos if c.get("id") == aluno_conteudo_id), None)
                    if not conteudo_selecionado_aluno:
                        continue

                    inicio = int(conteudo_selecionado_aluno.get("licao_inicial", 1) or 1)
                    fim = int(conteudo_selecionado_aluno.get("licao_final", inicio) or inicio)
                    licoes_por_aluno = st.session_state.licoes_status.get(nome_aluno, {})

                    for li in range(inicio, fim + 1):
                        status_li = licoes_por_aluno.get(str(li), "PENDENTE")
                        if isinstance(status_li, str):
                            status_li = status_li.strip().upper()
                        if status_li not in status_opcoes:
                            status_li = "PENDENTE"

                        if status_li != "PENDENTE":
                            registros_aulas.append({
                                "id_aula": id_aula,
                                "id_aluno": id_aluno,
                                "tipo": aluno_tipo_selecionado,
                                "conteudo": conteudo_selecionado_aluno.get("titulo", ""),
                                "status_conteudo": status_li,
                                "licao": str(li)
                            })

                sucesso_presencas = registrar_presencas(registros_presencas)
                sucesso_licoes = True
                if registros_aulas:
                    sucesso_licoes = registrar_presenca(registros_aulas)

                if sucesso_presencas and sucesso_licoes:
                    st.success("Aula, presenças e lições salvas com sucesso!")
                    st.session_state.presenca = {}
                    st.session_state.licoes_status = {}
                    st.session_state.global_licoes_status = {"_conteudo_id": None}
                    st.session_state.global_presenca = False
                elif sucesso_presencas and not registros_aulas:
                    st.success("Aula e presenças salvas com sucesso! Nenhuma lição diferente de PENDENTE foi marcada.")
                    st.session_state.presenca = {}
                    st.session_state.licoes_status = {}
                    st.session_state.global_licoes_status = {"_conteudo_id": None}
                    st.session_state.global_presenca = False
                elif not sucesso_presencas:
                    st.error("Falha ao salvar as presenças. Consulte os logs.")
                else:
                    st.error("Falha ao salvar as lições. Consulte os logs.")
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# Histórico de Aulas
# ================================
st.subheader("📜 Histórico de Aulas")
try:
    aulas_turma = listar_aulas(id_turma)
except Exception:
    aulas_turma = []

if not aulas_turma:
    st.info("Nenhuma aula registrada para esta turma.")
else:
    for aula in aulas_turma:
        titulo = f"{aula.get('data_aula')} — {aula.get('tipo','')} — {aula.get('duracao','')}min"
        with st.expander(titulo, expanded=False):
            c1, c2, c3, c4 = st.columns([2, 2, 1, 3])
            c1.write("**Data**")
            c1.write(aula.get('data_aula'))
            c2.write("**Tipo**")
            c2.write(aula.get('tipo'))
            c3.write("**Duração**")
            c3.write(f"{aula.get('duracao')} min")
            c4.write("**Observações**")
            c4.write(aula.get('observacoes',''))

            # Ver alunos
            with st.expander("Ver alunos", expanded=False):
                resp = (
                    supabase
                    .table('presencas')
                    .select('id, id_aluno, presenca, justificativa')
                    .eq('id_aula', aula.get('id'))
                    .execute()
                )
                registros = resp.data or []
                if not registros:
                    st.write("Nenhum aluno registrado nesta aula.")
                else:
                    ids = [r.get('id_aluno') for r in registros]
                    usuarios_resp = supabase.table('usuarios').select('id, nome').in_('id', ids).execute()
                    usuarios_map = {u['id']: u.get('nome','') for u in (usuarios_resp.data or [])}
                    for r in registros:
                        nome = usuarios_map.get(r.get('id_aluno'), str(r.get('id_aluno')))
                        presente = r.get('presenca', False)
                        justificativa = r.get('justificativa', '')
                        badge = "<span class='badge-presenca presente'>Presente</span>" if presente else "<span class='badge-presenca ausente'>Ausente</span>"
                        st.markdown(f"**{nome}** — {badge}", unsafe_allow_html=True)
                        if justificativa:
                            st.markdown(f"**Justificativa:** {justificativa}")

            # Lições
            with st.expander("Lições", expanded=False):
                resp2 = (
                    supabase
                    .table('alunos_aula')
                    .select('id, id_aluno, tipo, conteudo, licao, status_conteudo')
                    .eq('id_aula', aula.get('id'))
                    .order('id_aluno')
                    .execute()
                )
                reg2 = resp2.data or []
                if not reg2:
                    st.write("Nenhuma lição registrada.")
                else:
                    ids2 = [r.get('id_aluno') for r in reg2]
                    usuarios_resp2 = supabase.table('usuarios').select('id, nome').in_('id', ids2).execute()
                    usuarios_map2 = {u['id']: u.get('nome','') for u in (usuarios_resp2.data or [])}
                    tabela = []
                    for r in reg2:
                        tabela.append({
                            'Aluno': usuarios_map2.get(r.get('id_aluno'), r.get('id_aluno')),
                            'Tipo': r.get('tipo') or aula.get('tipo', ''),
                            'Conteúdo': r.get('conteudo') or '',
                            'Lição': r.get('licao'),
                            'Status': r.get('status_conteudo')
                        })
                    st.table(pd.DataFrame(tabela))

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)



