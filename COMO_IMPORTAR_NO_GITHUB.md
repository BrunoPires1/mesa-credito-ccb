# 📤 COMO ENVIAR PARA O GITHUB

## 1️⃣ CRIAR REPOSITÓRIO NO GITHUB

1. Acesse: https://github.com/new
2. Preencha:
   - Nome: `mesa-credito` (ou outro nome)
   - Deixe público ou privado
   - **NÃO marque** nenhuma opção
3. Clique: `Create repository`
4. **Copie a URL** que aparece (exemplo: https://github.com/seu-usuario/mesa-credito.git)

---

## 2️⃣ ABRIR TERMINAL NA PASTA

**Windows:**
- Abra esta pasta no Explorador
- Clique com botão direito
- Selecione: `Git Bash Here` ou `Abrir no Terminal`

**Ou no VS Code:**
- Abra esta pasta
- Menu: Terminal → New Terminal
- Ou pressione: `Ctrl + '`

---

## 3️⃣ EXECUTAR COMANDOS

**Copie e cole cada comando (um por vez):**

```bash
git init
```
*Inicializa o Git*

```bash
git add .
```
*Adiciona todos os arquivos*

```bash
git commit -m "Sistema otimizado"
```
*Cria o commit*

```bash
git remote add origin SUA-URL-AQUI
```
*⚠️ SUBSTITUA "SUA-URL-AQUI" pela URL que você copiou!*

```bash
git push -u origin main
```
*Envia para o GitHub*

**Se der erro no último comando, tente:**
```bash
git push -u origin master
```

---

## 4️⃣ VERIFICAR NO GITHUB

1. Volte para o GitHub no navegador
2. Atualize a página (F5)
3. Deve aparecer:
   - ✅ app.py
   - ✅ requirements.txt
   - ✅ .gitignore

---

## 5️⃣ CONFIGURAR RENDER

### A) Start Command

1. Acesse: https://dashboard.render.com/
2. Vá no seu serviço
3. Settings → Build & Deploy
4. Start Command - Cole isto:
   ```
   streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```
5. Save Changes

### B) Variáveis de Ambiente

1. Environment → Add Environment Variable
2. Adicione:

**SHEET_NAME:**
```
Nome da sua planilha Google Sheets
```

**GOOGLE_CREDENTIALS:**
```
JSON completo do arquivo de credenciais
(Copie tudo, em uma única linha)
```

3. Save Changes

---

## 6️⃣ COMPARTILHAR PLANILHA

1. Abra o arquivo JSON de credenciais
2. Procure: `"client_email"`
3. Copie o email (exemplo: seu-app@projeto.iam.gserviceaccount.com)
4. Abra a planilha no Google Sheets
5. Compartilhar → Adicionar esse email → Permissão: Editor

---

## 7️⃣ FAZER DEPLOY

1. Render Dashboard
2. Manual Deploy → Deploy latest commit
3. Aguardar 2-3 minutos
4. Logs devem mostrar: "Service is live! ✅"

---

## 8️⃣ TESTAR

1. Acesse a URL do Render
2. Deve aparecer: Tela de login
3. Teste fazer login
4. Pronto! 🎉

---

## 🐛 ERROS COMUNS

### "git: command not found"
**Solução:** Instalar Git
- Baixe: https://git-scm.com/download/win
- Instale
- Reinicie o terminal

### "Permission denied"
**Solução:** Usar HTTPS
```bash
git remote set-url origin https://github.com/seu-usuario/seu-repo.git
git push -u origin main
```

### "Build failed" no Render
**Solução:** Verificar:
- Arquivos estão no GitHub?
- Start Command correto?
- Variáveis configuradas?

---

## ✅ CHECKLIST

- [ ] Repositório criado no GitHub
- [ ] Comandos executados
- [ ] Arquivos no GitHub
- [ ] Start Command configurado
- [ ] Variáveis adicionadas
- [ ] Planilha compartilhada
- [ ] Deploy feito
- [ ] Sistema funcionando

---

**Tempo total: ~15 minutos**
**Resultado: Sistema funcionando! 🚀**
