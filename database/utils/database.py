from config import supabase
import streamlit as st


# ==========================
# CONSULTAS
# ==========================

@st.cache_data(ttl=60)
def carregar_regioes():
    return (
        supabase
        .table("regioes")
        .select("*")
        .order("nome")
        .execute()
        .data
    )


@st.cache_data(ttl=60)
def carregar_localidades():
    return (
        supabase
        .table("localidades")
        .select("*")
        .order("nome")
        .execute()
        .data
    )


@st.cache_data(ttl=60)
def carregar_turmas():
    return (
        supabase
        .table("turmas")
        .select("*")
        .eq("status", "ATIVA")
        .order("nome")
        .execute()
        .data
    )


@st.cache_data(ttl=60)
def carregar_conteudos():
    return (
        supabase
        .table("conteudos")
        .select("*")
        .order("categoria")
        .order("fase")
        .order("titulo")
        .execute()
        .data
    )


@st.cache_data(ttl=60)
def carregar_professores():

    return (
        supabase
        .table("usuarios")
        .select("*")
        .eq("perfil", "PROFESSOR")
        .eq("status", "ATIVO")
        .order("nome")
        .execute()
        .data
    )


@st.cache_data(ttl=60)
def carregar_auxiliares():

    return (
        supabase
        .table("usuarios")
        .select("*")
        .eq("perfil", "AUXILIAR")
        .eq("status", "ATIVO")
        .order("nome")
        .execute()
        .data
    )


@st.cache_data(ttl=60)
def carregar_alunos():

    return (
        supabase
        .table("usuarios")
        .select("*")
        .eq("perfil", "ALUNO")
        .eq("status", "ATIVO")
        .order("nome")
        .execute()
        .data
    )