import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
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

def enviar_teams(msg):
    requests.post(WEBHOOK_TEAMS, json={"text": msg})

def carregar_base():
    return sheet.get_all_values()

def assumir_ccb(ccb, valor, parceiro, analista):

    if not ccb:
        return "Informe a CCB."

    dados = sheet.get_all_values()

    if len(dados) > 1:
        for linha in dados[1:]:
            if str(linha[0]) == str(ccb):
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

    enviar_teams(f"📢 CCB {ccb} atualizada para {resultado}")

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
        ["Análise Pendente", "Análise Aprovada", "Análise Reprovada"]
    )

    anotacoes = st.text_area("Anotações")

    if st.button("Finalizar Análise"):

        # CASO 1 — PENDENTE
        if resultado == "Análise Pendente":

            if not anotacoes:
                st.error("Para Análise Pendente é obrigatório preencher Anotações.")
            else:
                finalizar_ccb(
                    st.session_state["ccb_ativa"],
                    resultado,
                    anotacoes
                )

                st.warning("CCB marcada como Pendente.")
                # NÃO remove da sessão (continua ativa)

        # CASO 2 — APROVADA OU REPROVADA
        else:

            finalizar_ccb(
                st.session_state["ccb_ativa"],
                resultado,
                anotacoes
            )

            st.success("Análise finalizada com sucesso!")
            del st.session_state["ccb_ativa"]

# ==============================
# PAINEL EXECUTIVO
# ==============================

st.divider()
st.subheader("📊 Painel Geral")

dados = carregar_base()

if len(dados) > 0:
    st.table(dados)
else:
    st.write("Nenhum registro encontrado.")
