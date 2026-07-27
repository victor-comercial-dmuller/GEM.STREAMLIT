from config import supabase
import hashlib


def listar_regioes():
    resposta = (
        supabase
        .table("regioes")
        .select(""" 
            id,
            nome,
            uf""")
        .order("nome")
        .execute()
    )

    return resposta.data


def inserir_regiao(nome, uf):

    resposta = (
        supabase
        .table("regioes")
        .insert({
            "nome": nome,
            "uf": uf
        })
        .execute()
    )

    return resposta.data


def editar_regiao(id, nome, uf):

    resposta = (
        supabase
        .table("regioes")
        .update({
            "nome": nome,
            "uf": uf
        })
        .eq("id", id)
        .execute()
    )

    return resposta.data


def excluir_regiao(id):

    resposta = (
        supabase
        .table("regioes")
        .delete()
        .eq("id", id)
        .execute()
    )

    return resposta.data