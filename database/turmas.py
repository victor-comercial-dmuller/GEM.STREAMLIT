from config import supabase
import hashlib


def listar_turmas():
    resposta = (
        supabase
        .table("turmas")
        .select("""
            id,
            nome,
            regiao_id,
            localidade_id,
            professor_id,
            auxiliar_id,
            regioes(nome),
            localidades(nome),
            professor:usuarios!professor_id(nome),
            auxiliar:usuarios!auxiliar_id(nome)
        """)
        .order("nome")
        .execute()
    )

    turmas = []

    for t in resposta.data:
        turmas.append({
            "id": t["id"],
            "Nome": t["nome"],
            "Região": t["regioes"]["nome"] if t["regioes"] else "",
            "Localidade": t["localidades"]["nome"] if t["localidades"] else "",
            "Professor": t["professor"]["nome"] if t["professor"] else "",
            "Auxiliar": t["auxiliar"]["nome"] if t["auxiliar"] else "",
            "regiao_id": t.get("regiao_id"),
            "localidade_id": t.get("localidade_id"),
            "professor_id": t.get("professor_id"),
            "auxiliar_id": t.get("auxiliar_id")
        })

    return turmas


def listar_turmas_com_isolamento(usuario_logado):
    """Lista turmas aplicando isolamento conforme o perfil do usuário logado."""
    perfil = usuario_logado.get("perfil", "—")
    regiao_id = usuario_logado.get("regiao_id")
    localidade_id = usuario_logado.get("localidade_id")
    usuario_id = usuario_logado.get("id")
    
    todas_turmas = listar_turmas()

    if perfil in ["ADMIN", "TI"]:
        return todas_turmas

    if perfil == "COORDENADOR REGIONAL":
        return [t for t in todas_turmas if t.get("regiao_id") == regiao_id]

    if perfil == "COORDENADOR LOCAL":
        return [t for t in todas_turmas if t.get("localidade_id") == localidade_id]

    if perfil == "PROFESSOR":
        # Professor vê apenas as turmas em que é professor
        return [t for t in todas_turmas if t.get("professor_id") == usuario_id]

    if perfil == "AUXILIAR":
        # Auxiliar vê apenas as turmas em que é auxiliar
        return [t for t in todas_turmas if t.get("auxiliar_id") == usuario_id]

    if perfil == "ALUNO":
        # Aluno vê apenas as turmas em que participa (será filtrado por alunos_aula)
        return [t for t in todas_turmas if t.get("localidade_id") == localidade_id]

    return todas_turmas


def inserir_turma(nome, localidade_id, regiao_id, professor_id, auxiliar_id):

    resposta = (
        supabase
        .table("turmas")
        .insert({
            "nome": nome,
            "localidade_id": localidade_id,
            "regiao_id": regiao_id,
            "professor_id": professor_id,
            "auxiliar_id": auxiliar_id
        })
        .execute()
    )

    return resposta.data


def desvincular_professor(usuario_id):
    resposta = (
        supabase
        .table("turmas")
        .update({"professor_id": None})
        .eq("professor_id", usuario_id)
        .execute()
    )

    return resposta.data


def desvincular_auxiliar(usuario_id):
    resposta = (
        supabase
        .table("turmas")
        .update({"auxiliar_id": None})
        .eq("auxiliar_id", usuario_id)
        .execute()
    )

    return resposta.data


def editar_turma(id, nome, regiao_id, localidade_id, professor_id, auxiliar_id):

    resposta = (
        supabase
        .table("turmas")
        .update({
            "nome": nome,
            "regiao_id": regiao_id,
            "localidade_id": localidade_id,
            "professor_id": professor_id,
            "auxiliar_id": auxiliar_id
        })
        .eq("id", id)
        .execute()
    )

    return resposta.data


def excluir_turma(id):

    resposta = (
        supabase
        .table("turmas")
        .delete()
        .eq("id", id)
        .execute()
    )

    return resposta.data