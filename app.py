import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime
import pandas as pd
import io

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

def gerar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Relatorio")
    output.seek(0)
    return output

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

    for linha in dados[1:]:
        numero = str(linha[0])
        status = linha[5]

        if numero == str(ccb):

            if status in ["Análise Aprovada", "Análise Reprovada"]:
                return "⚠️ Esta CCB já foi finalizada."

            if status in ["Em Análise", "Análise Pendente"]:
                st.session_state["ccb_ativa"] = ccb
                return "CONTINUAR"

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
                finalizar_ccb(st.session_state["ccb_ativa"], resultado, anotacoes)
                st.warning("CCB marcada como Pendente.")
                st.rerun()
        else:
            finalizar_ccb(st.session_state["ccb_ativa"], resultado, anotacoes)
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
    df = pd.DataFrame(registros, columns=header)

    df["Data da Análise"] = pd.to_datetime(
        df["Data da Análise"],
        dayfirst=True,
        errors="coerce"
    )

    df = df.dropna(subset=["Data da Análise"])

    status_filtro = st.selectbox(
        "Filtrar por Status",
        ["Todos", "Em Análise", "Análise Pendente", "Análise Aprovada", "Análise Reprovada"]
    )

    if status_filtro != "Todos":
        df = df[df["Status Analista"] == status_filtro]

    st.dataframe(df, use_container_width=True)

    # ==============================
    # RELATÓRIO POR PERÍODO
    # ==============================

    st.divider()
    st.subheader("📅 Relatório por Período")

    if not df.empty:

        data_min = df["Data da Análise"].min().date()
        data_max = df["Data da Análise"].max().date()

        col_inicio, col_fim = st.columns(2)

        data_inicio = col_inicio.date_input("Data Inicial", value=data_min, format="DD/MM/YYYY")
        data_fim = col_fim.date_input("Data Final", value=data_max, format="DD/MM/YYYY")

        df_periodo = df[
            (df["Data da Análise"] >= pd.to_datetime(data_inicio)) &
            (df["Data da Análise"] <= pd.to_datetime(data_fim) + pd.Timedelta(days=1))
        ]

        st.markdown(
            f"### Período: {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}"
        )

        p1, p2, p3, p4 = st.columns(4)

        p1.metric("Total", df_periodo.shape[0])
        p2.metric("Aprovadas", df_periodo[df_periodo["Status Analista"] == "Análise Aprovada"].shape[0])
        p3.metric("Reprovadas", df_periodo[df_periodo["Status Analista"] == "Análise Reprovada"].shape[0])
        p4.metric("Pendentes", df_periodo[df_periodo["Status Analista"] == "Análise Pendente"].shape[0])

        if not df_periodo.empty:

            st.bar_chart(df_periodo["Status Analista"].value_counts())

            arquivo_excel = gerar_excel(df_periodo)

            st.download_button(
                label="📥 Baixar Excel do Período",
                data=arquivo_excel,
                file_name=f"relatorio_{data_inicio.strftime('%d-%m-%Y')}_ate_{data_fim.strftime('%d-%m-%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        else:
            st.warning("Nenhum registro encontrado nesse período.")

    # ==============================
# DASHBOARD POR ANALISTA
# ==============================

st.divider()
st.subheader("👤 Dashboard por Analista")

df["MesAno"] = df["Data da Análise"].dt.strftime("%m/%Y")
meses_disponiveis = sorted(df["MesAno"].dropna().unique(), reverse=True)

if len(meses_disponiveis) > 0:

    mes_selecionado = st.selectbox("Selecionar Mês/Ano", meses_disponiveis)

    df_mes = df[df["MesAno"] == mes_selecionado]

    if not df_mes.empty:

        resumo = df_mes.groupby("Analista").agg(
            Total=("Status Analista", "count"),
            Em_Analise=("Status Analista", lambda x: (x == "Em Análise").sum()),
            Pendentes=("Status Analista", lambda x: (x == "Análise Pendente").sum()),
            Aprovadas=("Status Analista", lambda x: (x == "Análise Aprovada").sum()),
            Reprovadas=("Status Analista", lambda x: (x == "Análise Reprovada").sum())
        ).reset_index()

        resumo = resumo.sort_values(by="Total", ascending=False)

        st.dataframe(resumo, use_container_width=True)

    else:
        st.warning("Nenhum registro para esse mês.")

else:
    st.warning("Sem dados disponíveis para dashboard.")

