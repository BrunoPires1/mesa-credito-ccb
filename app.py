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

LOGO_URL = "https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPOSITORIO/main/logo.png"

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
    st.image(LOGO_URL, width=250)
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
    for linha in dados[1:]:
        if str(linha[0]) == str(ccb):
            return linha
    return None

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

            # MELHORIA: não exigir valor/parceiro se já existir
            if status in ["Em Análise", "Análise Pendente"]:
                st.session_state["ccb_ativa"] = ccb
                return "CONTINUAR"

    # Nova CCB
    if not valor or not parceiro:
        return "Informe Valor Líquido e Parceiro."

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

st.image(LOGO_URL, width=200)
st.title("📋 Mesa de Análise CCB")

st.subheader("Assumir / Retomar Análise")

ccb_input = st.text_input("Número da CCB", key="ccb_input")
valor = st.text_input("Valor Líquido", key="valor_input")
parceiro = st.text_input("Parceiro", key="parceiro_input")

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

    if st.button("Finalizar Análise"):

        if resultado == "Análise Pendente" and not anotacoes:
            st.error("Para Análise Pendente é obrigatório preencher Anotações.")
        else:
            finalizar_ccb(st.session_state["ccb_ativa"], resultado, anotacoes)

            st.success("Análise finalizada com sucesso!")

            # MELHORIA: limpar campos
            del st.session_state["ccb_ativa"]
            st.session_state["ccb_input"] = ""
            st.session_state["valor_input"] = ""
            st.session_state["parceiro_input"] = ""

            st.rerun()

# ==============================
# PAINEL GERAL
# ==============================

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

    # ==============================
    # GRÁFICO MÊS ATUAL (NOVO)
    # ==============================

    mes_atual = datetime.now().strftime("%m/%Y")
    df["MesAno"] = df["Data da Análise"].dt.strftime("%m/%Y")
    df_mes = df[df["MesAno"] == mes_atual]

    if not df_mes.empty:

        pendentes = df_mes[df_mes["Status Analista"] == "Análise Pendente"].shape[0]
        aprovadas = df_mes[df_mes["Status Analista"] == "Análise Aprovada"].shape[0]
        reprovadas = df_mes[df_mes["Status Analista"] == "Análise Reprovada"].shape[0]
        total = df_mes.shape[0]

        grafico_df = pd.DataFrame({
            "Status": ["Pendentes", "Aprovadas", "Reprovadas", "Total"],
            "Quantidade": [pendentes, aprovadas, reprovadas, total]
        })

        st.subheader(f"📈 Resumo Mês Atual ({mes_atual})")
        st.bar_chart(grafico_df.set_index("Status"))

    # ==============================
    # TABELA
    # ==============================

    df = df.sort_values(by="Data da Análise", ascending=False)
    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.write("Nenhum registro encontrado.")
