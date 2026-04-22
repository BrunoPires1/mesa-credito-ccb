# 🔧 CORREÇÕES PARA DEPLOY STREAMLIT NO RENDER

## ⚠️ PROBLEMA IDENTIFICADO

O sistema é **Streamlit**, não Flask! O comando de inicialização estava incorreto.

---

## ✅ CORREÇÕES OBRIGATÓRIAS

### 1. START COMMAND NO RENDER (CRÍTICO!)

**❌ ERRADO (comando atual):**
```bash
python app.py
```

**✅ CORRETO (usar este):**
```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**Como alterar:**
1. Render Dashboard
2. Seu serviço → Settings
3. Build & Deploy
4. Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
5. Save Changes

**⚠️ IMPORTANTE:** Use `$PORT` (variável do Render), não `10000` fixo!

---

### 2. REQUIREMENTS.TXT (Verificar)

**Arquivo atual:**
```
streamlit
gspread
oauth2client
pandas
requests
xlsxwriter
bcrypt
matplotlib
pytz
```

**✅ Está correto!** Mas pode remover linhas não usadas:
- `requests` (não usado no código)
- `xlsxwriter` (não usado no código)
- `pytz` (substituído por `zoneinfo`)

**Versão otimizada (opcional):**
```
streamlit
gspread
oauth2client
pandas
matplotlib
bcrypt
```

---

### 3. VARIÁVEIS DE AMBIENTE NO RENDER

**Como configurar:**
1. Render Dashboard
2. Seu serviço → Environment
3. Adicionar variáveis:

**SHEET_NAME:**
```
Nome da sua planilha Google Sheets
Exemplo: "Sistema Credito Econsignado"
```

**GOOGLE_CREDENTIALS:**
```json
{"type":"service_account","project_id":"seu-projeto","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"seu-service-account@projeto.iam.gserviceaccount.com","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}
```

**⚠️ IMPORTANTE:** 
- JSON em **uma única linha** (sem quebras)
- Incluir **tudo** (chaves privadas, etc.)
- Copiar direto do arquivo JSON do Google Cloud

---

### 4. COMPARTILHAR PLANILHA GOOGLE

**Passo a passo:**

1. **Encontrar o email do Service Account:**
   - Abra o JSON de credenciais
   - Procure por `"client_email"`
   - Exemplo: `seu-app@projeto-123.iam.gserviceaccount.com`

2. **Compartilhar a planilha:**
   - Abra a planilha no Google Sheets
   - Clique em "Compartilhar"
   - Adicione o email do service account
   - Permissão: **Editor**
   - Desmarque "Notificar pessoas"
   - Clique em "Compartilhar"

3. **Verificar abas:**
   - Planilha deve ter aba: `BASE_CONTROLE`
   - Planilha deve ter aba: `USUARIOS`

---

### 5. NÃO ALTERAR O CÓDIGO

**❌ NÃO ADICIONE:**
```python
app.run()  # Isso é Flask, não Streamlit!
```

**✅ O CÓDIGO JÁ ESTÁ CORRETO:**
```python
# Streamlit não precisa de app.run()
# O comando 'streamlit run app.py' já inicia o servidor
```

---

## 🚀 PASSO A PASSO COMPLETO

### Passo 1: Atualizar Start Command

```bash
# No Render Dashboard:
Settings → Build & Deploy → Start Command

# Substituir por:
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

---

### Passo 2: Verificar Variáveis de Ambiente

```bash
# No Render Dashboard:
Environment → Verificar:

SHEET_NAME = "Nome da Planilha"
GOOGLE_CREDENTIALS = {"type":"service_account",...}
```

---

### Passo 3: Compartilhar Planilha

```bash
# Google Sheets:
Compartilhar → Adicionar email do service account → Editor
```

---

### Passo 4: Fazer Deploy

```bash
# Opção A: Deploy automático (se já fez push)
# Render detecta mudanças no GitHub automaticamente

# Opção B: Deploy manual
# Render Dashboard → Manual Deploy → Deploy latest commit
```

---

### Passo 5: Aguardar Build

```
==> Building...
==> Installing dependencies from requirements.txt
==> Build successful

==> Starting service...
==> Running: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0

  You can now view your Streamlit app in your browser.

  Network URL: http://0.0.0.0:10000
  External URL: https://seu-app.onrender.com

==> Service is live! ✅
```

---

### Passo 6: Testar

```bash
# Acessar URL:
https://seu-app.onrender.com

# Deve aparecer:
- Tela de login do Streamlit
- Sistema de análise de crédito
```

---

## 🐛 TROUBLESHOOTING

### Erro: "Address already in use"

