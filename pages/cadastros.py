import pandas as pd
import streamlit as st

from database.usuarios import (
    listar_usuarios,
    inserir_usuario,
    editar_usuario,
    excluir_usuario,
    listar_professores,
    listar_auxiliares
)

from database.regioes import (
    listar_regioes,
    inserir_regiao,
    editar_regiao,
    excluir_regiao,
)

from database.localidades import (
    listar_localidades,
    inserir_localidade,
    editar_localidade,
    excluir_localidade,
)

from database.turmas import (
    listar_turmas,
    inserir_turma,
    editar_turma,
    excluir_turma,
    desvincular_professor,
    desvincular_auxiliar,
)


def _get_perfis_disponiveis(perfil_logado: str):
    if perfil_logado in ["ADMIN", "TI"]:
        return [
            "ADMIN",
            "COORDENADOR REGIONAL",
            "COORDENADOR LOCAL",
            "PROFESSOR",
            "AUXILIAR",
            "ALUNO",
        ]
    if perfil_logado == "COORDENADOR REGIONAL":
        return [
            "COORDENADOR LOCAL",
            "PROFESSOR",
            "AUXILIAR",
            "ALUNO",
        ]
    if perfil_logado == "COORDENADOR LOCAL":
        return [
            "PROFESSOR",
            "AUXILIAR",
            "ALUNO",
        ]
    if perfil_logado == "PROFESSOR":
        return [
            "AUXILIAR",
            "ALUNO",
        ]
    if perfil_logado == "AUXILIAR":
        return ["ALUNO"]
    return ["ALUNO"]


def _is_admin(perfil_logado: str):
    return perfil_logado in ["ADMIN", "TI"]


def _deve_pedir_localidade(perfil_alvo: str):
    return perfil_alvo != "COORDENADOR REGIONAL"


def _deve_pedir_turma(perfil_alvo: str):
    return perfil_alvo in ["PROFESSOR", "AUXILIAR", "ALUNO"]


def _turmas_do_usuario(usuario_atual):
    turmas = listar_turmas()
    perfil = usuario_atual.get("perfil", "—")
    usuario_id = usuario_atual.get("id")

    if perfil in ["ADMIN", "TI"]:
        return turmas

    return [
        turma for turma in turmas
        if turma.get("professor_id") == usuario_id
        or turma.get("auxiliar_id") == usuario_id
    ]


def _turma_atual_por_campo(usuario_id, campo):
    for turma in listar_turmas():
        if turma.get(campo) == usuario_id:
            return turma
    return None


def _regioes_acessiveis(usuario_atual):
    perfil = usuario_atual.get("perfil", "—")
    regiao_id = usuario_atual.get("regiao_id")
    regioes = listar_regioes()

    if perfil in ["ADMIN", "TI"]:
        return regioes

    if regiao_id:
        return [regiao for regiao in regioes if regiao.get("id") == regiao_id]

    return []


def _localidades_acessiveis(usuario_atual, regioes_ids=None):
    perfil = usuario_atual.get("perfil", "—")
    regiao_id = usuario_atual.get("regiao_id")
    localidade_id = usuario_atual.get("localidade_id")
    localidades = listar_localidades()

    if perfil in ["ADMIN", "TI"]:
        return localidades

    # COORDENADOR LOCAL: visualiza apenas sua própria localidade
    if perfil == "COORDENADOR LOCAL":
        if localidade_id:
            return [
                localidade for localidade in localidades
                if localidade.get("id") == localidade_id
            ]
        return []

    if regioes_ids:
        return [
            localidade for localidade in localidades
            if localidade.get("regiao_id") in regioes_ids
        ]

    if regiao_id:
        return [
            localidade for localidade in localidades
            if localidade.get("regiao_id") == regiao_id
        ]

    return []


def _turmas_acessiveis(usuario_atual, regioes_ids=None, localidades_ids=None):
    perfil = usuario_atual.get("perfil", "—")
    regiao_id = usuario_atual.get("regiao_id")
    localidade_id = usuario_atual.get("localidade_id")
    usuario_id = usuario_atual.get("id")
    turmas = listar_turmas()

    if perfil in ["ADMIN", "TI"]:
        return turmas

    # COORDENADOR LOCAL: visualiza apenas turmas de sua localidade
    if perfil == "COORDENADOR LOCAL":
        if localidade_id:
            return [
                turma for turma in turmas
                if turma.get("localidade_id") == localidade_id
            ]
        return []

    # PROFESSOR: visualiza apenas turmas onde é professor
    if perfil == "PROFESSOR":
        return [
            turma for turma in turmas
            if turma.get("professor_id") == usuario_id
        ]

    # AUXILIAR: visualiza apenas turmas onde é auxiliar
    if perfil == "AUXILIAR":
        return [
            turma for turma in turmas
            if turma.get("auxiliar_id") == usuario_id
        ]

    # Para outros perfis (COORDENADOR REGIONAL, ALUNO): aplica filtros hierárquicos
    filtradas = []
    for turma in turmas:
        if regioes_ids and turma.get("regiao_id") not in regioes_ids:
            continue
        if localidades_ids and turma.get("localidade_id") not in localidades_ids:
            continue

        if regiao_id and turma.get("regiao_id") != regiao_id:
            continue
        if localidade_id and turma.get("localidade_id") != localidade_id:
            continue

        filtradas.append(turma)

    return filtradas


