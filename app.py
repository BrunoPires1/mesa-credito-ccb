import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import requests
import bcrypt
import os
import json
from datetime import datetime

# ==============================
# CONFIGURAÇÕES VIA AMBIENTE
# ==============================

SHEET_NAME = os.environ["SHEET_NAME"]
WEBHOOK_TEAMS = os.environ["WEBHOOK_TEAMS"]

# Credenciais Google via variável de ambiente
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
    "bruno": bcrypt.hashpw("1234".encode(), bcrypt.gensalt()),
    "maria": bcrypt.hashpw("1234".encode(), bcrypt.gensalt())
}

def login():
    st.title("🔐 Login - Mesa de Crédito")
    user = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user in USERS and bcrypt.checkpw(password.encode(), USERS[user]):
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

def enviar_teams(msg):
    requests.post(WEBHOOK_TEAMS, json={"text": msg})

def carregar_base():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def assumir_ccb(ccb, valor, parceiro, analista):
    df = carregar_base()

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
    return "✅ CCB assumida com sucesso!"

def finalizar_ccb(ccb, resultado, anotacoes):
    cells = sheet.findall(str(ccb))
    if not cells:
        return "CCB não encontrada."

    row = cells[0].row
    sheet.update_cell(row, 6, resultado)
    sheet.update_cell(row, 8, anotacoes)

    enviar_teams(f"📢 CCB {ccb} finalizada como {resultado}")
    return "✅ Análise finalizada!"

# ==============================
# INTERFACE
# ==============================

st.title("📋 Mesa de Análise CCB")

ccb = st.text_input("Número da CCB")
valor = st.text_input("Valor Líquido")
parceiro = st.text_input("Parceiro")
analista = st.session_state["user"]

if st.button("Assumir Análise"):
    st.info(assumir_ccb(ccb, valor, parceiro, analista))

st.divider()

resultado = st.radio("Resultado", ["Análise Aprovada", "Análise Reprovada"])
anotacoes = st.text_area("Anotações")

if st.button("Finalizar"):
    st.success(finalizar_ccb(ccb, resultado, anotacoes))

st.divider()

st.subheader("📊 Painel")
st.dataframe(carregar_base())