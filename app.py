import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# ==============================
# 🎨 ESTILO
# ==============================

st.markdown("""
<style>
.stApp { background-color: #f4f6f9; }
h1, h2, h3 { color: #0d3b66; }
.stButton>button {
    background-color: #0d3b66;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# 🔧 CONFIGURAÇÕES GOOGLE
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
# 🔐 LOGIN
# ==============================

@st.cache_data(ttl=60)
def carregar_usuarios():
    aba = client.open(SHEET_NAME).worksheet("USUARIOS")
    dados = aba.get_all_values()
    usuarios = {}
    for linha in dados[1:]:
        if len(linha) >= 3:
            usuarios[linha[0]] = {"senha": linha[1], "perfil": linha[2]}
    return usuarios

USERS = carregar_usuarios()

def login():
    st.title("🔐 Login - Mesa de Crédito")
    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user in USERS and USERS[user]["senha"] == senha:
            st.session_state["user"] = user
            st.session_state["perfil"] = USERS[user]["perfil"]
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

if "user" not in st.session_state:
    login()
    st.stop()

analista = st.session_state["user"]
perfil = st.session_state["perfil"]

# ==============================
# 📌 MENU
# ==============================

menu_opcoes = ["📋 Operação", "📊 Acompanhamento"]
if perfil == "Supervisor":
    menu_opcoes.append("🔐 Administração")

menu = st.sidebar.selectbox("Menu", menu_opcoes)
st.sidebar.write(f"👤 {analista}")
st.sidebar.write(f"🎯 {perfil}")

if st.sidebar.button("🚪 Sair"):
    st.session_state.clear()
    st.rerun()

# ==============================
# 📊 BASE
# ==============================

@st.cache_data(ttl=30)
def carregar_base():
    return sheet.get_all_values()

def limpar_cache():
    st.cache_data.clear()

# ==============================
# 📋 OPERAÇÃO
# ==============================

if menu == "📋 Operação":

    st.title("📋 Mesa de Análise")

    ccb = st.text_input("Número da CCB")
    valor = st.text_input("Valor Líquido")
    parceiro = st.text_input("Parceiro")

    def assumir():
        if not ccb:
            st.error("Informe a CCB.")
            return

        dados = sheet.get_all_values()

        for linha in dados[1:]:
            if linha[0] == ccb:
                st.session_state["ccb_ativa"] = ccb
                return

        nova = [
            ccb,
            valor,
            parceiro,
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Assinatura Reprovada",
            "Em Análise",
            analista,
            ""
        ]

        sheet.insert_row(nova, index=len(dados)+1)
        limpar_cache()
        st.session_state["ccb_ativa"] = ccb

    if st.button("Assumir Análise"):
        assumir()
        st.rerun()

    if "ccb_ativa" in st.session_state:

        st.subheader(f"Finalizando {st.session_state['ccb_ativa']}")

        resultado = st.radio(
            "Resultado",
            ["Análise Pendente", "Análise Aprovada", "Análise Reprovada"]
        )

        anotacoes = st.text_area("Anotações")

        if st.button("Finalizar"):
            dados = sheet.get_all_values()
            for idx, linha in enumerate(dados[1:], start=2):
                if linha[0] == st.session_state["ccb_ativa"]:
                    sheet.update(f"F{idx}", [[resultado]])
                    sheet.update(f"H{idx}", [[anotacoes]])
                    break

            limpar_cache()
            del st.session_state["ccb_ativa"]
            st.rerun()

    st.divider()
    st.subheader("📊 Painel Geral")

    dados = carregar_base()
    if len(dados) > 1:
        df = pd.DataFrame(dados[1:], columns=dados[0])
        df["Data da Análise"] = pd.to_datetime(df["Data da Análise"], dayfirst=True, errors="coerce")
        df = df.sort_values(by="Data da Análise", ascending=False)
        st.dataframe(df, use_container_width=True)

# ==============================
# 📊 ACOMPANHAMENTO
# ==============================

if menu == "📊 Acompanhamento":

    st.title("📊 Acompanhamento")

    dados = carregar_base()
    if len(dados) > 1:
        df = pd.DataFrame(dados[1:], columns=dados[0])
        df["Data da Análise"] = pd.to_datetime(df["Data da Análise"], dayfirst=True, errors="coerce")
        df["MesAno"] = df["Data da Análise"].dt.strftime("%m/%Y")

        st.subheader("Resumo do Mês Atual")
        mes = datetime.now().strftime("%m/%Y")
        df_mes = df[df["MesAno"] == mes]

        if not df_mes.empty:
            resumo = df_mes["Status Analista"].value_counts()

            fig, ax = plt.subplots()
            barras = ax.bar(resumo.index, resumo.values)

            for b in barras:
                ax.text(b.get_x()+b.get_width()/2, b.get_height(),
                        int(b.get_height()), ha="center", va="bottom")

            plt.xticks(rotation=45)
            st.pyplot(fig)

        st.divider()
        st.subheader("Dashboard por Analista")

        resumo_analista = df.groupby("Analista")["Status Analista"].count().reset_index()
        st.dataframe(resumo_analista, use_container_width=True)

# ==============================
# 🔐 ADMINISTRAÇÃO
# ==============================

if menu == "🔐 Administração":

    if perfil != "Supervisor":
        st.warning("Acesso restrito.")
        st.stop()

    st.title("Administração")

    aba = client.open(SHEET_NAME).worksheet("USUARIOS")
    dados = aba.get_all_values()
    df_users = pd.DataFrame(dados[1:], columns=dados[0])

    st.dataframe(df_users, use_container_width=True)

    st.subheader("Adicionar Usuário")

    novo = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    perfil_novo = st.selectbox("Perfil", ["Operador", "Supervisor"])

    if st.button("Adicionar"):
        aba.append_row([novo, senha, perfil_novo])
        limpar_cache()
        st.rerun()
