import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import requests
import os
import json
from datetime import datetime

# ==============================
# CONFIGURAÇÕES
# ==============================

SHEET_NAME = os.environ["SHEET_NAME"]
WEBHOOK_TEAMS = os.environ["WEBHOOK_TEAMS"]
google_creds = json.loads(os.environ["GOOGLE_CREDENTIALS"])

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet("BASE_CONTROLE")

# ==============================
# LOGIN SIMPLES
# ==============================

USERS = {
    "bruno": "1234",
    "maria": "1234"
}

def login():
    st.title("🔐 Login - Mesa de Crédito")
    user = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user in USERS and USERS[user] == password:
            st.session_state["user"] = user
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

if "user" not in st.session_state:
    login()
    st.stop()

# ==============================
# FUNÇÕES
# ==============================

def carregar_base():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def enviar_teams(msg):
    requests.post(WEBHOOK_TEAMS, json={"text": msg})

def assumir_ccb(ccb, valor, parceiro, analista):

    df = carregar_base()

    if not ccb:
        return "Informe a CCB."

    if ccb in df["CCB"].astype(str).values:
        return "⚠️ CCB já cadastrada."

    sheet.append_row([
        ccb,
        valor,
        parceiro,
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "Assinatura Reprovada",
        "Em Análise",
        analista,
        ""
    ])

    enviar_teams(f"🔎 CCB {ccb} assumida por {analista}")

    return "OK"

def finalizar_ccb(ccb, resultado, anotacoes):

    cells = sheet.findall(str(ccb))
    if not cells:
        return "CCB não encontrada."

    row = cells[0].row

    sheet.update_cell(row, 6, resultado)
    sheet.update_cell(row, 8, anotacoes)

    enviar_teams(f"📢 CCB {ccb} finalizada como {resultado}")

    return "Finalizado"

# ==============================
# INTERFACE PRINCIPAL
# ==============================

st.title("📋 Mesa de Análise CCB")

analista = st.session_state["user"]

st.subheader("Assumir Nova Análise")

ccb = st.text_input("Número da CCB")
valor = st.text_input("Valor Líquido")
parceiro = st.text_input("Parceiro")

if st.button("Assumir Análise"):
    resposta = assumir_ccb(ccb, valor, parceiro, analista)

    if resposta == "OK":
        st.success("CCB assumida com sucesso!")
        st.session_state["ccb_ativa"] = ccb
    else:
        st.error(resposta)

# ==============================
# FINALIZAR
# ==============================

if "ccb_ativa" in st.session_state:

    st.divider()
    st.subheader("Finalizar Análise")

    resultado = st.radio(
        "Resultado",
        ["Análise Aprovada", "Análise Reprovada"]
    )

    anotacoes = st.text_area("Anotações")

    if st.button("Finalizar Análise"):
        resp = finalizar_ccb(
            st.session_state["ccb_ativa"],
            resultado,
            anotacoes
        )

        if resp == "Finalizado":
            st.success("Análise finalizada com sucesso!")
            del st.session_state["ccb_ativa"]

# ==============================
# PAINEL EXECUTIVO
# ==============================

st.divider()
st.subheader("📊 Painel Geral")

df = carregar_base()
st.dataframe(df, use_container_width=True)
