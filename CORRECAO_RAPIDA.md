# ⚡ CORREÇÃO RÁPIDA - DEPLOY STREAMLIT NO RENDER

## 🎯 PROBLEMA

Você está tentando rodar um app **Streamlit** com comando de **Flask**!

---

## ✅ SOLUÇÃO (3 PASSOS)

### 1️⃣ CORRIGIR START COMMAND NO RENDER (2 minutos)

**Acesse:**
```
Render Dashboard → Seu Serviço → Settings → Build & Deploy
```

**Encontre "Start Command" e SUBSTITUA:**

❌ **ERRADO:**
```bash
python app.py
```

✅ **CORRETO:**
```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**Clique em:** `Save Changes`

---

### 2️⃣ VERIFICAR VARIÁVEIS DE AMBIENTE (1 minuto)

**Acesse:**
```
Render Dashboard → Seu Serviço → Environment
```

**Verifique se existem:**

```
SHEET_NAME = "Nome da sua planilha"
GOOGLE_CREDENTIALS = {"type":"service_account",...}
```

**Se não existirem, adicione!**

**⚠️ IMPORTANTE:** 
- `GOOGLE_CREDENTIALS` deve ser o JSON **completo** em **uma única linha**
- Copie direto do arquivo JSON do Google Cloud

---

### 3️⃣ COMPARTILHAR PLANILHA GOOGLE (1 minuto)

**Encontre o email do Service Account:**
- Abra o JSON de credenciais
- Procure: `"client_email"`
- Exemplo: `seu-app@projeto.iam.gserviceaccount.com`

**Compartilhe a planilha:**
1. Abra a planilha no Google Sheets
2. Clique em "Compartilhar"
3. Adicione o email do service account
4. Permissão: **Editor**
5. Clique em "Compartilhar"

---

## 🚀 FAZER DEPLOY

### Opção A: Deploy Manual (Recomendado)
```
Render Dashboard → Seu Serviço → Manual Deploy → Deploy latest commit
```

### Opção B: Deploy Automático
```
Fazer push no GitHub → Render detecta automaticamente
```

---

## ⏱️ AGUARDAR (2-3 minutos)

**Logs esperados:**
```
==> Building...
==> Installing dependencies
==> Build successful

==> Starting service...
==> Running: streamlit run app.py...

  You can now view your Streamlit app in your browser.

==> Service is live! ✅
```

---

## ✅ TESTAR

**Acesse a URL:**
```
https://seu-app.onrender.com
```

**Deve aparecer:**
- ✅ Tela de login do Streamlit
- ✅ Sistema de análise de crédito

---

## 🐛 SE DER ERRO

### Erro: "Address already in use"
**Solução:** Verificar se usou `$PORT` (não `10000`)

### Erro: "SHEET_NAME not found"
**Solução:** Adicionar variável de ambiente no Render

### Erro: "Invalid JSON"
**Solução:** JSON deve estar em uma única linha

### Erro: "Permission denied"
**Solução:** Compartilhar planilha com service account

---

## 📋 CHECKLIST RÁPIDO

- [ ] Start Command correto: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
- [ ] `SHEET_NAME` configurado no Render
- [ ] `GOOGLE_CREDENTIALS` configurado no Render (JSON completo)
- [ ] Planilha compartilhada com service account (Editor)
- [ ] Deploy feito (manual ou automático)
- [ ] Logs mostram "Service is live"
- [ ] URL acessível e funcionando

---

## 🎉 PRONTO!

**Tempo total:** ~5 minutos
**Resultado:** Sistema Streamlit funcionando no Render! 🚀

---

**📖 Guia completo:** [CORRECOES_RENDER_STREAMLIT.md](CORRECOES_RENDER_STREAMLIT.md)
