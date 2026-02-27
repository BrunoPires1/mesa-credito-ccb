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
# CACHE
# ==============================

@st.cache_data(ttl=20)
def carregar_base():
    return sheet.get_all_values()

def limpar_cache():
    carregar_base.clear()

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

def ordenar_planilha():

    dados = sheet.get_all_values()
    header = dados[0]
    registros = dados[1:]

    if not registros:
        return

    df = pd.DataFrame(registros, columns=header)

    df["Data da Análise"] = pd.to_datetime(
        df["Data da Análise"],
        dayfirst=True,
        errors="coerce"
    )

    df = df.sort_values(by="Data da Análise", ascending=False)

    # 🔥 CONVERTE DATA DE VOLTA PARA STRING
    df["Data da Análise"] = df["Data da Análise"].dt.strftime("%d/%m/%Y %H:%M:%S")

    sheet.clear()
    sheet.append_row(header)
    sheet.append_rows(df.values.tolist())

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

    sheet.insert_row(nova_linha, index=2)

    ordenar_planilha()
    limpar_cache()

    st.session_state["ccb_ativa"] = ccb
    return "OK"

def finalizar_ccb(ccb, resultado, anotacoes):

    dados = sheet.get_all_values()

    for idx, linha in enumerate(dados[1:], start=2):
        if str(linha[0]) == str(ccb):
            sheet.update_cell(idx, 6, resultado)
            sheet.update_cell(idx, 8, anotacoes)

            ordenar_planilha()
            limpar_cache()

            return "Finalizado"

    return "CCB não encontrada."

# ==============================
# INTERFACE
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
            finalizar_ccb(st.session_state["ccb_ativa"], resultado, anotacoes)

            if resultado != "Análise Pendente":
                del st.session_state["ccb_ativa"]

            st.rerun()

# ==============================
# PAINEL + RANKING
# ==============================

st.divider()
st.subheader("📊 Painel Geral")

dados = carregar_base()

if len(dados) > 1:

    header = dados[0]
    registros = dados[1:]
    df = pd.DataFrame(registros, columns=header)

    df["Data da Análise"] = pd.to_datetime(df["Data da Análise"], dayfirst=True)

    df = df.sort_values(by="Data da Análise", ascending=False)

    st.dataframe(df, use_container_width=True, hide_index=True)

    # ==============================
    # RANKING ANALISTAS
    # ==============================

    st.divider()
    st.subheader("🏆 Ranking Analistas (Mês Atual)")

    df["MesAno"] = df["Data da Análise"].dt.strftime("%m/%Y")
    mes_atual = datetime.now().strftime("%m/%Y")

    df_mes = df[df["MesAno"] == mes_atual]

    if not df_mes.empty:

        ranking = df_mes.groupby("Analista").agg(
            Total=("Status Analista", "count"),
            Aprovadas=("Status Analista", lambda x: (x == "Análise Aprovada").sum()),
            Reprovadas=("Status Analista", lambda x: (x == "Análise Reprovada").sum())
        ).reset_index()

        ranking = ranking.sort_values(by="Total", ascending=False)

        st.dataframe(ranking, use_container_width=True, hide_index=True)

else:
    st.write("Nenhum registro encontrado.")
