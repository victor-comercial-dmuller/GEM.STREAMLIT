# Estrutura do Banco de Dados - Sistema de Gestão de Aulas

## IMPORTANTE

Antes de alterar qualquer tela, função ou consulta do sistema, considere que esta é a estrutura oficial do banco Supabase.

Nunca crie tabelas ou relacionamentos novos sem necessidade.

Sempre utilize as tabelas existentes.

Todos os IDs são BIGINT.

---

# Arquitetura Geral

O sistema possui 14 tabelas principais.

Região
    ↓
Localidade
    ↓
Turma
    ↓
Aula
    ↓
Alunos da Aula
    ↓
Avaliações

Além disso existem módulos independentes para:

- Usuários
- Conteúdos
- Planejamentos
- Programas mínimos
- Observações de alunos
- Relatos de dificuldades
- Anexos
- Acessos

---

# Tabelas

## usuarios

Cadastro único de pessoas.

Pode representar:

- ADMIN
- PROFESSOR
- AUXILIAR
- ALUNO

Relacionamentos

usuarios
    ├── Região
    ├── Localidade
    ├── Turmas (Professor)
    ├── Turmas (Auxiliar)
    ├── Avaliações
    ├── Observações
    ├── Relatos
    └── Acessos

---

## regioes

Cadastro das regiões.

Campos principais

id
nome
uf
ativo

Relacionamentos

1 Região

↓

N Localidades

↓

N Usuários

↓

N Turmas

---

## localidades

Pertencem a uma Região.

Relacionamentos

Região

↓

Localidade

↓

Turmas

↓

Usuários

---

## turmas

Cada turma pertence a:

- uma região
- uma localidade
- um professor
- um auxiliar

Relacionamentos

Turma

↓

Aulas

↓

Planejamentos

---

## conteudos

Biblioteca de conteúdos utilizados nas aulas.

Cada aula pode possuir um conteúdo.

Campos

categoria
fase
titulo
descricao

---

## aulas

Representa uma aula realizada.

Cada aula pertence obrigatoriamente a uma Turma.

Pode possuir um Conteúdo.

Relacionamentos

Turma

↓

Aula

↓

Alunos da Aula

---

## alunos_aula

Tabela mais importante do sistema.

Representa a participação de um aluno em determinada aula.

Cada registro possui:

- aluno
- aula
- presença
- conteúdo aplicado
- observação
- horário entrada
- horário saída

Relacionamentos

Aluno

↓

Aluno_Aula

↓

Avaliações

Existe UNIQUE(id_aula,id_aluno).

Nunca pode existir o mesmo aluno duas vezes na mesma aula.

---

## avaliacoes

Avaliações realizadas sobre um registro de alunos_aula.

Nunca são feitas diretamente para o aluno.

Fluxo correto

Aluno

↓

Aluno_Aula

↓

Avaliação

Existe UNIQUE(id_aluno_aula,tipo_avaliacao)

Não pode existir duas avaliações do mesmo tipo para a mesma presença.

---

## planejamentos

Planejamento de aulas.

Relaciona:

Professor

↓

Turma

Possui status:

- RASCUNHO
- ENVIADO
- APROVADO

---

## programas_minimos

Biblioteca de programas mínimos.

Possui atividades armazenadas em JSONB.

---

## observacoes_aluno

Observações gerais do aluno.

Relaciona:

Aluno

↓

Usuário responsável

---

## relatos_dificuldades

Controle de dificuldades dos alunos.

Relaciona

Aluno

Professor

Status possíveis

ABERTO

EM ACOMPANHAMENTO

FINALIZADO

---

## anexos

Tabela genérica.

Pode armazenar anexos de qualquer módulo.

Campos

tabela
id_registro
url

---

## acessos

Log de acesso ao sistema.

Registra

Usuário

Data

IP

Sistema

Navegador

---

# Fluxo principal do sistema

Região

↓

Localidade

↓

Turma

↓

Aula

↓

Aluno da Aula

↓

Avaliação

---

# Chaves estrangeiras

usuarios
    -> regioes
    -> localidades

localidades
    -> regioes

turmas
    -> regioes
    -> localidades
    -> usuarios (professor)
    -> usuarios (auxiliar)

aulas
    -> turmas
    -> conteudos

alunos_aula
    -> aulas
    -> usuarios

avaliacoes
    -> alunos_aula
    -> usuarios

planejamentos
    -> turmas
    -> usuarios

observacoes_aluno
    -> usuarios (aluno)
    -> usuarios (autor)

relatos_dificuldades
    -> usuarios (aluno)
    -> usuarios (professor)

acessos
    -> usuarios

---

# Índices importantes

UNIQUE

usuarios.login

regioes.nome

localidades(regiao,nome)

turmas(localidade,nome)

conteudos(categoria,fase,titulo)

alunos_aula(id_aula,id_aluno)

avaliacoes(id_aluno_aula,tipo_avaliacao)

Esses índices NÃO devem ser violados.

---

# Triggers

As tabelas abaixo atualizam automaticamente o campo updated_at:

- regioes
- localidades
- usuarios
- turmas
- conteudos
- aulas
- alunos_aula
- avaliacoes
- planejamentos
- relatos_dificuldades

Utilizam a função

atualizar_updated_at()

Não atualizar updated_at manualmente.

---

# Regras para qualquer IA

Antes de alterar qualquer tela:

1. Nunca criar novas tabelas se existir uma equivalente.

2. Nunca duplicar informações existentes.

3. Sempre utilizar os relacionamentos já definidos.

4. Toda consulta deve respeitar as Foreign Keys.

5. Avaliações pertencem ao registro de alunos_aula e não diretamente ao aluno.

6. O fluxo principal do sistema é:

Região
→ Localidade
→ Turma
→ Aula
→ Alunos da Aula
→ Avaliações

7. Sempre reutilizar tabelas existentes antes de sugerir alterações estruturais.

8. Não remover índices, constraints ou triggers existentes.

9. Considerar esta documentação como a fonte oficial da estrutura do banco.