def _filtrar_usuarios_por_acesso(usuarios, usuario_atual):
    perfil = usuario_atual.get("perfil", "—")
    regiao_id = usuario_atual.get("regiao_id")
    localidade_id = usuario_atual.get("localidade_id")
    usuario_id = usuario_atual.get("id")

    if perfil in ["ADMIN", "TI"]:
        return usuarios

    if perfil == "COORDENADOR REGIONAL":
        return [
            usuario for usuario in usuarios
            if usuario.get("regiao_id") == regiao_id
        ]

    if perfil == "COORDENADOR LOCAL":
        return [
            usuario for usuario in usuarios
            if usuario.get("localidade_id") == localidade_id
        ]

    if perfil == "PROFESSOR":
        # Professor vê apenas alunos das turmas onde é professor
        turmas_do_professor = [turma for turma in listar_turmas() if turma.get("professor_id") == usuario_id]
        turmas_ids = {turma.get("id") for turma in turmas_do_professor}
        
        return [
            usuario for usuario in usuarios
            if usuario.get("perfil") == "ALUNO" and any(
                aluno_turma.get("turma_id") in turmas_ids
                for aluno_turma in _alunos_turma(usuario.get("id"))
            )
        ]

    if perfil == "AUXILIAR":
        # Auxiliar vê apenas alunos das turmas onde é auxiliar
        turmas_do_auxiliar = [turma for turma in listar_turmas() if turma.get("auxiliar_id") == usuario_id]
        turmas_ids = {turma.get("id") for turma in turmas_do_auxiliar}
        
        return [
            usuario for usuario in usuarios
            if usuario.get("perfil") == "ALUNO" and any(
                aluno_turma.get("turma_id") in turmas_ids
                for aluno_turma in _alunos_turma(usuario.get("id"))
            )
        ]

    if perfil == "ALUNO":
        # Aluno vê apenas a si próprio
        return [usuario for usuario in usuarios if usuario.get("id") == usuario_id]

    return []


def _alunos_turma(aluno_id):
    """Retorna as turmas de um aluno. Para implementação futura quando houver tabela de vínculo aluno-turma."""
    return []


def _professores_acessiveis(usuario_atual):
    """Retorna professores acessíveis ao usuário atual, respeitando isolamento por localidade."""
    perfil = usuario_atual.get("perfil", "—")
    localidade_id = usuario_atual.get("localidade_id")
    regiao_id = usuario_atual.get("regiao_id")
    
    professores = listar_professores()
    
    if perfil in ["ADMIN", "TI"]:
        return professores
    
    if perfil == "COORDENADOR LOCAL":
        # Coordenador Local vê apenas professores de sua localidade
        return [p for p in professores if p.get("localidade_id") == localidade_id]
    
    if perfil == "COORDENADOR REGIONAL":
        # Coordenador Regional vê apenas professores de sua região
        return [p for p in professores if p.get("regiao_id") == regiao_id]
    
    # Outros perfis veem apenas professores acessíveis por localidade
    return [p for p in professores if p.get("localidade_id") == localidade_id]


def _auxiliares_acessiveis(usuario_atual):
    """Retorna auxiliares acessíveis ao usuário atual, respeitando isolamento por localidade."""
    perfil = usuario_atual.get("perfil", "—")
    localidade_id = usuario_atual.get("localidade_id")
    regiao_id = usuario_atual.get("regiao_id")
    
    auxiliares = listar_auxiliares()
    
    if perfil in ["ADMIN", "TI"]:
        return auxiliares
    
    if perfil == "COORDENADOR LOCAL":
        # Coordenador Local vê apenas auxiliares de sua localidade
        return [a for a in auxiliares if a.get("localidade_id") == localidade_id]
    
    if perfil == "COORDENADOR REGIONAL":
        # Coordenador Regional vê apenas auxiliares de sua região
        return [a for a in auxiliares if a.get("regiao_id") == regiao_id]
    
    # Outros perfis veem apenas auxiliares acessíveis por localidade
    return [a for a in auxiliares if a.get("localidade_id") == localidade_id]


if "usuario" not in st.session_state or not st.session_state.usuario:
    st.info("Faça login para acessar os cadastros.")
    st.stop()

usuario = st.session_state.usuario
perfil_logado = usuario.get("perfil", "—")


st.title("📋 Cadastros")

aba1,aba2,aba3,aba4 = st.tabs([
"👥 Usuários",
"🌏 Região",
"📍Localidade",
"👨🏻‍🎓👨🏽‍🎓👨🏿‍🎓TURMA",
])


