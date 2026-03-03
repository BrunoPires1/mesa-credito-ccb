import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import pytz

st.set_page_config(layout="wide")

# ==============================
# ESTILO PERSONALIZADO (CSS)
# ==============================

st.markdown("""
<style>
.stApp { background-color: #f4f6f9; }
h1, h2, h3 { color: #0d3b66; }
.stButton>button {
    background-color: #0d3b66;
    color: white;
    border-radius: 8px;
    padding: 8px 16px;
    border: none;
}
.stButton>button:hover { background-color: #144e8c; }
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# CONFIGURAÇÕES GOOGLE
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
# LOGIN
# ==============================

def carregar_usuarios():
    aba = client.open(SHEET_NAME).worksheet("USUARIOS")
    dados = aba.get_all_values()

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
        if user in USERS and USERS[user]["senha"] == password:
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
# MENU LATERAL
# ==============================

menu_opcoes = ["📋 Operação", "📊 Acompanhamento"]
if perfil == "Supervisor":
    menu_opcoes.append("🔐 Administração")

menu = st.sidebar.selectbox("Menu", menu_opcoes)

st.sidebar.markdown("---")
st.sidebar.write(f"👤 Usuário: **{analista}**")
st.sidebar.write(f"🎯 Perfil: **{perfil}**")

if st.sidebar.button("🚪 Sair"):
    del st.session_state["user"]
    del st.session_state["perfil"]
    st.rerun()

# ==============================
# FUNÇÕES
# ==============================

def carregar_base():
    return sheet.get_all_values()

def buscar_ccb(ccb):
    dados = carregar_base()
    for linha in dados[1:]:
        if str(linha[0]) == str(ccb):
            return linha
    return None

def assumir_ccb(ccb, valor, parceiro, analista):
    if not ccb:
        return "Informe a CCB."

    dados = carregar_base()

    for linha in dados[1:]:
        numero = str(linha[0])
        status = linha[5]

        if numero == str(ccb):
            if status in ["Análise Aprovada", "Análise Reprovada"]:
                return "⚠️ Esta CCB já foi finalizada."
            if status in ["Em Análise", "Análise Pendente"]:
                st.session_state["ccb_ativa"] = ccb
                return "CONTINUAR"

    fuso = pytz.timezone("America/Sao_Paulo")
    data_atual = datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")

    nova_linha = [
        ccb, valor, parceiro, data_atual,
        "Assinatura Reprovada", "Em Análise",
        analista, ""
    ]

    sheet.append_row(nova_linha)
    st.session_state["ccb_ativa"] = ccb
    return "OK"

def finalizar_ccb(ccb, resultado, anotacoes):
    dados = carregar_base()
    for idx, linha in enumerate(dados[1:], start=2):
        if str(linha[0]) == str(ccb):
            sheet.update(f"F{idx}", [[resultado]])
            sheet.update(f"H{idx}", [[anotacoes]])
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
            st.rerun()
        elif resposta == "CONTINUAR":
            st.success("Retomando análise desta CCB.")
            st.rerun()
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

        df["Data da Análise"] = pd.to_datetime(
            df["Data da Análise"],
            dayfirst=True,
            errors="coerce"
        )

        df = df.dropna(subset=["Data da Análise"])
        df = df.sort_values(by="Data da Análise", ascending=False)
        df["Data da Análise"] = df["Data da Análise"].dt.strftime("%d/%m/%Y %H:%M:%S")

        st.dataframe(df, use_container_width=True, hide_index=True)