**Causa:** Porta fixa no comando
**Solução:** Usar `$PORT` em vez de `10000`

```bash
# ❌ Errado:
streamlit run app.py --server.port=10000

# ✅ Correto:
streamlit run app.py --server.port=$PORT
```

---

### Erro: "SHEET_NAME not found"

**Causa:** Variável de ambiente não configurada
**Solução:** 
1. Render → Environment
2. Adicionar `SHEET_NAME`
3. Redeploy

---

### Erro: "GOOGLE_CREDENTIALS invalid JSON"

**Causa:** JSON com quebras de linha ou incompleto
**Solução:**
1. Copiar JSON completo do arquivo
2. Remover quebras de linha
3. Colar em uma única linha
4. Verificar se tem todas as chaves

**Testar JSON localmente:**
```python
import json
creds = '{"type":"service_account",...}'
json.loads(creds)  # Deve funcionar sem erro
```

---

### Erro: "Permission denied" no Google Sheets

**Causa:** Planilha não compartilhada com service account
**Solução:**
1. Verificar email do service account no JSON
2. Compartilhar planilha com esse email
3. Permissão: Editor

---

### Erro: "Worksheet not found"

**Causa:** Abas com nomes incorretos
**Solução:**
1. Verificar se existe aba `BASE_CONTROLE`
2. Verificar se existe aba `USUARIOS`
3. Nomes devem ser exatos (case-sensitive)

---

### Erro: "Module not found"

**Causa:** Dependência faltando no requirements.txt
**Solução:**
1. Verificar requirements.txt
2. Adicionar módulo faltante
3. Commit e push
4. Redeploy

---

## 📋 CHECKLIST DE VERIFICAÇÃO

### Antes do Deploy
- [ ] Start Command correto no Render
- [ ] `SHEET_NAME` configurado
- [ ] `GOOGLE_CREDENTIALS` configurado (JSON completo)
- [ ] Planilha compartilhada com service account
- [ ] Abas `BASE_CONTROLE` e `USUARIOS` existem
- [ ] requirements.txt correto

### Durante o Deploy
- [ ] Build bem-sucedido
- [ ] "Installing dependencies" OK
- [ ] "Starting service" OK
- [ ] "Service is live" apareceu

### Após o Deploy
- [ ] URL acessível
- [ ] Tela de login aparece
- [ ] Login funciona
- [ ] Operações funcionam

---

## 🎯 CONFIGURAÇÃO COMPLETA DO RENDER

### Build & Deploy
```
Build Command: pip install -r requirements.txt
Start Command: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### Environment Variables
```
SHEET_NAME = "Nome da Planilha"
GOOGLE_CREDENTIALS = {"type":"service_account",...}
```

### Settings
```
Branch: main (ou master)
Auto-Deploy: Yes
```

---

## 📝 EXEMPLO COMPLETO

### 1. Configurar Render

**Settings → Build & Deploy:**
```
Build Command: pip install -r requirements.txt
Start Command: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**Environment:**
```
SHEET_NAME = "Sistema Credito Econsignado"
GOOGLE_CREDENTIALS = {"type":"service_account","project_id":"meu-projeto-123",...}
```

---

### 2. Compartilhar Planilha

```
Email: meu-app@meu-projeto-123.iam.gserviceaccount.com
Permissão: Editor
```

---

### 3. Deploy

```bash
# Manual Deploy ou aguardar auto-deploy
```

---

### 4. Verificar Logs

```
==> Build successful
==> Starting service...
==> You can now view your Streamlit app
==> Service is live!
```

---

### 5. Testar

```
https://meu-app.onrender.com
→ Tela de login ✅
→ Login funciona ✅
→ Sistema funciona ✅
```

---

## 🎉 RESUMO DAS CORREÇÕES

### O que estava errado:
❌ Start Command: `python app.py` (Flask)
❌ Tentando rodar Streamlit como Flask

### O que foi corrigido:
✅ Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
✅ Variáveis de ambiente configuradas
✅ Planilha compartilhada
✅ Código já estava correto (não precisa alterar)

### Resultado:
🚀 Sistema Streamlit funcionando no Render!

---

## 📞 SUPORTE

### Logs do Render
```
Render Dashboard → Logs
Procure por:
- "ERROR"
- "FAILED"
- "Permission denied"
```

### Testar Localmente
```bash
# Configurar variáveis de ambiente localmente
export SHEET_NAME="Nome da Planilha"
export GOOGLE_CREDENTIALS='{"type":"service_account",...}'

# Rodar localmente
streamlit run app.py

# Deve abrir em http://localhost:8501
```

---

**Pronto! Agora o deploy deve funcionar corretamente! 🎉**
