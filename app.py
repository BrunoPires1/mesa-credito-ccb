import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import os
import json
from datetime import datetime
import pandas as pd

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

    if len(dados) > 1:
        for linha in dados[1:]:

            numero = str(linha[0])
            status = linha[5]

            if numero == str(ccb):

                if status in ["Análise Aprovada", "Análise Reprovada"]:
                    return "⚠️ Esta CCB já foi finalizada."

                if status in ["Em Análise", "Análise Pendente"]:
                    st.session_state["ccb_ativa"] = ccb
                    return "CONTINUAR"

    # Se não existir → cria nova
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

    st.session_state["ccb_ativa"] = ccb
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

st.subheader("Assumir / Retomar Análise")

ccb = st.text_input("Número da CCB")
valor = st.text_input("Valor Líquido")
parceiro = st.text_input("Parceiro")

# 🔹 Exibir status automaticamente
if ccb:
    info = buscar_ccb(ccb)

    if info:
        st.info(f"""
        📌 CCB já existente  
        👤 Analista: {info[6]}  
        📊 Status: {info[5]}
        """)

if st.button("Assumir Análise"):
    resposta = assumir_ccb(ccb, valor, parceiro, analista)

    if resposta == "OK":
        st.success("CCB criada e assumida com sucesso!")

    elif resposta == "CONTINUAR":
        st.info("Retomando análise desta CCB.")

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

        if resultado == "Análise Pendente":

            if not anotacoes:
                st.error("Para Análise Pendente é obrigatório preencher Anotações.")
            else:
                finalizar_ccb(ccb, resultado, anotacoes)
                st.warning("CCB marcada como Pendente.")

        else:
            finalizar_ccb(ccb, resultado, anotacoes)
            st.success("Análise finalizada com sucesso!")
            del st.session_state["ccb_ativa"]

# ==============================
# PAINEL COM FILTRO
# ==============================

st.divider()
st.subheader("📊 Painel Geral")

dados = carregar_base()

if len(dados) > 1:

    header = dados[0]
    registros = dados[1:]

    status_filtro = st.selectbox(
        "Filtrar por Status",
        ["Todos", "Em Análise", "Análise Pendente", "Análise Aprovada", "Análise Reprovada"]
    )

    if status_filtro != "Todos":
        registros = [r for r in registros if r[5] == status_filtro]

    st.table([header] + registros)

    # ==============================
    # DASHBOARD
    # ==============================

    st.divider()
    st.subheader("📈 Dashboard Executivo")

    df = pd.DataFrame(registros, columns=header)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Em Análise", df[df["Status Analista"] == "Em Análise"].shape[0])
    col2.metric("Pendentes", df[df["Status Analista"] == "Análise Pendente"].shape[0])
    col3.metric("Aprovadas", df[df["Status Analista"] == "Análise Aprovada"].shape[0])
    col4.metric("Reprovadas", df[df["Status Analista"] == "Análise Reprovada"].shape[0])

    st.bar_chart(df["Status Analista"].value_counts())

else:
    st.write("Nenhum registro encontrado.")
