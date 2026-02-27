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
# CONTROLE DE FORMULÁRIO DINÂMICO
# ==============================

if "form_key" not in st.session_state:
    st.session_state["form_key"] = 0

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

    # 🔥 ALTERAÇÃO AQUI (INSERT_ROW)
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

    sheet.insert_row(nova_linha, index=len(dados) + 1)

    st.session_state["ccb_ativa"] = ccb
    return "OK"

def finalizar_ccb(ccb, resultado, anotacoes):

    dados = sheet.get_all_values()

    for idx, linha in enumerate(dados[1:], start=2):
        if str(linha[0]) == str(ccb):

            # 🔥 ALTERAÇÃO AQUI (UPDATE POR RANGE)
            sheet.update(f"F{idx}", [[resultado]])
            sheet.update(f"H{idx}", [[anotacoes]])

            return "Finalizado"

    return "CCB não encontrada."

# ==============================
# INTERFACE
# ==============================

st.title("📋 Mesa de Análise CCB")

st.subheader("Assumir / Retomar Análise")

ccb_input = st.text_input(
    "Número da CCB",
    key=f"campo_ccb_{st.session_state['form_key']}"
)

valor = st.text_input(
    "Valor Líquido",
    key=f"campo_valor_{st.session_state['form_key']}"
)

parceiro = st.text_input(
    "Parceiro",
    key=f"campo_parceiro_{st.session_state['form_key']}"
)

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

            del st.session_state["ccb_ativa"]
            st.session_state["form_key"] += 1
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

    hoje = datetime.now().date()

    col1, col2 = st.columns(2)

    data_inicio = col1.date_input("Data Inicial", value=hoje, format="DD/MM/YYYY")
    data_fim = col2.date_input("Data Final", value=hoje, format="DD/MM/YYYY")

    df = df[
        (df["Data da Análise"] >= pd.to_datetime(data_inicio)) &
        (df["Data da Análise"] <= pd.to_datetime(data_fim) + pd.Timedelta(days=1))
    ]

    status_filtro = st.selectbox(
        "Filtrar por Status",
        ["Todos", "Em Análise", "Análise Pendente", "Análise Aprovada", "Análise Reprovada"]
    )

    if status_filtro != "Todos":
        df = df[df["Status Analista"] == status_filtro]

    df = df.sort_values(by="Data da Análise", ascending=False)

    st.dataframe(df, use_container_width=True, hide_index=True)

    # ==============================
    # RESUMO DO MÊS ATUAL
    # ==============================

    st.divider()
    st.subheader("📈 Resumo do Mês Atual")

    mes_atual = datetime.now().strftime("%m/%Y")
    df["MesAno"] = df["Data da Análise"].dt.strftime("%m/%Y")

    df_mes_atual = df[df["MesAno"] == mes_atual]

    if not df_mes_atual.empty:

    pendentes = df_mes_atual[df_mes_atual["Status Analista"] == "Análise Pendente"].shape[0]
    aprovadas = df_mes_atual[df_mes_atual["Status Analista"] == "Análise Aprovada"].shape[0]
    reprovadas = df_mes_atual[df_mes_atual["Status Analista"] == "Análise Reprovada"].shape[0]
    total = df_mes_atual.shape[0]

    resumo_mes = pd.DataFrame({
        "Status": [
            "Propostas Pendentes",
            "Propostas Aprovadas",
            "Propostas Reprovadas",
            "Total de Propostas"
        ],
        "Quantidade": [
            pendentes,
            aprovadas,
            reprovadas,
            total
        ]
    })

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()

    barras = ax.bar(resumo_mes["Status"], resumo_mes["Quantidade"])

    # Adiciona rótulo (quantidade) acima das barras
    for barra in barras:
        altura = barra.get_height()
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            altura,
            f'{int(altura)}',
            ha='center',
            va='bottom'
        )

    ax.set_ylabel("Quantidade")
    ax.set_title("Resumo do Mês Atual")
    plt.xticks(rotation=45)

    st.pyplot(fig)

    else:
    st.info("Nenhuma proposta encontrada no mês atual.")

    # ==============================
    # DASHBOARD POR ANALISTA
    # ==============================

    st.divider()
    st.subheader("👤 Dashboard por Analista")

    meses = sorted(df["MesAno"].dropna().unique(), reverse=True)

    if len(meses) > 0:

        mes_sel = st.selectbox("Selecionar Mês/Ano", meses)

        df_mes = df[df["MesAno"] == mes_sel]

        resumo = df_mes.groupby("Analista").agg(
            Total=("Status Analista", "count"),
            Em_Analise=("Status Analista", lambda x: (x == "Em Análise").sum()),
            Pendentes=("Status Analista", lambda x: (x == "Análise Pendente").sum()),
            Aprovadas=("Status Analista", lambda x: (x == "Análise Aprovada").sum()),
            Reprovadas=("Status Analista", lambda x: (x == "Análise Reprovada").sum())
        ).reset_index()

        resumo = resumo.sort_values(by="Total", ascending=False)

        st.dataframe(resumo, use_container_width=True, hide_index=True)