with aba1:
    # identificação usuário
    usuario = st.session_state.usuario
    perfil_logado = usuario.get("perfil", "—")



    st.title("👥 Usuários")

    regioes_disponiveis = _regioes_acessiveis(usuario)

    def get_usuarios_por_perfil(perfil):
        usuarios_todos = [u for u in listar_usuarios() if u.get("Perfil") == perfil]
        
        # Aplicar isolamento conforme perfil do usuário logado
        return _filtrar_usuarios_por_acesso(usuarios_todos, usuario)

    def render_usuarios_tabela(usuarios, titulo):
        st.markdown(f"### {titulo}")
        if usuarios:
            df = pd.DataFrame(usuarios)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=250,
            )
        else:
            st.info(f"Nenhum usuário {titulo.lower()} cadastrado.")

    def format_usuario(usuario_item):
        return f"{usuario_item['Nome']} ({usuario_item['Login']})"

    def render_form_admin():
        usuarios = get_usuarios_por_perfil("ADMIN")
        with st.form("form_admin"):
            nome = st.text_input("Nome", key="admin_nome")
            login = st.text_input("Login", key="admin_login")
            senha = st.text_input("Senha", type="password", key="admin_senha")

            form_invalido = (
                not nome
                or not login
                or not senha
            )

            col_salvar, col_cancelar = st.columns(2)
            with col_salvar:
                salvar = st.form_submit_button("Salvar")
            with col_cancelar:
                cancelar = st.form_submit_button("Cancelar")

            if salvar:
                if form_invalido:
                    st.error("Preencha todos os campos obrigatórios para ADMIN.")
                else:
                    try:
                        inserir_usuario(
                            nome,
                            login,
                            senha,
                            "ADMIN",
                            None,
                            None,
                        )
                        st.success("Usuário ADMIN criado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao criar usuário: {e}")

            if cancelar:
                st.rerun()

        render_usuarios_tabela(usuarios, "ADMIN")

        if usuarios:
            selected_usuario = st.selectbox(
                "Selecionar ADMIN para editar/excluir",
                usuarios,
                format_func=format_usuario,
                key="admin_select_usuario"
            )
            if selected_usuario:
                with st.form("form_edit_admin"):
                    nome_edit = st.text_input(
                        "Nome",
                        value=selected_usuario["Nome"],
                        key=f"admin_edit_nome_{selected_usuario['id']}"
                    )
                    login_edit = st.text_input(
                        "Login",
                        value=selected_usuario["Login"],
                        key=f"admin_edit_login_{selected_usuario['id']}"
                    )
                    status_edit = st.text_input(
                        "Status",
                        value=selected_usuario.get("Status", ""),
                        key=f"admin_edit_status_{selected_usuario['id']}"
                    )

                    col_update, col_delete = st.columns(2)
                    with col_update:
                        salvar_edit = st.form_submit_button("Salvar alterações")
                    with col_delete:
                        excluir = st.form_submit_button("Excluir")

                    if salvar_edit:
                        try:
                            editar_usuario(
                                selected_usuario["id"],
                                nome_edit,
                                login_edit,
                                "ADMIN",
                                status_edit,
                            )
                            st.success("Usuário ADMIN atualizado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar usuário: {e}")

                    if excluir:
                        try:
                            excluir_usuario(selected_usuario["id"])
                            st.success("Usuário ADMIN excluído com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir usuário: {e}")

    def render_form_coord_regional():
        usuarios = get_usuarios_por_perfil("COORDENADOR REGIONAL")
        with st.form("form_coord_regional"):
            nome = st.text_input("Nome", key="coord_regional_nome")
            login = st.text_input("Login", key="coord_regional_login")
            senha = st.text_input("Senha", type="password", key="coord_regional_senha")

            regiao_id = None
            if regioes_disponiveis:
                default_index = 0
                for index, regiao in enumerate(regioes_disponiveis):
                    if regiao.get("id") == usuario.get("regiao_id"):
                        default_index = index
                        break
                regiao_selecionada = st.selectbox(
                    "Região",
                    regioes_disponiveis,
                    index=default_index,
                    format_func=lambda item: item["nome"],
                    key="coord_regional_regiao"
                )
                regiao_id = regiao_selecionada["id"]
            else:
                st.warning("Cadastre pelo menos uma região acessível antes de criar usuários.")

            form_invalido = (
                not nome
                or not login
                or not senha
                or regiao_id is None
            )

            col_salvar, col_cancelar = st.columns(2)
            with col_salvar:
                salvar = st.form_submit_button("Salvar")
            with col_cancelar:
                cancelar = st.form_submit_button("Cancelar")

            if salvar:
                if form_invalido:
                    st.error("Preencha todos os campos obrigatórios para COORDENADOR REGIONAL.")
                else:
                    try:
                        inserir_usuario(
                            nome,
                            login,
                            senha,
                            "COORDENADOR REGIONAL",
                            None,
                            regiao_id,
                        )
                        st.success("Usuário COORDENADOR REGIONAL criado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao criar usuário: {e}")

            if cancelar:
                st.rerun()

        render_usuarios_tabela(usuarios, "COORDENADOR REGIONAL")

        if usuarios:
            selected_usuario = st.selectbox(
                "Selecionar COORDENADOR REGIONAL para editar/excluir",
                usuarios,
                format_func=format_usuario,
                key="coord_regional_select_usuario"
            )
            if selected_usuario:
                with st.form("form_edit_coord_regional"):
                    nome_edit = st.text_input(
                        "Nome",
                        value=selected_usuario["Nome"],
                        key=f"coord_regional_edit_nome_{selected_usuario['id']}"
                    )
                    login_edit = st.text_input(
                        "Login",
                        value=selected_usuario["Login"],
                        key=f"coord_regional_edit_login_{selected_usuario['id']}"
                    )
                    status_edit = st.text_input(
                        "Status",
                        value=selected_usuario.get("Status", ""),
                        key=f"coord_regional_edit_status_{selected_usuario['id']}"
                    )

                    col_update, col_delete = st.columns(2)
                    with col_update:
                        salvar_edit = st.form_submit_button("Salvar alterações")
                    with col_delete:
                        excluir = st.form_submit_button("Excluir")

                    if salvar_edit:
                        try:
                            editar_usuario(
                                selected_usuario["id"],
                                nome_edit,
                                login_edit,
                                "COORDENADOR REGIONAL",
                                status_edit,
                            )
                            st.success("Usuário COORDENADOR REGIONAL atualizado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar usuário: {e}")

                    if excluir:
                        try:
                            excluir_usuario(selected_usuario["id"])
                            st.success("Usuário COORDENADOR REGIONAL excluído com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir usuário: {e}")

    def render_form_coord_local():
        usuarios = get_usuarios_por_perfil("COORDENADOR LOCAL")
        
        # Inicializar session_state para seleções dinâmicas
        if "coord_local_regiao_selecionada" not in st.session_state:
            st.session_state.coord_local_regiao_selecionada = None
        if "coord_local_localidade_selecionada" not in st.session_state:
            st.session_state.coord_local_localidade_selecionada = None
            
        with st.form("form_coord_local"):
            nome = st.text_input("Nome", key="coord_local_nome")
            login = st.text_input("Login", key="coord_local_login")
            senha = st.text_input("Senha", type="password", key="coord_local_senha")

            regiao_id = None
            localidade_id = None
            if regioes_disponiveis:
                default_index = 0
                for index, regiao in enumerate(regioes_disponiveis):
                    if regiao.get("id") == usuario.get("regiao_id"):
                        default_index = index
                        break
                regiao_selecionada = st.selectbox(
                    "Região",
                    regioes_disponiveis,
                    index=default_index,
                    format_func=lambda item: item["nome"],
                    key="coord_local_regiao"
                )
                regiao_id = regiao_selecionada["id"] if regiao_selecionada else None
                
                # Atualizar session_state com a região selecionada
                st.session_state.coord_local_regiao_selecionada = regiao_id

                # Filtrar localidades baseado na região selecionada
                localidades_disponiveis = _localidades_acessiveis(usuario, [regiao_id] if regiao_id else None)
                if localidades_disponiveis:
                    localidade_selecionada = st.selectbox(
                        "Localidade",
                        localidades_disponiveis,
                        format_func=lambda item: item["nome"],
                        key="coord_local_localidade"
                    )
                    localidade_id = localidade_selecionada["id"] if localidade_selecionada else None
                    st.session_state.coord_local_localidade_selecionada = localidade_id
                else:
                    st.warning("Cadastre pelo menos uma localidade antes de criar usuários.")
            else:
                st.warning("Cadastre pelo menos uma região acessível antes de criar usuários.")

            form_invalido = (
                not nome
                or not login
                or not senha
                or regiao_id is None
                or localidade_id is None
            )

            col_salvar, col_cancelar = st.columns(2)
            with col_salvar:
                salvar = st.form_submit_button("Salvar")
            with col_cancelar:
                cancelar = st.form_submit_button("Cancelar")

            if salvar:
                if form_invalido:
                    st.error("Preencha todos os campos obrigatórios para COORDENADOR LOCAL.")
                else:
                    try:
                        inserir_usuario(
                            nome,
                            login,
                            senha,
                            "COORDENADOR LOCAL",
                            localidade_id,
                            regiao_id,
                        )
                        st.success("Usuário COORDENADOR LOCAL criado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao criar usuário: {e}")

            if cancelar:
                st.rerun()

        render_usuarios_tabela(usuarios, "COORDENADOR LOCAL")

        if usuarios:
            selected_usuario = st.selectbox(
                "Selecionar COORDENADOR LOCAL para editar/excluir",
                usuarios,
                format_func=format_usuario,
                key="coord_local_select_usuario"
            )
            if selected_usuario:
                with st.form("form_edit_coord_local"):
                    nome_edit = st.text_input(
                        "Nome",
                        value=selected_usuario["Nome"],
                        key=f"coord_local_edit_nome_{selected_usuario['id']}"
                    )
                    login_edit = st.text_input(
                        "Login",
                        value=selected_usuario["Login"],
                        key=f"coord_local_edit_login_{selected_usuario['id']}"
                    )
                    status_edit = st.text_input(
                        "Status",
                        value=selected_usuario.get("Status", ""),
                        key=f"coord_local_edit_status_{selected_usuario['id']}"
                    )

                    col_update, col_delete = st.columns(2)
                    with col_update:
                        salvar_edit = st.form_submit_button("Salvar alterações")
                    with col_delete:
                        excluir = st.form_submit_button("Excluir")

                    if salvar_edit:
                        try:
                            editar_usuario(
                                selected_usuario["id"],
                                nome_edit,
                                login_edit,
                                "COORDENADOR LOCAL",
                                status_edit,
                            )
                            st.success("Usuário COORDENADOR LOCAL atualizado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar usuário: {e}")

                    if excluir:
                        try:
                            excluir_usuario(selected_usuario["id"])
                            st.success("Usuário COORDENADOR LOCAL excluído com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir usuário: {e}")

    def render_form_professor():
        usuarios = get_usuarios_por_perfil("PROFESSOR")
        
        # Inicializar session_state para seleções dinâmicas
        if "prof_regiao_selecionada" not in st.session_state:
            st.session_state.prof_regiao_selecionada = None
        if "prof_localidade_selecionada" not in st.session_state:
            st.session_state.prof_localidade_selecionada = None
            
        with st.form("form_professor"):
            nome = st.text_input("Nome", key="professor_nome")
            login = st.text_input("Login", key="professor_login")
            senha = st.text_input("Senha", type="password", key="professor_senha")

            regiao_id = None
            localidade_id = None
            turmas_disponiveis = []

            if regioes_disponiveis:
                default_index = 0
                for index, regiao in enumerate(regioes_disponiveis):
                    if regiao.get("id") == usuario.get("regiao_id"):
                        default_index = index
                        break
                regiao_selecionada = st.selectbox(
                    "Região",
                    regioes_disponiveis,
                    index=default_index,
                    format_func=lambda item: item["nome"],
                    key="professor_regiao"
                )
                regiao_id = regiao_selecionada["id"] if regiao_selecionada else None
                
                # Atualizar session_state com a região selecionada
                st.session_state.prof_regiao_selecionada = regiao_id

                # Filtrar localidades baseado na região selecionada
                localidades_disponiveis = _localidades_acessiveis(usuario, [regiao_id] if regiao_id else None)
                if localidades_disponiveis:
                    localidade_selecionada = st.selectbox(
                        "Localidade",
                        localidades_disponiveis,
                        format_func=lambda item: item["nome"],
                        key="professor_localidade"
                    )
                    localidade_id = localidade_selecionada["id"] if localidade_selecionada else None
                    st.session_state.prof_localidade_selecionada = localidade_id
                else:
                    st.warning("Cadastre pelo menos uma localidade antes de criar usuários.")

                # Filtrar turmas baseado na região e localidade selecionadas
                turmas_disponiveis = _turmas_acessiveis(usuario, [regiao_id] if regiao_id else None, [localidade_id] if localidade_id else None)
                if turmas_disponiveis:
                    turmas_opcoes = [None] + turmas_disponiveis
                    turma_selecionada = st.selectbox(
                        "Turma (opcional)",
                        turmas_opcoes,
                        format_func=lambda item: "Nenhuma" if item is None else item["Nome"],
                        key="professor_turma"
                    )
                    turma_id = turma_selecionada["id"] if turma_selecionada else None
                else:
                    st.info("Nenhuma turma disponível para as regiões/localidades selecionadas.")
                    turma_id = None
            else:
                st.warning("Cadastre pelo menos uma região acessível antes de criar usuários.")
                turma_id = None

            form_invalido = (
                not nome
                or not login
                or not senha
                or regiao_id is None
                or localidade_id is None
            )

            col_salvar, col_cancelar = st.columns(2)
            with col_salvar:
                salvar = st.form_submit_button("Salvar")
            with col_cancelar:
                cancelar = st.form_submit_button("Cancelar")

            if salvar:
                if form_invalido:
                    st.error("Preencha todos os campos obrigatórios para PROFESSOR.")
                else:
                    try:
                        usuario_criado = inserir_usuario(
                            nome,
                            login,
                            senha,
                            "PROFESSOR",
                            localidade_id,
                            regiao_id,
                        )
                        if usuario_criado:
                            usuario_novo_id = usuario_criado[0]["id"] if isinstance(usuario_criado, list) and usuario_criado else None
                            if turma_id and usuario_novo_id:
                                turma_atual = next((turma for turma in turmas_disponiveis if turma["id"] == turma_id), None)
                                if turma_atual:
                                    editar_turma(
                                        turma_id,
                                        turma_atual["Nome"],
                                        turma_atual["regiao_id"],
                                        turma_atual["localidade_id"],
                                        usuario_novo_id,
                                        turma_atual.get("auxiliar_id")
                                    )
                        st.success("Usuário PROFESSOR criado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao criar usuário: {e}")

            if cancelar:
                st.rerun()

        render_usuarios_tabela(usuarios, "PROFESSOR")

        if usuarios:
            selected_usuario = st.selectbox(
                "Selecionar PROFESSOR para editar/excluir",
                usuarios,
                format_func=format_usuario,
                key="professor_select_usuario"
            )
            if selected_usuario:
                turma_atual = _turma_atual_por_campo(selected_usuario["id"], "professor_id")
                turmas_disponiveis = _turmas_acessiveis(usuario)
                turmas_opcoes = [None] + turmas_disponiveis
                default_index = 0
                if turma_atual:
                    for index, turma in enumerate(turmas_opcoes):
                        if turma and turma.get("id") == turma_atual.get("id"):
                            default_index = index
                            break

                with st.form("form_edit_professor"):
                    nome_edit = st.text_input(
                        "Nome",
                        value=selected_usuario["Nome"],
                        key=f"professor_edit_nome_{selected_usuario['id']}"
                    )
                    login_edit = st.text_input(
                        "Login",
                        value=selected_usuario["Login"],
                        key=f"professor_edit_login_{selected_usuario['id']}"
                    )
                    status_edit = st.text_input(
                        "Status",
                        value=selected_usuario.get("Status", ""),
                        key=f"professor_edit_status_{selected_usuario['id']}"
                    )
                    turma_selecionada_edit = st.selectbox(
                        "Turma (opcional)",
                        turmas_opcoes,
                        index=default_index,
                        format_func=lambda item: "Nenhuma" if item is None else item["Nome"],
                        key=f"professor_edit_turma_{selected_usuario['id']}"
                    )
                    nova_turma_id = turma_selecionada_edit["id"] if turma_selecionada_edit else None

                    col_update, col_delete = st.columns(2)
                    with col_update:
                        salvar_edit = st.form_submit_button("Salvar alterações")
                    with col_delete:
                        excluir = st.form_submit_button("Excluir")

                    if salvar_edit:
                        try:
                            editar_usuario(
                                selected_usuario["id"],
                                nome_edit,
                                login_edit,
                                "PROFESSOR",
                                status_edit,
                            )
                            if nova_turma_id != (turma_atual.get("id") if turma_atual else None):
                                if turma_atual:
                                    desvincular_professor(selected_usuario["id"])
                                if nova_turma_id:
                                    turma_destino = next((turma for turma in turmas_disponiveis if turma["id"] == nova_turma_id), None)
                                    if turma_destino:
                                        editar_turma(
                                            nova_turma_id,
                                            turma_destino["Nome"],
                                            turma_destino["regiao_id"],
                                            turma_destino["localidade_id"],
                                            selected_usuario["id"],
                                            turma_destino.get("auxiliar_id")
                                        )
                            st.success("Usuário PROFESSOR atualizado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar usuário: {e}")

                    if excluir:
                        try:
                            desvincular_professor(selected_usuario["id"])
                            excluir_usuario(selected_usuario["id"])
                            st.success("Usuário PROFESSOR excluído com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir usuário: {e}")

    def render_form_auxiliar():
        usuarios = get_usuarios_por_perfil("AUXILIAR")
        
        # Inicializar session_state para seleções dinâmicas
        if "aux_regiao_selecionada" not in st.session_state:
            st.session_state.aux_regiao_selecionada = None
        if "aux_localidade_selecionada" not in st.session_state:
            st.session_state.aux_localidade_selecionada = None
            
        with st.form("form_auxiliar"):
            nome = st.text_input("Nome", key="auxiliar_nome")
            login = st.text_input("Login", key="auxiliar_login")
            senha = st.text_input("Senha", type="password", key="auxiliar_senha")

            regiao_id = None
            localidade_id = None
            turmas_disponiveis = []

            if regioes_disponiveis:
                default_index = 0
                for index, regiao in enumerate(regioes_disponiveis):
                    if regiao.get("id") == usuario.get("regiao_id"):
                        default_index = index
                        break
                regiao_selecionada = st.selectbox(
                    "Região",
                    regioes_disponiveis,
                    index=default_index,
                    format_func=lambda item: item["nome"],
                    key="auxiliar_regiao"
                )
                regiao_id = regiao_selecionada["id"] if regiao_selecionada else None
                
                # Atualizar session_state com a região selecionada
                st.session_state.aux_regiao_selecionada = regiao_id

                # Filtrar localidades baseado na região selecionada
                localidades_disponiveis = _localidades_acessiveis(usuario, [regiao_id] if regiao_id else None)
                if localidades_disponiveis:
                    localidade_selecionada = st.selectbox(
                        "Localidade",
                        localidades_disponiveis,
                        format_func=lambda item: item["nome"],
                        key="auxiliar_localidade"
                    )
                    localidade_id = localidade_selecionada["id"] if localidade_selecionada else None
                    st.session_state.aux_localidade_selecionada = localidade_id
                else:
                    st.warning("Cadastre pelo menos uma localidade antes de criar usuários.")

                # Filtrar turmas baseado na região e localidade selecionadas
                turmas_disponiveis = _turmas_acessiveis(usuario, [regiao_id] if regiao_id else None, [localidade_id] if localidade_id else None)
                if turmas_disponiveis:
                    turmas_opcoes = [None] + turmas_disponiveis
                    turma_selecionada = st.selectbox(
                        "Turma (opcional)",
                        turmas_opcoes,
                        format_func=lambda item: "Nenhuma" if item is None else item["Nome"],
                        key="auxiliar_turma"
                    )
                    turma_id = turma_selecionada["id"] if turma_selecionada else None
                else:
                    st.info("Nenhuma turma disponível para as regiões/localidades selecionadas.")
                    turma_id = None
            else:
                st.warning("Cadastre pelo menos uma região acessível antes de criar usuários.")
                turma_id = None

            form_invalido = (
                not nome
                or not login
                or not senha
                or regiao_id is None
                or localidade_id is None
            )

            col_salvar, col_cancelar = st.columns(2)
            with col_salvar:
                salvar = st.form_submit_button("Salvar")
            with col_cancelar:
                cancelar = st.form_submit_button("Cancelar")

            if salvar:
                if form_invalido:
                    st.error("Preencha todos os campos obrigatórios para AUXILIAR.")
                else:
                    try:
                        usuario_criado = inserir_usuario(
                            nome,
                            login,
                            senha,
                            "AUXILIAR",
                            localidade_id,
                            regiao_id,
                        )
                        if usuario_criado:
                            usuario_novo_id = usuario_criado[0]["id"] if isinstance(usuario_criado, list) and usuario_criado else None
                            if turma_id and usuario_novo_id:
                                turma_atual = next((turma for turma in turmas_disponiveis if turma["id"] == turma_id), None)
                                if turma_atual:
                                    editar_turma(
                                        turma_id,
                                        turma_atual["Nome"],
                                        turma_atual["regiao_id"],
                                        turma_atual["localidade_id"],
                                        turma_atual.get("professor_id"),
                                        usuario_novo_id
                                    )
                        st.success("Usuário AUXILIAR criado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao criar usuário: {e}")

            if cancelar:
                st.rerun()

        render_usuarios_tabela(usuarios, "AUXILIAR")

        if usuarios:
            selected_usuario = st.selectbox(
                "Selecionar AUXILIAR para editar/excluir",
                usuarios,
                format_func=format_usuario,
                key="auxiliar_select_usuario"
            )
            if selected_usuario:
                turma_atual = _turma_atual_por_campo(selected_usuario["id"], "auxiliar_id")
                turmas_disponiveis = _turmas_acessiveis(usuario)
                turmas_opcoes = [None] + turmas_disponiveis
                default_index = 0
                if turma_atual:
                    for index, turma in enumerate(turmas_opcoes):
                        if turma and turma.get("id") == turma_atual.get("id"):
                            default_index = index
                            break

                with st.form("form_edit_auxiliar"):
                    nome_edit = st.text_input(
                        "Nome",
                        value=selected_usuario["Nome"],
                        key=f"auxiliar_edit_nome_{selected_usuario['id']}"
                    )
                    login_edit = st.text_input(
                        "Login",
                        value=selected_usuario["Login"],
                        key=f"auxiliar_edit_login_{selected_usuario['id']}"
                    )
                    status_edit = st.text_input(
                        "Status",
                        value=selected_usuario.get("Status", ""),
                        key=f"auxiliar_edit_status_{selected_usuario['id']}"
                    )
                    turma_selecionada_edit = st.selectbox(
                        "Turma (opcional)",
                        turmas_opcoes,
                        index=default_index,
                        format_func=lambda item: "Nenhuma" if item is None else item["Nome"],
                        key=f"auxiliar_edit_turma_{selected_usuario['id']}"
                    )
                    nova_turma_id = turma_selecionada_edit["id"] if turma_selecionada_edit else None

                    col_update, col_delete = st.columns(2)
                    with col_update:
                        salvar_edit = st.form_submit_button("Salvar alterações")
                    with col_delete:
                        excluir = st.form_submit_button("Excluir")

                    if salvar_edit:
                        try:
                            editar_usuario(
                                selected_usuario["id"],
                                nome_edit,
                                login_edit,
                                "AUXILIAR",
                                status_edit,
                            )
                            if nova_turma_id != (turma_atual.get("id") if turma_atual else None):
                                if turma_atual:
                                    desvincular_auxiliar(selected_usuario["id"])
                                if nova_turma_id:
                                    turma_destino = next((turma for turma in turmas_disponiveis if turma["id"] == nova_turma_id), None)
                                    if turma_destino:
                                        editar_turma(
                                            nova_turma_id,
                                            turma_destino["Nome"],
                                            turma_destino["regiao_id"],
                                            turma_destino["localidade_id"],
                                            turma_destino.get("professor_id"),
                                            selected_usuario["id"]
                                        )
                            st.success("Usuário AUXILIAR atualizado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar usuário: {e}")

                    if excluir:
                        try:
                            desvincular_auxiliar(selected_usuario["id"])
                            excluir_usuario(selected_usuario["id"])
                            st.success("Usuário AUXILIAR excluído com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir usuário: {e}")

    def render_form_aluno():
        usuarios = get_usuarios_por_perfil("ALUNO")
        
        # Inicializar session_state para seleções dinâmicas
        if "aluno_regiao_selecionada" not in st.session_state:
            st.session_state.aluno_regiao_selecionada = None
        if "aluno_localidade_selecionada" not in st.session_state:
            st.session_state.aluno_localidade_selecionada = None
            
        with st.form("form_aluno"):
            nome = st.text_input("Nome", key="aluno_nome")
            login = st.text_input("Login", key="aluno_login")
            senha = st.text_input("Senha", type="password", key="aluno_senha")

            regiao_id = None
            localidade_id = None
            turmas_ids = []
            turmas_disponiveis = []

            if regioes_disponiveis:
                default_index = 0
                for index, regiao in enumerate(regioes_disponiveis):
                    if regiao.get("id") == usuario.get("regiao_id"):
                        default_index = index
                        break
                regiao_selecionada = st.selectbox(
                    "Região",
                    regioes_disponiveis,
                    index=default_index,
                    format_func=lambda item: item["nome"],
                    key="aluno_regiao"
                )
                regiao_id = regiao_selecionada["id"] if regiao_selecionada else None
                
                # Atualizar session_state com a região selecionada
                st.session_state.aluno_regiao_selecionada = regiao_id

                # Filtrar localidades baseado na região selecionada
                localidades_disponiveis = _localidades_acessiveis(usuario, [regiao_id] if regiao_id else None)
                if localidades_disponiveis:
                    localidade_selecionada = st.selectbox(
                        "Localidade",
                        localidades_disponiveis,
                        format_func=lambda item: item["nome"],
                        key="aluno_localidade"
                    )
                    localidade_id = localidade_selecionada["id"] if localidade_selecionada else None
                    st.session_state.aluno_localidade_selecionada = localidade_id
                else:
                    st.warning("Cadastre pelo menos uma localidade antes de criar usuários.")

                # Filtrar turmas baseado na região e localidade selecionadas
                turmas_disponiveis = _turmas_acessiveis(usuario, [regiao_id] if regiao_id else None, [localidade_id] if localidade_id else None)
                if turmas_disponiveis:
                    turma_selecionada = st.selectbox(
                        "Turma",
                        turmas_disponiveis,
                        format_func=lambda item: item["Nome"],
                        key="aluno_turma"
                    )
                    turmas_ids = [turma_selecionada["id"]] if turma_selecionada else []
                else:
                    st.info("Nenhuma turma disponível para as regiões/localidades selecionadas.")
            else:
                st.warning("Cadastre pelo menos uma região acessível antes de criar usuários.")

            data_nascimento = st.date_input("Data de nascimento", key="aluno_data_nascimento")
            responsavel = st.text_input("Responsável", key="aluno_responsavel")
            telefone_responsavel = st.text_input("Telefone responsável", key="aluno_telefone_responsavel")
            data_matricula = st.date_input("Data matrícula", key="aluno_data_matricula")

            form_invalido = (
                not nome
                or not login
                or not senha
                or regiao_id is None
                or localidade_id is None
                or len(turmas_ids) == 0
            )

            col_salvar, col_cancelar = st.columns(2)
            with col_salvar:
                salvar = st.form_submit_button("Salvar")
            with col_cancelar:
                cancelar = st.form_submit_button("Cancelar")

            if salvar:
                if form_invalido:
                    st.error("Preencha todos os campos obrigatórios para ALUNO.")
                else:
                    try:
                        responsavel_value = responsavel if responsavel else None
                        telefone_responsavel_value = telefone_responsavel if telefone_responsavel else None
                        data_nascimento_value = str(data_nascimento) if data_nascimento else None
                        data_matricula_value = str(data_matricula) if data_matricula else None

                        inserir_usuario(
                            nome,
                            login,
                            senha,
                            "ALUNO",
                            localidade_id,
                            regiao_id,
                            responsavel=responsavel_value,
                            telefone_responsavel=telefone_responsavel_value,
                            data_nascimento=data_nascimento_value,
                            data_matricula=data_matricula_value,
                        )
                        st.success("Usuário ALUNO criado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao criar usuário: {e}")

            if cancelar:
                st.rerun()

        render_usuarios_tabela(usuarios, "ALUNO")

        if usuarios:
            selected_usuario = st.selectbox(
                "Selecionar ALUNO para editar/excluir",
                usuarios,
                format_func=format_usuario,
                key="aluno_select_usuario"
            )
            if selected_usuario:
                with st.form("form_edit_aluno"):
                    nome_edit = st.text_input(
                        "Nome",
                        value=selected_usuario["Nome"],
                        key=f"aluno_edit_nome_{selected_usuario['id']}"
                    )
                    login_edit = st.text_input(
                        "Login",
                        value=selected_usuario["Login"],
                        key=f"aluno_edit_login_{selected_usuario['id']}"
                    )
                    status_edit = st.text_input(
                        "Status",
                        value=selected_usuario.get("Status", ""),
                        key=f"aluno_edit_status_{selected_usuario['id']}"
                    )

                    col_update, col_delete = st.columns(2)
                    with col_update:
                        salvar_edit = st.form_submit_button("Salvar alterações")
                    with col_delete:
                        excluir = st.form_submit_button("Excluir")

                    if salvar_edit:
                        try:
                            editar_usuario(
                                selected_usuario["id"],
                                nome_edit,
                                login_edit,
                                "ALUNO",
                                status_edit,
                            )
                            st.success("Usuário ALUNO atualizado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar usuário: {e}")

                    if excluir:
                        try:
                            excluir_usuario(selected_usuario["id"])
                            st.success("Usuário ALUNO excluído com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir usuário: {e}")

    aba_admin, aba_coord_regional, aba_coord_local, aba_professor, aba_auxiliar, aba_aluno = st.tabs([
        "ADMIN",
        "COORD REG",
        "COORD LOCAL",
        "PROFESSOR",
        "AUXILIAR",
        "ALUNO",
    ])

    with aba_admin:
        render_form_admin()

    with aba_coord_regional:
        render_form_coord_regional()

    with aba_coord_local:
        render_form_coord_local()

    with aba_professor:
        render_form_professor()

    with aba_auxiliar:
        render_form_auxiliar()

    with aba_aluno:
        render_form_aluno()

