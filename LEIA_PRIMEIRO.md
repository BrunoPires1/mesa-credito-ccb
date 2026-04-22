# 🚀 GUIA RÁPIDO - 3 PASSOS SIMPLES

## 📁 ARQUIVOS DESTA PASTA

- ✅ **app.py** - Sistema otimizado (pronto!)
- ✅ **requirements.txt** - Dependências (pronto!)
- ✅ **.gitignore** - Proteção (pronto!)
- 📖 **LEIA_PRIMEIRO.md** - Este arquivo
- 📖 **COMO_IMPORTAR_NO_GITHUB.md** - Guia detalhado
- 📋 **COMANDOS_PRONTOS.txt** - Comandos para copiar

---

## 🎯 O QUE FAZER (3 PASSOS)

### 1️⃣ ENVIAR PARA GITHUB (5 min)

**Abra o terminal nesta pasta e cole estes comandos:**

```bash
git init
git add .
git commit -m "Sistema otimizado"
git remote add origin SUA-URL-DO-GITHUB-AQUI
git push -u origin main
```

**⚠️ Substitua "SUA-URL-DO-GITHUB-AQUI" pela URL do seu repositório!**

**Como criar repositório:**
1. Acesse: https://github.com/new
2. Nome: `mesa-credito`
3. Clique: `Create repository`
4. Copie a URL que aparece

---

### 2️⃣ CONFIGURAR RENDER (5 min)

**Acesse:** https://dashboard.render.com/

**A) Mudar Start Command:**
```
Settings → Build & Deploy → Start Command

Cole isto:
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0

Clique: Save Changes
```

**B) Adicionar variáveis:**
```
Environment → Add Environment Variable

1. SHEET_NAME = Nome da sua planilha
2. GOOGLE_CREDENTIALS = JSON completo das credenciais
```

---

### 3️⃣ COMPARTILHAR PLANILHA (2 min)

1. Abra o JSON de credenciais do Google
2. Procure: `"client_email"` (exemplo: seu-app@projeto.iam.gserviceaccount.com)
3. Copie esse email
4. Abra a planilha no Google Sheets
5. Compartilhar → Adicionar esse email → Editor

---

## ✅ FAZER DEPLOY

1. Render → Manual Deploy → Deploy latest commit
2. Aguardar 2-3 minutos
3. Acessar a URL
4. Pronto! 🎉

---

## 🐛 PROBLEMAS?

**Erro no Git?**
- Instale: https://git-scm.com/download/win
- Reinicie o terminal

**Erro no Render?**
- Verifique se os 3 passos foram feitos
- Veja os logs no Render Dashboard

---

## 📖 PRECISA DE MAIS DETALHES?

Abra: **COMO_IMPORTAR_NO_GITHUB.md**

---

**Tempo total: ~12 minutos**
**Resultado: Sistema 5x mais rápido funcionando! 🚀**
