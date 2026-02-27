import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime
import pandas as pd

# ==============================
# CONFIGURAÇÕES
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

analista = st.session_state["user"]

# ==============================
# FUNÇÕES
# ==============================

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

    # Criar nova
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

    st.session_state["ccb_ativa"] = ccb
    return "OK"

def finalizar_ccb(ccb, resultado, anotacoes):

    dados = sheet.get_all_values()

    for idx, linha in enumerate(dados[1:], start=2):

        if str(linha[0]) == str(ccb):

            sheet.update_cell(idx, 6, resultado)
            sheet.update_cell(idx, 8, anotacoes)
            return "Finalizado"

    return "CCB não encontrada."

# ==============================
# INTERFACE
# ==============================

st.title("📋 Mesa de Análise CCB")

st.subheader("Assumir / Retomar Análise")

ccb_input = st.text_input("Número da CCB")
valor = st.text_input("Valor Líquido")
parceiro = st.text_input("Parceiro")

# Mostrar status
if ccb_input:
    info = buscar_ccb(ccb_input)

    if info:
        st.info(f"""
        📌 CCB já existente  
        👤 Analista: {info[6]}  
        📊 Status: {info[5]}
        """)

if st.button("Assumir Análise"):

    resposta = assumir_ccb(ccb_input, valor, parceiro, analista)

    if resposta == "OK":
        st.success("CCB criada e assumida com sucesso!")

    elif resposta == "CONTINUAR":
        st.success("Retomando análise desta CCB.")

    else:
        st.error(resposta)

# ==============================
# FINALIZAÇÃO
# ==============================

if "ccb_ativa" in st.session_state:

    st.divider()
    st.subheader(f"Finalizando CCB {st.session_state['ccb_ativa']}")

    resultado = st.radio(
        "Resultado",
        ["Análise Pendente", "Análise Aprovada", "Análise Reprovada"]
    )

    anotacoes = st.text_area("Anotações")

    if st.button("Salvar Resultado"):

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
                st.rerun()

        else:
            finalizar_ccb(
                st.session_state["ccb_ativa"],
                resultado,
                anotacoes
            )

            st.success("Análise finalizada com sucesso!")
            del st.session_state["ccb_ativa"]
            st.rerun()

# ==============================
# PAINEL
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

    df = pd.DataFrame(registros, columns=header)

    # ==============================
    # DASHBOARD EXECUTIVO
    # ==============================

    st.divider()
    st.subheader("📈 Dashboard Executivo")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Em Análise", df[df["Status Analista"] == "Em Análise"].shape[0])
    col2.metric("Pendentes", df[df["Status Analista"] == "Análise Pendente"].shape[0])
    col3.metric("Aprovadas", df[df["Status Analista"] == "Análise Aprovada"].shape[0])
    col4.metric("Reprovadas", df[df["Status Analista"] == "Análise Reprovada"].shape[0])

    st.bar_chart(df["Status Analista"].value_counts())

    # ==============================
    # DASHBOARD POR ANALISTA
    # ==============================

    st.divider()
    st.subheader("👤 Performance por Analista")

    analistas = df["Analista"].unique()

    for nome in analistas:

        df_analista = df[df["Analista"] == nome]

        st.markdown(f"### {nome}")

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric("Total", df_analista.shape[0])
        c2.metric("Em Análise", df_analista[df_analista["Status Analista"] == "Em Análise"].shape[0])
        c3.metric("Pendentes", df_analista[df_analista["Status Analista"] == "Análise Pendente"].shape[0])
        c4.metric("Aprovadas", df_analista[df_analista["Status Analista"] == "Análise Aprovada"].shape[0])
        c5.metric("Reprovadas", df_analista[df_analista["Status Analista"] == "Análise Reprovada"].shape[0])

    # ==============================
    # RELATÓRIO MENSAL
    # ==============================

    st.divider()
    st.subheader("📅 Relatório Mensal")

    df["Data da Análise"] = pd.to_datetime(df["Data da Análise"], dayfirst=True, errors="coerce")
    df["MesAno"] = df["Data da Análise"].dt.strftime("%m/%Y")

    meses = df["MesAno"].dropna().unique()

    if len(meses) > 0:

        mes_selecionado = st.selectbox("Selecione o mês", meses)

        df_mes = df[df["MesAno"] == mes_selecionado]

        m1, m2, m3, m4 = st.columns(4)

        m1.metric("Total", df_mes.shape[0])
        m2.metric("Aprovadas", df_mes[df_mes["Status Analista"] == "Análise Aprovada"].shape[0])
        m3.metric("Reprovadas", df_mes[df_mes["Status Analista"] == "Análise Reprovada"].shape[0])
        m4.metric("Pendentes", df_mes[df_mes["Status Analista"] == "Análise Pendente"].shape[0])

        st.bar_chart(df_mes["Status Analista"].value_counts())

else:
    st.write("Nenhum registro encontrado.")