with aba2:

    st.title("🌏 Regiões")

    col1, col2 = st.columns([1, 5])

    with col1:
        if _is_admin(perfil_logado) and st.button("➕ Nova região"):
            st.session_state.nova_região = True

    st.divider()

    if not _is_admin(perfil_logado):
        st.info("Seu acesso está restrito à região vinculada ao seu usuário.")

    if st.session_state.get("nova_região", False):

        with st.form("form_nova_região"):

            nome = st.text_input("Nome")
            uf = st.text_input("UF")

            

            col_salvar, col_cancelar = st.columns(2)

            with col_salvar:
                salvar = st.form_submit_button("Salvar")

            with col_cancelar:
                cancelar = st.form_submit_button("Cancelar")

            if salvar:
                try:
                    inserir_regiao(
                        nome, uf)

                    st.success("Região criada com sucesso!")

                    st.session_state.nova_região = False

                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar região: {e}")

            if cancelar:

                st.session_state.nova_região = False

                st.rerun()

    regioes = _regioes_acessiveis(usuario)

    if regioes:

        df = pd.DataFrame(regioes)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("Nenhuma região cadastrada.")

with aba3:

    st.title("📍 Localidade")

    col1, col2 = st.columns([1, 5])

    with col1:
        if st.button("➕ Nova localidade"):
            st.session_state.nova_localidade = True

    st.divider()

    if st.session_state.get("nova_localidade", False):

        with st.form("form_nova_localidade"):

            nome = st.text_input("Nome")
            regioes_disponiveis = _regioes_acessiveis(usuario)

            if not regioes_disponiveis:
                st.warning("Cadastre pelo menos uma região antes de criar uma localidade.")
                st.stop()

            regiao_selecionada = st.multiselect(
                "Regiões",
                regioes_disponiveis,
                default=[regioes_disponiveis[0]],
                max_selections=1,
                format_func=lambda x: x["nome"]
            )
            regiao_id = regiao_selecionada[0]["id"] if regiao_selecionada else regioes_disponiveis[0]["id"]

            col_salvar, col_cancelar = st.columns(2)

            with col_salvar:
                salvar = st.form_submit_button("Salvar")

            with col_cancelar:
                cancelar = st.form_submit_button("Cancelar")

            if salvar:
                try:
                    inserir_localidade(
                        nome, regiao_id)

                    st.success("Localidade criada com sucesso!")

                    st.session_state.nova_localidade = False

                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar localidade: {e}")

            if cancelar:

                st.session_state.nova_localidade = False

                st.rerun()

    localidades = _localidades_acessiveis(usuario)

    if localidades:

        df = pd.DataFrame(localidades)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("Nenhuma localidade cadastrada.")

