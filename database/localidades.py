from config import supabase
import hashlib


def listar_localidades():

    resposta = (
        supabase
        .table("localidades")
        .select("""
            id,
            nome,
            regiao_id,
            regioes(nome)
        """)
        .order("nome")
        .execute()
    )

    localidades = []

    for item in resposta.data:
        localidades.append({
            "id": item["id"],
            "nome": item["nome"],
            "regiao": item["regioes"]["nome"] if item["regioes"] else "",
            "regiao_id": item.get("regiao_id")
        })

    return localidades


def inserir_localidade(nome, regiao_id):

    resposta = (
        supabase
        .table("localidades")
        .insert({
            "nome": nome,
            "regiao_id": regiao_id
        })
        .execute()
    )

    return resposta.data


def editar_localidade(id, nome, regiao_id):

    resposta = (
        supabase
        .table("localidades")
        .update({
            "nome": nome,
            "regiao_id": regiao_id
        })
        .eq("id", id)
        .execute()
    )

    return resposta.data


def excluir_localidade(id):

    resposta = (
        supabase
        .table("localidades")
        .delete()
        .eq("id", id)
        .execute()
    )

    return resposta.data