import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime
import pandas as pd
import io
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# ==============================
# ESTILO PERSONALIZADO (CSS)
# ==============================

st.markdown("""
<style>
.stApp {
    background-color: #f4f6f9;
}

h1, h2, h3 {
    color: #0d3b66;
}

.stButton>button {
    background-color: #0d3b66;
    color: white;
    border-radius: 8px;
    padding: 8px 16px;
    border: none;
}

.stButton>button:hover {
    background-color: #144e8c;
    color: white;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# CONFIGURAÇÕES
# ==============================

SHEET_NAME = os.environ["SHEET_NAME"]
google_creds = json.loads(os.environ["GOOGLE_CREDENTIALS"])

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def conectar_google():
    creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)
    return gspread.authorize(creds)

@st.cache_resource
def carregar_sheet():
    client = conectar_google()
    return client.open(SHEET_NAME).worksheet("BASE_CONTROLE")

client = conectar_google()
sheet = carregar_sheet()

# ==============================
# LOGIN
# ==============================

def carregar_usuarios():
    aba_usuarios = client.open(SHEET_NAME).worksheet("USUARIOS")
    dados = aba_usuarios.get_all_values()

    usuarios = {}

    for linha in dados[1:]:
        if len(linha) >= 3:
            usuarios[linha[0]] = {
                "senha": linha[1],
                "perfil": linha[2]
            }

    return usuarios

USERS = carregar_usuarios()

def login():
    st.title("🔐 Login - Mesa de Crédito")
    user = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        if user in USERS:

            if USERS[user]["senha"] == password:

                st.session_state["user"] = user
                st.session_state["perfil"] = USERS[user]["perfil"]

                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")
        else:
            st.error("Usuário ou senha inválidos")

# 🔐 BLOQUEIO DE ACESSO
if "user" not in st.session_state:
    login()
    st.stop()

analista = st.session_state["user"]
perfil = st.session_state["perfil"]

# ==============================
# MENU LATERAL
# ==============================

menu_opcoes = ["📋 Operação", "📊 Acompanhamento"]

if perfil == "Supervisor":
    menu_opcoes.append("🔐 Administração")

menu = st.sidebar.selectbox("Menu", menu_opcoes)

st.sidebar.markdown("---")
st.sidebar.write(f"👤 Usuário: **{analista}**")
st.sidebar.write(f"🎯 Perfil: **{perfil}**")

st.sidebar.markdown("---")

if st.sidebar.button("🚪 Sair"):
    del st.session_state["user"]
    del st.session_state["perfil"]
    st.rerun()

# ==============================
# FUNÇÕES
# ==============================

@st.cache_data(ttl=30)
def carregar_base():
    return sheet.get_all_values()

def buscar_ccb(ccb):
    dados = sheet.get_all_values()
    if len(dados) <= 1:
        return None
    for linha in dados[1:]:
        if str(linha[0]) == str(ccb):
            return linha
    return None

def assumir_ccb(ccb, valor, parceiro, analista):
    if not ccb:
        return "Informe a CCB."

    dados = sheet.get_all_values()

    for linha in dados[1:]:
        numero = str(linha[0])
        status = linha[5]

        if numero == str(ccb):
            if status in ["Análise Aprovada", "Análise Reprovada"]:
                return "⚠️ Esta CCB já foi finalizada."

            if status in ["Em Análise", "Análise Pendente"]:
                st.session_state["ccb_ativa"] = ccb
                return "CONTINUAR"

    nova_linha = [
        ccb,
        valor,
        parceiro,
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "Assinatura Reprovada",
        "Em Análise",
        analista,
        ""
    ]

    sheet.insert_row(nova_linha, index=len(dados) + 1)
    st.session_state["ccb_ativa"] = ccb
    return "OK"

import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime
import pandas as pd
import io
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# ==============================
# ESTILO PERSONALIZADO (CSS)
# ==============================

st.markdown("""
<style>
.stApp {
    background-color: #f4f6f9;
}

h1, h2, h3 {
    color: #0d3b66;
}

.stButton>button {
    background-color: #0d3b66;
    color: white;
    border-radius: 8px;
    padding: 8px 16px;
    border: none;
}

.stButton>button:hover {
    background-color: #144e8c;
    color: white;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# CONFIGURAÇÕES
# ==============================

SHEET_NAME = os.environ["SHEET_NAME"]
google_creds = json.loads(os.environ["GOOGLE_CREDENTIALS"])

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def conectar_google():
    creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)
    return gspread.authorize(creds)

@st.cache_resource
def carregar_sheet():
    client = conectar_google()
    return client.open(SHEET_NAME).worksheet("BASE_CONTROLE")

client = conectar_google()
sheet = carregar_sheet()

# ==============================
# LOGIN
# ==============================

@st.cache_data(ttl=30)
def carregar_usuarios():
    aba_usuarios = client.open(SHEET_NAME).worksheet("USUARIOS")
    dados = aba_usuarios.get_all_values()

    usuarios = {}

    for linha in dados[1:]:
        if len(linha) >= 3:
            usuarios[linha[0]] = {
                "senha": linha[1],
                "perfil": linha[2]
            }

    return usuarios

USERS = carregar_usuarios()

def login():
    st.title("🔐 Login - Mesa de Crédito")
    user = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        if user in USERS:

            if USERS[user]["senha"] == password:

                st.session_state["user"] = user
                st.session_state["perfil"] = USERS[user]["perfil"]

                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")
        else:
            st.error("Usuário ou senha inválidos")

# 🔐 BLOQUEIO DE ACESSO
if "user" not in st.session_state:
    login()
    st.stop()

analista = st.session_state["user"]
perfil = st.session_state["perfil"]

# ==============================
# MENU LATERAL
# ==============================

menu_opcoes = ["📋 Operação", "📊 Acompanhamento"]

if perfil == "Supervisor":
    menu_opcoes.append("🔐 Administração")

menu = st.sidebar.selectbox("Menu", menu_opcoes)

st.sidebar.markdown("---")
st.sidebar.write(f"👤 Usuário: **{analista}**")
st.sidebar.write(f"🎯 Perfil: **{perfil}**")

st.sidebar.markdown("---")

if st.sidebar.button("🚪 Sair"):
    del st.session_state["user"]
    del st.session_state["perfil"]
    st.rerun()

# ==============================
# FUNÇÕES
# ==============================

@st.cache_data(ttl=30)
def carregar_base():
    return sheet.get_all_values()

def buscar_ccb(ccb):
    dados = sheet.get_all_values()
    if len(dados) <= 1:
        return None
    for linha in dados[1:]:
        if str(linha[0]) == str(ccb):
            return linha
    return None

def assumir_ccb(ccb, valor, parceiro, analista):
    if not ccb:
        return "Informe a CCB."

    dados = sheet.get_all_values()

    for linha in dados[1:]:
        numero = str(linha[0])
        status = linha[5]

        if numero == str(ccb):
            if status in ["Análise Aprovada", "Análise Reprovada"]:
                return "⚠️ Esta CCB já foi finalizada."

            if status in ["Em Análise", "Análise Pendente"]:
                st.session_state["ccb_ativa"] = ccb
                return "CONTINUAR"

    nova_linha = [
        ccb,
        valor,
        parceiro,
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "Assinatura Reprovada",
        "Em Análise",
        analista,
        ""
    ]

    sheet.insert_row(nova_linha, index=len(dados) + 1)

    st.cache_data.clear()  # 🔥 LIMPA CACHE

    st.session_state["ccb_ativa"] = ccb
    return "OK"

def finalizar_ccb(ccb, resultado, anotacoes):
    dados = sheet.get_all_values()

    for idx, linha in enumerate(dados[1:], start=2):
        if str(linha[0]) == str(ccb):

            sheet.update(f"F{idx}", [[resultado]])
            sheet.update(f"H{idx}", [[anotacoes]])

            st.cache_data.clear()  # 🔥 LIMPA CACHE

            return "Finalizado"

    return "CCB não encontrada."
# ==============================
# 📋 OPERAÇÃO
# ==============================

if menu == "📋 Operação":

    st.title("📋 Mesa de Análise CCB")

    ccb_input = st.text_input("Número da CCB")
    valor = st.text_input("Valor Líquido")
    parceiro = st.text_input("Parceiro")

    if ccb_input:
        info = buscar_ccb(ccb_input)
        if info:
            st.info(f"📌 CCB já existente  \n👤 Analista: {info[6]}  \n📊 Status: {info[5]}")

    if st.button("Assumir Análise"):
        resposta = assumir_ccb(ccb_input, valor, parceiro, analista)
        if resposta == "OK":
            st.success("CCB criada e assumida com sucesso!")
        elif resposta == "CONTINUAR":
            st.success("Retomando análise desta CCB.")
        else:
            st.error(resposta)

    if "ccb_ativa" in st.session_state:
        st.divider()
        st.subheader(f"Finalizando CCB {st.session_state['ccb_ativa']}")

        resultado = st.radio(
            "Resultado",
            ["Análise Pendente", "Análise Aprovada", "Análise Reprovada"]
        )
        anotacoes = st.text_area("Anotações")

        if st.button("Finalizar Análise"):
            if resultado == "Análise Pendente" and not anotacoes:
                st.error("Para Análise Pendente é obrigatório preencher Anotações.")
            else:
                finalizar_ccb(st.session_state["ccb_ativa"], resultado, anotacoes)
                st.success("Análise finalizada com sucesso!")
                del st.session_state["ccb_ativa"]
                st.rerun()

    st.divider()
    st.subheader("📊 Painel Geral")

    dados = carregar_base()
    if len(dados) > 1:
        header = dados[0]
        registros = dados[1:]
        df = pd.DataFrame(registros, columns=header)

        df["Data da Análise"] = pd.to_datetime(df["Data da Análise"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["Data da Análise"])
        df = df.sort_values(by="Data da Análise", ascending=False)

        st.dataframe(df, use_container_width=True, hide_index=True)

# ==============================
# 📊 ACOMPANHAMENTO
# ==============================

if menu == "📊 Acompanhamento":

    st.title("📊 Acompanhamento")

    dados = carregar_base()
    if len(dados) > 1:

        header = dados[0]
        registros = dados[1:]
        df = pd.DataFrame(registros, columns=header)

        df["Data da Análise"] = pd.to_datetime(df["Data da Análise"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["Data da Análise"])

        st.divider()
        st.subheader("📈 Resumo do Mês Atual")

        mes_atual = datetime.now().strftime("%m/%Y")
        df["MesAno"] = df["Data da Análise"].dt.strftime("%m/%Y")
        df_mes_atual = df[df["MesAno"] == mes_atual]

        if not df_mes_atual.empty:

            pendentes = df_mes_atual[df_mes_atual["Status Analista"] == "Análise Pendente"].shape[0]
            aprovadas = df_mes_atual[df_mes_atual["Status Analista"] == "Análise Aprovada"].shape[0]
            reprovadas = df_mes_atual[df_mes_atual["Status Analista"] == "Análise Reprovada"].shape[0]
            total = df_mes_atual.shape[0]

            resumo_mes = pd.DataFrame({
                "Status": [
                    "Propostas Pendentes",
                    "Propostas Aprovadas",
                    "Propostas Reprovadas",
                    "Total de Propostas"
                ],
                "Quantidade": [
                    pendentes,
                    aprovadas,
                    reprovadas,
                    total
                ]
            })

            fig, ax = plt.subplots()
            barras = ax.bar(resumo_mes["Status"], resumo_mes["Quantidade"])

            for barra in barras:
                altura = barra.get_height()
                ax.text(
                    barra.get_x() + barra.get_width() / 2,
                    altura,
                    f'{int(altura)}',
                    ha='center',
                    va='bottom'
                )

            plt.xticks(rotation=45)
            st.pyplot(fig)

        else:
            st.info("Nenhuma proposta encontrada no mês atual.")

        st.divider()
        st.subheader("👤 Dashboard por Analista")

        meses = sorted(df["MesAno"].dropna().unique(), reverse=True)

        if len(meses) > 0:
            mes_sel = st.selectbox("Selecionar Mês/Ano", meses)
            df_mes = df[df["MesAno"] == mes_sel]

            resumo = df_mes.groupby("Analista").agg(
                Total=("Status Analista", "count"),
                Em_Analise=("Status Analista", lambda x: (x == "Em Análise").sum()),
                Pendentes=("Status Analista", lambda x: (x == "Análise Pendente").sum()),
                Aprovadas=("Status Analista", lambda x: (x == "Análise Aprovada").sum()),
                Reprovadas=("Status Analista", lambda x: (x == "Análise Reprovada").sum())
            ).reset_index()

            resumo = resumo.sort_values(by="Total", ascending=False)
            st.dataframe(resumo, use_container_width=True, hide_index=True)

# ==============================
# 🔐 ADMINISTRAÇÃO
# ==============================

if menu == "🔐 Administração":

    if perfil != "Supervisor":
        st.warning("Acesso restrito a Supervisores.")
        st.stop()

    st.title("🔐 Administração de Usuários")

    aba_usuarios = client.open(SHEET_NAME).worksheet("USUARIOS")
    dados = aba_usuarios.get_all_values()

    df_users = pd.DataFrame(dados[1:], columns=dados[0])

    st.subheader("Usuários Atuais")
    st.dataframe(df_users, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Adicionar Novo Usuário")

    novo_user = st.text_input("Novo Usuário")
    nova_senha = st.text_input("Senha", type="password")
    
    perfil_novo = st.selectbox(
        "Perfil",
        ["Operador", "Supervisor"]
)

    if st.button("Adicionar Usuário"):
        if novo_user and nova_senha:
            aba_usuarios.append_row([
                novo_user,
                nova_senha,
                perfil_novo
    ])
            st.cache_data.clear()  # 🔥 LIMPA CACHE
            st.success("Usuário adicionado com sucesso!")
            st.rerun()
        else:
            st.error("Preencha todos os campos.")

    st.divider()
    st.subheader("Remover Usuário")

    usuario_remover = st.selectbox("Selecionar usuário", df_users["Usuario"])

    if st.button("Remover Usuário"):
        linhas = aba_usuarios.get_all_values()
        for idx, linha in enumerate(linhas):
            if linha[0] == usuario_remover:
                aba_usuarios.delete_rows(idx + 1)
                st.cache_data.clear()  # 🔥 LIMPA CACHE
                st.success("Usuário removido com sucesso!")
                st.rerun()

# ==============================
# 📋 OPERAÇÃO
# ==============================

if menu == "📋 Operação":

    st.title("📋 Mesa de Análise CCB")

    ccb_input = st.text_input("Número da CCB")
    valor = st.text_input("Valor Líquido")
    parceiro = st.text_input("Parceiro")

    if ccb_input:
        info = buscar_ccb(ccb_input)
        if info:
            st.info(f"📌 CCB já existente  \n👤 Analista: {info[6]}  \n📊 Status: {info[5]}")

    if st.button("Assumir Análise"):
        resposta = assumir_ccb(ccb_input, valor, parceiro, analista)
        if resposta == "OK":
            st.success("CCB criada e assumida com sucesso!")
        elif resposta == "CONTINUAR":
            st.success("Retomando análise desta CCB.")
        else:
            st.error(resposta)

    if "ccb_ativa" in st.session_state:
        st.divider()
        st.subheader(f"Finalizando CCB {st.session_state['ccb_ativa']}")

        resultado = st.radio(
            "Resultado",
            ["Análise Pendente", "Análise Aprovada", "Análise Reprovada"]
        )
        anotacoes = st.text_area("Anotações")

        if st.button("Finalizar Análise"):
            if resultado == "Análise Pendente" and not anotacoes:
                st.error("Para Análise Pendente é obrigatório preencher Anotações.")
            else:
                finalizar_ccb(st.session_state["ccb_ativa"], resultado, anotacoes)
                st.success("Análise finalizada com sucesso!")
                del st.session_state["ccb_ativa"]
                st.rerun()

    st.divider()
    st.subheader("📊 Painel Geral")

    dados = carregar_base()
    if len(dados) > 1:
        header = dados[0]
        registros = dados[1:]
        df = pd.DataFrame(registros, columns=header)

        df["Data da Análise"] = pd.to_datetime(df["Data da Análise"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["Data da Análise"])
        df = df.sort_values(by="Data da Análise", ascending=False)

        st.dataframe(df, use_container_width=True, hide_index=True)

# ==============================
# 📊 ACOMPANHAMENTO
# ==============================

if menu == "📊 Acompanhamento":

    st.title("📊 Acompanhamento")

    dados = carregar_base()
    if len(dados) > 1:

        header = dados[0]
        registros = dados[1:]
        df = pd.DataFrame(registros, columns=header)

        df["Data da Análise"] = pd.to_datetime(df["Data da Análise"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["Data da Análise"])

        st.divider()
        st.subheader("📈 Resumo do Mês Atual")

        mes_atual = datetime.now().strftime("%m/%Y")
        df["MesAno"] = df["Data da Análise"].dt.strftime("%m/%Y")
        df_mes_atual = df[df["MesAno"] == mes_atual]

        if not df_mes_atual.empty:

            pendentes = df_mes_atual[df_mes_atual["Status Analista"] == "Análise Pendente"].shape[0]
            aprovadas = df_mes_atual[df_mes_atual["Status Analista"] == "Análise Aprovada"].shape[0]
            reprovadas = df_mes_atual[df_mes_atual["Status Analista"] == "Análise Reprovada"].shape[0]
            total = df_mes_atual.shape[0]

            resumo_mes = pd.DataFrame({
                "Status": [
                    "Propostas Pendentes",
                    "Propostas Aprovadas",
                    "Propostas Reprovadas",
                    "Total de Propostas"
                ],
                "Quantidade": [
                    pendentes,
                    aprovadas,
                    reprovadas,
                    total
                ]
            })

            fig, ax = plt.subplots()
            barras = ax.bar(resumo_mes["Status"], resumo_mes["Quantidade"])

            for barra in barras:
                altura = barra.get_height()
                ax.text(
                    barra.get_x() + barra.get_width() / 2,
                    altura,
                    f'{int(altura)}',
                    ha='center',
                    va='bottom'
                )

            plt.xticks(rotation=45)
            st.pyplot(fig)

        else:
            st.info("Nenhuma proposta encontrada no mês atual.")

        st.divider()
        st.subheader("👤 Dashboard por Analista")

        meses = sorted(df["MesAno"].dropna().unique(), reverse=True)

        if len(meses) > 0:
            mes_sel = st.selectbox("Selecionar Mês/Ano", meses)
            df_mes = df[df["MesAno"] == mes_sel]

            resumo = df_mes.groupby("Analista").agg(
                Total=("Status Analista", "count"),
                Em_Analise=("Status Analista", lambda x: (x == "Em Análise").sum()),
                Pendentes=("Status Analista", lambda x: (x == "Análise Pendente").sum()),
                Aprovadas=("Status Analista", lambda x: (x == "Análise Aprovada").sum()),
                Reprovadas=("Status Analista", lambda x: (x == "Análise Reprovada").sum())
            ).reset_index()

            resumo = resumo.sort_values(by="Total", ascending=False)
            st.dataframe(resumo, use_container_width=True, hide_index=True)

# ==============================
# 🔐 ADMINISTRAÇÃO
# ==============================

if menu == "🔐 Administração":

    if perfil != "Supervisor":
        st.warning("Acesso restrito a Supervisores.")
        st.stop()

    st.title("🔐 Administração de Usuários")

    aba_usuarios = client.open(SHEET_NAME).worksheet("USUARIOS")
    dados = aba_usuarios.get_all_values()

    df_users = pd.DataFrame(dados[1:], columns=dados[0])

    st.subheader("Usuários Atuais")
    st.dataframe(df_users, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Adicionar Novo Usuário")

    novo_user = st.text_input("Novo Usuário")
    nova_senha = st.text_input("Senha", type="password")
    
    perfil_novo = st.selectbox(
        "Perfil",
        ["Operador", "Supervisor"]
)

    if st.button("Adicionar Usuário"):
        if novo_user and nova_senha:
            aba_usuarios.append_row([
                novo_user,
                nova_senha,
                perfil_novo
    ])
            st.cache_data.clear()  # 🔥 LIMPA CACHE
            st.success("Usuário adicionado com sucesso!")
            st.rerun()
        else:
            st.error("Preencha todos os campos.")

    st.divider()
    st.subheader("Remover Usuário")

    usuario_remover = st.selectbox("Selecionar usuário", df_users["Usuario"])

    if st.button("Remover Usuário"):
        linhas = aba_usuarios.get_all_values()
        for idx, linha in enumerate(linhas):
            if linha[0] == usuario_remover:
                aba_usuarios.delete_rows(idx + 1)
                st.cache_data.clear()  # 🔥 LIMPA CACHE
                st.success("Usuário removido com sucesso!")
                st.rerun()

