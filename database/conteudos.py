from config import supabase
import streamlit as st


def listar_conteudos():
    """Lista todos os conteúdos cadastrados."""
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

        conteudos = []
        for c in resposta.data:
            conteudos.append({
                "id": c["id"],
                "Categoria": c.get("categoria", ""),
                "Título": c.get("titulo", ""),
                "Descrição": c.get("descricao", ""),
                "Ativo": c.get("ativo", True),
                "Lição Inicial": c.get("licao_inicial", ""),
                "Lição Final": c.get("licao_final", ""),
                "Criado em": c.get("created_at", ""),
                "Atualizado em": c.get("updated_at", ""),
            })

        return conteudos
    except Exception as e:
        st.error(f"Erro ao listar conteúdos: {e}")
        return []


def inserir_conteudo(categoria, titulo, licao_inicial, licao_final, descricao=None):
    """Insere um novo conteúdo na tabela conteudos."""
    try:
        payload = {
            "categoria": categoria,
            "titulo": titulo,
            "licao_inicial": licao_inicial,
            "licao_final": licao_final,
            "ativo": True,
        }

        if descricao and descricao.strip():
            payload["descricao"] = descricao

        resposta = (
            supabase
            .table("conteudos")
            .insert(payload)
            .execute()
        )

        return resposta.data
    except Exception as e:
        st.error(f"Erro ao inserir conteúdo: {e}")
        return None


def editar_conteudo(id, categoria, titulo, licao_inicial, licao_final, descricao=None, ativo=True):
    """Edita um conteúdo existente."""
    try:
        payload = {
            "categoria": categoria,
            "titulo": titulo,
            "licao_inicial": licao_inicial,
            "licao_final": licao_final,
            "ativo": ativo,
        }

        if descricao is not None:
            payload["descricao"] = descricao if descricao.strip() else None

        resposta = (
            supabase
            .table("conteudos")
            .update(payload)
            .eq("id", id)
            .execute()
        )

        return resposta.data
    except Exception as e:
        st.error(f"Erro ao editar conteúdo: {e}")
        return None


def excluir_conteudo(id):
    """Marca um conteúdo como inativo (soft delete)."""
    try:
        resposta = (
            supabase
            .table("conteudos")
            .update({"ativo": False})
            .eq("id", id)
            .execute()
        )

        return resposta.data
    except Exception as e:
        st.error(f"Erro ao excluir conteúdo: {e}")
        return None
