from config import supabase
import hashlib
import streamlit as st


def gerar_hash(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def validar_login(login, senha):
    try:
        senha_hash = gerar_hash(senha)

        resposta = (
            supabase
            .table("usuarios")
            .select("*")
            .eq("login", login)
            .eq("senha_hash", senha_hash)
            .execute()
        )

        if resposta.data:
            return resposta.data[0]

        return None
    except Exception as e:
        st.error(f"Erro ao validar login: {e}")
        return None


def listar_usuarios():
    try:
        resposta = (
            supabase
            .table("usuarios")
            .select("""
                id,
                nome,
                login,
                perfil,
                status,
                regioes(nome),
                localidades(nome),
                regiao_id,
                localidade_id,
                responsavel,
                telefone_responsavel,
                data_nascimento,
                data_matricula
            """)
            .order("nome")
            .execute()
        )

        usuarios = []

        for u in resposta.data:
            usuarios.append({
                "id": u["id"],
                "Nome": u["nome"],
                "Login": u["login"],
                "Perfil": u["perfil"],
                "Status": u.get("status", ""),
                "Região": u["regioes"]["nome"] if u["regioes"] else "",
                "Localidade": u["localidades"]["nome"] if u["localidades"] else "",
                "regiao_id": u.get("regiao_id"),
                "localidade_id": u.get("localidade_id"),
                "responsavel": u.get("responsavel", ""),
                "telefone_responsavel": u.get("telefone_responsavel", ""),
                "data_nascimento": u.get("data_nascimento", ""),
                "data_matricula": u.get("data_matricula", "")
            })

        return usuarios
    except Exception as e:
        st.error(f"Erro ao listar usuários: {e}")
        return []


def listar_usuarios_com_isolamento(usuario_logado):
    """Lista usuários aplicando isolamento conforme o perfil do usuário logado."""
    try:
        todos_usuarios = listar_usuarios()
        perfil = usuario_logado.get("perfil", "—")
        regiao_id = usuario_logado.get("regiao_id")
        localidade_id = usuario_logado.get("localidade_id")
        usuario_id = usuario_logado.get("id")

        if perfil in ["ADMIN", "TI"]:
            return todos_usuarios

        if perfil == "COORDENADOR REGIONAL":
            return [u for u in todos_usuarios if u.get("regiao_id") == regiao_id]

        if perfil == "COORDENADOR LOCAL":
            return [u for u in todos_usuarios if u.get("localidade_id") == localidade_id]

        if perfil == "PROFESSOR":
            # Professor vê apenas usuários de sua localidade
            return [u for u in todos_usuarios if u.get("localidade_id") == localidade_id]

        if perfil == "AUXILIAR":
            # Auxiliar vê apenas usuários de sua localidade
            return [u for u in todos_usuarios if u.get("localidade_id") == localidade_id]

        if perfil == "ALUNO":
            # Aluno vê apenas a si próprio
            return [u for u in todos_usuarios if u.get("id") == usuario_id]

        return todos_usuarios
    except Exception as e:
        st.error(f"Erro ao listar usuários com isolamento: {e}")
        return []



def inserir_usuario(
    nome,
    login,
    senha,
    perfil,
    localidade_id,
    regiao_id,
    responsavel=None,
    telefone_responsavel=None,
    data_nascimento=None,
    data_matricula=None,
):
    try:
        senha_hash = gerar_hash(senha)

        payload = {
            "nome": nome,
            "login": login,
            "senha_hash": senha_hash,
            "perfil": perfil,
            "localidade_id": localidade_id,
            "regiao_id": regiao_id,
        }

        if responsavel is not None:
            payload["responsavel"] = responsavel
        if telefone_responsavel is not None:
            payload["telefone_responsavel"] = telefone_responsavel
        if data_nascimento is not None:
            payload["data_nascimento"] = data_nascimento
        if data_matricula is not None:
            payload["data_matricula"] = data_matricula

        resposta = (
            supabase
            .table("usuarios")
            .insert(payload)
            .execute()
        )

        return resposta.data
    except Exception as e:
        st.error(f"Erro ao inserir usuário: {e}")
        return None


def editar_usuario(id, nome, login, perfil, status):
    try:
        resposta = (
            supabase
            .table("usuarios")
            .update({
                "nome": nome,
                "login": login,
                "perfil": perfil,
                "status": status
            })
            .eq("id", id)
            .execute()
        )

        return resposta.data
    except Exception as e:
        st.error(f"Erro ao editar usuário: {e}")
        return None


def excluir_usuario(id):
    try:
        resposta = (
            supabase
            .table("usuarios")
            .delete()
            .eq("id", id)
            .execute()
        )

        return resposta.data
    except Exception as e:
        st.error(f"Erro ao excluir usuário: {e}")
        return None


def listar_professores():
    try:
        resposta = (
            supabase
            .table("usuarios")
            .select("*")
            .eq("perfil", "PROFESSOR")
            .order("nome")
            .execute()
        )

        return resposta.data
    except Exception as e:
        st.error(f"Erro ao listar professores: {e}")
        return []


def listar_auxiliares():
    try:
        resposta = (
            supabase
            .table("usuarios")
            .select("*")
            .eq("perfil", "AUXILIAR")
            .order("nome")
            .execute()
        )

        return resposta.data
    except Exception as e:
        st.error(f"Erro ao listar auxiliares: {e}")
        return []