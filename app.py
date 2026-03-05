import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime
import pandas as pd
import io
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# ==============================
# CONTROLE DE TEMA (CLARO / ESCURO)
# ==============================

if "tema" not in st.session_state:
    st.session_state.tema = "claro"

st.write("SISTEMA DE CONTROLE DE ANÁLISE DE CRÉDITO ECONSIGNADO")

# ==============================
# ESTILO DINÂMICO (CLARO / ESCURO)
# ==============================

if st.session_state.tema == "claro":

    st.markdown("""
    <style>
    .stApp {
        background-color: #f4f6f9;
        color: #000000;
    }

    h1, h2, h3 {
        color: #0d3b66;
    }

    .stButton>button {
        background-color: #0d3b66;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
    }
    </style>
    """, unsafe_allow_html=True)

else:

    st.markdown("""
    <style>

    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }

    h1, h2, h3 {
        color: #58a6ff;
    }

    /* labels dos campos */
    label {
        color: #e6edf3 !important;
        font-weight: 500;
    }

    /* texto digitado */
    input, textarea {
        color: #ffffff !important;
    }

    /* fundo dos campos */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
    }

    /* selectbox */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #161b22 !important;
        color: #ffffff !important;
    }

    /* texto dentro do select */
    .stSelectbox div {
        color: #ffffff !important;
    }

    /* botões */
    .stButton>button {
        background-color: #238636;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
    }

    /* tabela */
    .stDataFrame {
        color: white;
    }

    </style>
    """, unsafe_allow_html=True)

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
sheet_usuarios = client.open(SHEET_NAME).worksheet("USUARIOS")

# ==============================
# LOGIN
# ==============================

def carregar_usuarios():
    dados = sheet_usuarios.get_all_values()

    usuarios_dict = {}

    if len(dados) > 1:
        for linha in dados[1:]:
            usuarios_dict[linha[0]] = {
                "senha": linha[1],
                "perfil": linha[2]
            }

    return usuarios_dict

def login():
    st.title("🔐 Login - Mesa de Crédito")

    user = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        usuarios = carregar_usuarios()

        if user in usuarios and usuarios[user]["senha"] == password:

            st.session_state["user"] = user
            st.session_state["perfil"] = usuarios[user]["perfil"]

            st.rerun()

        else:
            st.error("Usuário ou senha inválidos")
        
if "user" not in st.session_state:
    login()
    st.stop()

analista = st.session_state["user"]

# ==============================
# MENU LATERAL
# ==============================

opcoes_menu = ["📋 Operação", "📊 Acompanhamento"]

if st.session_state["perfil"] == "Supervisor":
    opcoes_menu.append("🔐 Administração")

menu = st.sidebar.selectbox("Menu", opcoes_menu)

st.sidebar.markdown("---")
st.sidebar.write(f"👤 Usuário: **{analista}**")
st.sidebar.write(f"🔑 Perfil: **{st.session_state['perfil']}**")
# BOTÃO DE TROCA DE TEMA
if st.session_state.tema == "claro":
    if st.sidebar.button("🌙 Modo Escuro"):
        st.session_state.tema = "escuro"
        st.rerun()
else:
    if st.sidebar.button("☀️ Modo Claro"):
        st.session_state.tema = "claro"
        st.rerun()

# ==============================
# FUNÇÕES
# ==============================

@st.cache_data(ttl=30)
def carregar_base():
    return carregar_base()

def buscar_ccb(ccb):
    dados = carregar_base()
    if len(dados) <= 1:
        return None
    for linha in dados[1:]:
        if str(linha[0]) == str(ccb):
            return linha
    return None

def assumir_ccb(ccb, valor, parceiro, analista, status_bankerize):
    if not ccb:
        return "Informe a CCB."

    dados = carregar_base()

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
        status_bankerize,  # 🔥 AGORA VEM DO SELECTBOX
        "Em Análise",
        analista,
        ""
    ]

    sheet.insert_row(nova_linha, index=len(dados) + 1)
    st.cache_data.clear()
    st.session_state["ccb_ativa"] = ccb
    return "OK"

def finalizar_ccb(ccb, resultado, anotacoes, status_bankerize):
    dados = sheet.get_all_values()
    for idx, linha in enumerate(dados[1:], start=2):
        if str(linha[0]) == str(ccb):
            sheet.update(f"E{idx}", [[status_bankerize]])
            sheet.update(f"F{idx}", [[resultado]])
            sheet.update(f"H{idx}", [[anotacoes]])
            st.cache_data.clear()
            return "Finalizado"
    return "CCB não encontrada."

