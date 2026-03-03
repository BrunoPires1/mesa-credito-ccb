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
# 🔧 CONFIG GOOGLE
# ==============================

SHEET_NAME = os.environ["SHEET_NAME"]
google_creds = json.loads(os.environ["GOOGLE_CREDENTIALS"])

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet("BASE_CONTROLE")

# ==============================
# 📊 CACHE BASE PRINCIPAL
# ==============================

@st.cache_data(ttl=30)
def carregar_base():
    return sheet.get_all_values()

# ==============================
# 🔐 CACHE USUÁRIOS
# ==============================

@st.cache_data(ttl=300)
def carregar_usuarios():
    aba = client.open(SHEET_NAME).worksheet("USUARIOS")
    dados = aba.get_all_values()

    usuarios = {}
    for linha in dados[1:]:
        if len(linha) >= 2:
            usuarios[linha[0]] = linha[1]
    return usuarios

ADMINS = ["Bruno.Pires", "Fabio.Moura"]

# ==============================
# 🔐 LOGIN
# ==============================

def login():
    st.title("🔐 Login - Mesa de Crédito")

    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        usuarios = carregar_usuarios()  # 🔥 só carrega quando clica

        if user in usuarios and usuarios[user] == senha:
            st.session_state["user"] = user
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

if "user" not in st.session_state:
    login()
    st.stop()

analista = st.session_state["user"]

# ==============================
# 📌 MENU
# ==============================

menu = st.sidebar.selectbox(
    "Menu",
    ["📋 Operação", "📊 Acompanhamento", "🔐 Administração"],
    key="menu_principal"
)

st.sidebar.markdown("---")
st.sidebar.write(f"👤 Usuário: **{analista}**")

# ==============================
# 📋 FUNÇÕES
# ==============================

def buscar_ccb(ccb):
    dados = carregar_base()
    for linha in dados[1:]:
        if str(linha[0]) == str(ccb):
            return linha
    return None

def assumir_ccb(ccb, valor, parceiro):
    if not ccb:
        return "Informe a CCB."

    dados = carregar_base()

    for linha in dados[1:]:
        if linha[0] == ccb:
            st.session_state["ccb_ativa"] = ccb
            return "CONTINUAR"

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
    st.cache_data.clear()  # 🔥 limpa cache
    st.session_state["ccb_ativa"] = ccb
    return "OK"

def finalizar_ccb(ccb, resultado, anotacoes):
    dados = carregar_base()

    for idx, linha in enumerate(dados[1:], start=2):
        if linha[0] == ccb:
            sheet.update(f"F{idx}", [[resultado]])
            sheet.update(f"H{idx}", [[anotacoes]])
            st.cache_data.clear()  # 🔥 limpa cache
            return "Finalizado"

    return "Não encontrada"

# ==============================
# 📋 OPERAÇÃO
# ==============================

if menu == "📋 Operação":

    st.title("📋 Mesa de Análise CCB")

    ccb = st.text_input("Número da CCB")
    valor = st.text_input("Valor Líquido")
    parceiro = st.text_input("Parceiro")

    if ccb:
        info = buscar_ccb(ccb)
        if info:
            st.info(f"📌 Já existe\n👤 Analista: {info[6]}\n📊 Status: {info[5]}")

    if st.button("Assumir Análise"):
        assumir_ccb(ccb, valor, parceiro)
        st.rerun()

    if "ccb_ativa" in st.session_state:

        st.subheader(f"Finalizando {st.session_state['ccb_ativa']}")

        resultado = st.radio(
            "Resultado",
            ["Análise Pendente", "Análise Aprovada", "Análise Reprovada"]
        )

        anotacoes = st.text_area("Anotações")

        if st.button("Finalizar"):
            finalizar_ccb(st.session_state["ccb_ativa"], resultado, anotacoes)
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

    if analista not in ADMINS:
        st.warning("Acesso restrito.")
        st.stop()

    st.title("Administração de Usuários")

    aba = client.open(SHEET_NAME).worksheet("USUARIOS")
    dados = aba.get_all_values()
    df_users = pd.DataFrame(dados[1:], columns=dados[0])

    st.dataframe(df_users, use_container_width=True)

    novo = st.text_input("Novo Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Adicionar"):
        aba.append_row([novo, senha])
        st.cache_data.clear()
        st.rerun()
