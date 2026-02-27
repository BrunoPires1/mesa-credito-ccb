import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime
import pandas as pd
import io

st.set_page_config(layout="wide")

# ==============================
# CONFIGURAÇÕES GOOGLE
# ==============================

SHEET_NAME = os.environ["SHEET_NAME"]
google_creds = json.loads(os.environ["GOOGLE_CREDENTIALS"])

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet("BASE_CONTROLE")

# ==============================
# LOGIN
# ==============================

USERS = {
    "Bruno.Pires": "831227",
    "Amanda.Fiorio": "135433",
    "Andressa.Silva": "152909",
    "Antonio.Aymi": "016912",
    "Fabio.Moura": "108026",
    "Hugo.Poltronieri": "104830",
    "Juliana.Santos": "442908",
    "KauaFantoni": "183349",
    "Lorrayne.Falcao": "145472",
    "Matheus.Machado": "132300",
    "Nathalia.Moreira": "189966",
    "Ulisses.Neto": "119715",
}

def login():

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("logo.png", width=220)

    st.markdown("<h2 style='text-align:center;'>Login - Mesa de Crédito</h2>", unsafe_allow_html=True)

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
    try:
        return sheet.get_all_records()
    except Exception as e:
        st.error(f"Erro ao carregar planilha: {e}")
        return []

def buscar_ccb(ccb):
    dados = carregar_base()
    for linha in dados:
        if str(linha["CCB"]) == str(ccb):
            return linha
    return None

def assumir_ccb(ccb, valor, parceiro, analista):

    if not ccb:
        return "Informe a CCB."

    dados = carregar_base()

    for linha in dados:
        if str(linha["CCB"]) == str(ccb):

            status = linha["Status Analista"]

            if status in ["Análise Aprovada", "Análise Reprovada"]:
                return "⚠️ Esta CCB já foi finalizada."

            if status in ["Em Análise", "Análise Pendente"]:
                st.session_state["ccb_ativa"] = ccb
                return "CONTINUAR"

    try:
        sheet.append_row([
            ccb,
            valor,
            parceiro,
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Assinatura Reprovada",
            "Em Análise",
            analista,
            ""
        ], value_input_option="USER_ENTERED")

        st.session_state["ccb_ativa"] = ccb
        return "OK"

    except Exception as e:
        return f"Erro ao salvar: {e}"

def finalizar_ccb(ccb, resultado, anotacoes):

    dados = sheet.get_all_values()

    for idx, linha in enumerate(dados[1:], start=2):

        if str(linha[0]) == str(ccb):

            nova_linha = [
                linha[0],  # CCB
                linha[1],  # Valor
                linha[2],  # Parceiro
                linha[3],  # Data
                linha[4],  # Status Bankerize
                resultado, # Status Analista
                linha[6],  # Analista
                anotacoes  # Anotações
            ]

            try:
                sheet.update(f"A{idx}:H{idx}", [nova_linha])
                return "Finalizado"
            except Exception as e:
                return f"Erro ao atualizar: {e}"

    return "CCB não encontrada."

# ==============================
# INTERFACE PRINCIPAL
# ==============================

col_logo, col_titulo = st.columns([1, 4])

with col_logo:
    st.image("logo.png", width=180)

with col_titulo:
    st.title("Mesa de Análise CCB")

st.subheader("Assumir / Retomar Análise")

ccb_input = st.text_input("Número da CCB")
valor = st.text_input("Valor Líquido")
parceiro = st.text_input("Parceiro")

if ccb_input:
    info = buscar_ccb(ccb_input)
    if info:
        st.info(f"""
        📌 CCB já existente  
        👤 Analista: {info['Analista']}  
        📊 Status: {info['Status Analista']}
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

    if st.button("Finalizar Análise"):

        if resultado == "Análise Pendente" and not anotacoes:
            st.error("Para Análise Pendente é obrigatório preencher Anotações.")
        else:
            resp = finalizar_ccb(st.session_state["ccb_ativa"], resultado, anotacoes)

            if "Erro" in resp:
                st.error(resp)
            else:
                if resultado != "Análise Pendente":
                    del st.session_state["ccb_ativa"]
                st.success("Registro atualizado com sucesso!")
                st.rerun()

# ==============================
# PAINEL GERAL
# ==============================

st.divider()
st.subheader("📊 Painel Geral")

dados = carregar_base()

if dados:

    df = pd.DataFrame(dados)

    df["Data da Análise"] = pd.to_datetime(
        df["Data da Análise"],
        dayfirst=True,
        errors="coerce"
    )

    df = df.sort_values(by="Data da Análise", ascending=False)

    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.write("Nenhum registro encontrado.")