# ==============================
# 📋 OPERAÇÃO
# ==============================

if menu == "📋 Operação":

    st.title("📋 Mesa de Análise CCB")

    ccb_input = st.text_input("Número da CCB")
    valor = st.text_input("Valor Líquido")
    parceiro = st.text_input("Parceiro")

    status_bankerize = st.selectbox(
        "Status Bankerize",
        [
            "Aguardando Análise da Assinatura",
            "Aguardando Análise de Risco",
            "Aguardando Análise Manual da Assinatura",
            "Assinatura Reprovada",
            "Pendente"
        ],
        key="status_bankerize_select"
    )

    if ccb_input:
        info = buscar_ccb(ccb_input)
        if info:
            st.info(
                f"📌 CCB já existente  \n"
                f"👤 Analista: {info[6]}  \n"
                f"📊 Status: {info[5]}"
            )

    if st.button("Assumir Análise"):
        resposta = assumir_ccb(
            ccb_input,
            valor,
            parceiro,
            analista,
            status_bankerize
        )

        if resposta == "OK":
            st.success("CCB criada e assumida com sucesso!")
        elif resposta == "CONTINUAR":
            st.success("Retomando análise desta CCB.")
        else:
            st.error(resposta)

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
                finalizar_ccb(st.session_state["ccb_ativa"], resultado, anotacoes, status_bankerize)
                st.success("Análise finalizada com sucesso!")
                del st.session_state["ccb_ativa"]
                st.rerun()

    # ==============================
    # 📊 PAINEL GERAL
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
        df = df.sort_values(by="Data da Análise", ascending=False)

        # FORMATO BRASILEIRO
        df["Data da Análise"] = df["Data da Análise"].dt.strftime("%d/%m/%Y %H:%M:%S")

        st.dataframe(df, use_container_width=True, hide_index=True)

    else:
        st.info("Nenhum registro encontrado.")

# ==============================
# 📊 ACOMPANHAMENTO
# ==============================

if menu == "📊 Acompanhamento":

    st.title("📊 Acompanhamento")

    dados = carregar_base()
    if len(dados) > 1:

        header = dados[0]
        registros = dados[1:]
        df = pd.DataFrame(registros, columns=header)

        df["Data da Análise"] = pd.to_datetime(df["Data da Análise"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["Data da Análise"])

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

            fig, ax = plt.subplots()
            barras = ax.bar(resumo_mes["Status"], resumo_mes["Quantidade"])

            for barra in barras:
                altura = barra.get_height()
                ax.text(
                    barra.get_x() + barra.get_width() / 2,
                    altura,
                    f'{int(altura)}',
                    ha='center',
                    va='bottom'
                )

            plt.xticks(rotation=45)
            st.pyplot(fig)

        else:
            st.info("Nenhuma proposta encontrada no mês atual.")

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

# ==============================
# 🔐 ADMINISTRAÇÃO
# ==============================

if menu == "🔐 Administração":

    if st.session_state["perfil"] != "Supervisor":
        st.warning("Acesso restrito a Supervisores.")
        st.stop()

    st.title("🔐 Administração de Usuários")

    usuarios = carregar_usuarios()

    # LISTAR USUÁRIOS
    lista = []
    for nome, dados in usuarios.items():
        lista.append({
            "Usuário": nome,
            "Perfil": dados["perfil"]
        })

    df_users = pd.DataFrame(lista)
    st.dataframe(df_users, use_container_width=True, hide_index=True)

    st.divider()

    # ADICIONAR USUÁRIO
    st.subheader("Adicionar Novo Usuário")

    novo_usuario = st.text_input("Nome do Usuário")
    nova_senha = st.text_input("Senha", type="password")
    novo_perfil = st.selectbox("Perfil", ["Operador", "Supervisor"])

    if st.button("Cadastrar Usuário"):

        if novo_usuario and nova_senha:

            sheet_usuarios.append_row([
                novo_usuario,
                nova_senha,
                novo_perfil
            ])

            st.success("Usuário cadastrado com sucesso!")
            st.rerun()
        else:
            st.error("Preencha todos os campos.")

    st.divider()

    # EXCLUIR USUÁRIO
    st.subheader("Excluir Usuário")

    usuario_excluir = st.selectbox(
        "Selecionar Usuário para Excluir",
        list(usuarios.keys())
    )

    if st.button("Excluir Usuário"):

        dados = sheet_usuarios.get_all_values()

        for idx, linha in enumerate(dados[1:], start=2):
            if linha[0] == usuario_excluir:
                sheet_usuarios.delete_rows(idx)
                break

        st.success("Usuário excluído com sucesso!")
        st.rerun()