with aba4:

    st.title("👨🏻‍🎓👨🏽‍🎓👨🏿‍🎓TURMA")

    col1, col2 = st.columns([1, 5])

    with col1:
        if st.button("➕ Nova turma"):
            st.session_state.nova_turma = True

    st.divider()

    if st.session_state.get("nova_turma", False):

        with st.form("form_nova_turma"):

            nome = st.text_input("Nome")
            regioes_disponiveis = _regioes_acessiveis(usuario)

            if not regioes_disponiveis:
                st.warning("Cadastre pelo menos uma região antes de criar uma turma.")

            regiao_selecionada = None
            if regioes_disponiveis:
                regiao_selecionada = st.selectbox(
                    "Região",
                    regioes_disponiveis,
                    format_func=lambda x: x["nome"],
                    key="nova_turma_regiao"
                )
            regiao_id = regiao_selecionada["id"] if regiao_selecionada else None

            # Cascata: Localidades filtradas pela Região selecionada
            localidades_disponiveis = _localidades_acessiveis(usuario, [regiao_id] if regiao_id else None)
            if not localidades_disponiveis:
                st.warning("Cadastre pelo menos uma localidade antes de criar uma turma.")

            localidade_selecionada = None
            if localidades_disponiveis:
                localidade_selecionada = st.selectbox(
                    "Localidade",
                    localidades_disponiveis,
                    format_func=lambda x: x["nome"],
                    key="nova_turma_localidade"
                )
            localidade_id = localidade_selecionada["id"] if localidade_selecionada else None

            # Cascata: Professores filtrados pela Localidade selecionada
            professor = [
                item for item in _professores_acessiveis(usuario)
                if item.get("localidade_id") == localidade_id
            ]

            # Cascata: Auxiliares filtrados pela Localidade selecionada
            auxiliar = [
                item for item in _auxiliares_acessiveis(usuario)
                if item.get("localidade_id") == localidade_id
            ]

            professor_opcoes = [None] + professor
            professor_selecionado = st.selectbox(
                "Professor (opcional)",
                professor_opcoes,
                format_func=lambda x: "Nenhum" if x is None else x.get("nome", "N/A"),
                key="nova_turma_professor"
            )
            professor_id = professor_selecionado["id"] if professor_selecionado else None

            auxiliar_opcoes = [None] + auxiliar
            auxiliar_selecionado = st.selectbox(
                "Auxiliar (opcional)",
                auxiliar_opcoes,
                format_func=lambda x: "Nenhum" if x is None else x.get("nome", "N/A"),
                key="nova_turma_auxiliar"
            )
            auxiliar_id = auxiliar_selecionado["id"] if auxiliar_selecionado else None

            col_salvar, col_cancelar = st.columns(2)

            with col_salvar:
                salvar = st.form_submit_button(
                    "Salvar",
                )

            with col_cancelar:
                cancelar = st.form_submit_button("Cancelar")

            if salvar:
                if not nome:
                    st.error("Informe o nome da turma.")
                    st.stop()

                if regiao_id is None:
                    st.error("Selecione uma região.")
                    st.stop()

                if localidade_id is None:
                    st.error("Selecione uma localidade.")
                    st.stop()

                dados = {
                    "nome": nome,
                    "regiao_id": regiao_id,
                    "localidade_id": localidade_id,
                    "professor_id": professor_id,
                    "auxiliar_id": auxiliar_id,
                }

                try:
                    inserir_turma(**dados)

                    st.success("Turma criada com sucesso!")

                    st.session_state.nova_turma = False

                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar turma: {e}")

            if cancelar:

                st.session_state.nova_turma = False

                st.rerun()

    turmas = _turmas_acessiveis(usuario)

    if turmas:

        df = pd.DataFrame(turmas)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("Nenhuma turma cadastrada.")