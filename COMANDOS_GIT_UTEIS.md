# 🔧 COMANDOS GIT ÚTEIS

## 📚 GUIA DE REFERÊNCIA RÁPIDA

### 🚀 DEPLOY BÁSICO

```bash
# Fluxo completo de deploy
git add .
git commit -m "feat: descrição da mudança"
git push origin main
```

---

## 📋 COMANDOS ESSENCIAIS

### Status e Informações

```bash
# Ver status dos arquivos
git status

# Ver histórico de commits
git log

# Ver histórico resumido
git log --oneline

# Ver últimos 5 commits
git log --oneline -5

# Ver diferenças não commitadas
git diff

# Ver diferenças de um arquivo específico
git diff app.py
```

---

### Adicionar Arquivos

```bash
# Adicionar arquivo específico
git add app.py

# Adicionar múltiplos arquivos
git add app.py requirements.txt

# Adicionar todos os arquivos modificados
git add .

# Adicionar apenas arquivos .py
git add *.py

# Adicionar apenas arquivos .md
git add *.md

# Ver o que será commitado
git status
```

---

### Commits

```bash
# Commit simples
git commit -m "mensagem"

# Commit com descrição detalhada
git commit -m "título" -m "descrição detalhada"

# Commit de todos os arquivos modificados (sem git add)
git commit -am "mensagem"

# Alterar mensagem do último commit (antes do push)
git commit --amend -m "nova mensagem"

# Adicionar arquivos ao último commit (antes do push)
git add arquivo_esquecido.py
git commit --amend --no-edit
```

---

### Push e Pull

```bash
# Push para branch main
git push origin main

# Push para branch master
git push origin master

# Push forçado (CUIDADO!)
git push origin main --force

# Pull (baixar mudanças do GitHub)
git pull origin main

# Pull com rebase
git pull --rebase origin main
```

---

## 🌿 BRANCHES

### Criar e Trocar

```bash
# Ver branches
git branch

# Criar nova branch
git branch feature/nova-funcionalidade

# Trocar para branch
git checkout feature/nova-funcionalidade

# Criar e trocar em um comando
git checkout -b feature/nova-funcionalidade

# Voltar para main
git checkout main
```

---

### Merge e Delete

```bash
# Fazer merge de branch para main
git checkout main
git merge feature/nova-funcionalidade

# Deletar branch local
git branch -d feature/nova-funcionalidade

# Deletar branch remota
git push origin --delete feature/nova-funcionalidade
```

---

## ⏪ DESFAZER MUDANÇAS

### Antes do Commit

```bash
# Descartar mudanças em arquivo específico
git checkout -- app.py

# Descartar todas as mudanças
git checkout -- .

# Remover arquivo do staging (após git add)
git reset HEAD app.py

# Remover todos os arquivos do staging
git reset HEAD
```

---

### Depois do Commit (Local)

```bash
# Desfazer último commit (mantém mudanças)
git reset --soft HEAD~1

# Desfazer último commit (descarta mudanças)
git reset --hard HEAD~1

# Desfazer últimos 3 commits
git reset --hard HEAD~3

# Voltar para commit específico
git reset --hard abc1234
```

---

### Depois do Push (Remoto)

```bash
# Reverter commit (cria novo commit)
git revert HEAD

# Reverter commit específico
git revert abc1234

# Reverter múltiplos commits
git revert HEAD~3..HEAD

# Push das reversões
git push origin main
```

---

## 🔍 INSPEÇÃO

### Ver Mudanças

```bash
# Ver mudanças de um commit
git show abc1234

# Ver arquivos alterados em um commit
git show --name-only abc1234

# Ver histórico de um arquivo
git log -- app.py

# Ver quem modificou cada linha
git blame app.py

# Buscar em commits
git log --grep="bug"

# Buscar por autor
git log --author="João"
```

---

## 🏷️ TAGS

### Criar e Gerenciar

```bash
# Criar tag
git tag v1.0.0

# Criar tag com mensagem
git tag -a v1.0.0 -m "Versão 1.0.0 - Sistema otimizado"

# Listar tags
git tag

# Push de tag específica
git push origin v1.0.0

# Push de todas as tags
git push origin --tags

# Deletar tag local
git tag -d v1.0.0

# Deletar tag remota
git push origin --delete v1.0.0
```

---

## 🔧 CONFIGURAÇÃO

### Configurar Git

```bash
# Configurar nome
git config --global user.name "Seu Nome"

# Configurar email
git config --global user.email "seu@email.com"

# Ver configurações
git config --list

# Configurar editor padrão
git config --global core.editor "code"

# Configurar cores
git config --global color.ui auto
```

---

## 📦 STASH (Guardar Mudanças Temporariamente)

```bash
# Guardar mudanças
git stash

# Guardar com mensagem
git stash save "trabalho em progresso"

# Listar stashes
git stash list

# Aplicar último stash
git stash apply

# Aplicar e remover último stash
git stash pop

# Aplicar stash específico
git stash apply stash@{0}

# Deletar último stash
git stash drop

# Deletar todos os stashes
git stash clear
```

---

## 🎯 CENÁRIOS COMUNS

### Cenário 1: Deploy Simples

```bash
# 1. Ver o que mudou
git status

# 2. Adicionar mudanças
git add app.py

# 3. Commit
git commit -m "feat: otimização de performance"

# 4. Push
git push origin main

# 5. Render faz deploy automático!
```

---

### Cenário 2: Corrigir Erro Após Push

```bash
# 1. Fazer correção no código
# 2. Commit da correção
git add app.py
git commit -m "fix: corrigir erro no cache"

# 3. Push
git push origin main
```

---

### Cenário 3: Trabalhar em Nova Funcionalidade

```bash
# 1. Criar branch
git checkout -b feature/notificacoes

# 2. Fazer mudanças e commits
git add .
git commit -m "feat: adicionar notificações por email"

# 3. Voltar para main
git checkout main

# 4. Fazer merge
git merge feature/notificacoes

# 5. Push
git push origin main

# 6. Deletar branch
git branch -d feature/notificacoes
```

---

### Cenário 4: Desfazer Deploy Problemático

```bash
# Opção A: Reverter (recomendado)
git revert HEAD
git push origin main

# Opção B: Reset (cuidado!)
git reset --hard HEAD~1
git push origin main --force
```

---

### Cenário 5: Atualizar do GitHub

```bash
# 1. Baixar mudanças
git pull origin main

# 2. Se houver conflitos, resolver manualmente
# 3. Commit da resolução
git add .
git commit -m "merge: resolver conflitos"

# 4. Push
git push origin main
```

---

## 🚨 EMERGÊNCIAS

### "Commitei arquivo errado!"

```bash
# Antes do push
git reset --soft HEAD~1
git reset HEAD arquivo_errado.py
git commit -m "mensagem correta"
git push origin main
```

---

### "Fiz push de credenciais!"

```bash
# 1. URGENTE: Revogar credenciais no Google Cloud
# 2. Remover do histórico (complexo, melhor criar novo repo)
# 3. Adicionar ao .gitignore
echo "credentials.json" >> .gitignore

# 4. Commit
git add .gitignore
git commit -m "chore: adicionar credentials ao gitignore"
git push origin main
```

---

### "Conflito de merge!"

```bash
# 1. Ver arquivos em conflito
git status

# 2. Abrir arquivo e resolver conflitos manualmente
# Procure por:
# <<<<<<< HEAD
# seu código
# =======
# código do GitHub
# >>>>>>> branch

# 3. Após resolver
git add arquivo_resolvido.py
git commit -m "merge: resolver conflitos"
git push origin main
```

---

### "Perdi minhas mudanças!"

```bash
# Se fez commit
git reflog
git checkout abc1234

# Se não fez commit
# Infelizmente, perdeu mesmo :(
# Sempre faça commits frequentes!
```

---

## 📝 MENSAGENS DE COMMIT

### Padrão Recomendado

```
tipo: descrição curta (máx 50 caracteres)

Descrição detalhada opcional (máx 72 caracteres por linha)

- Ponto 1
- Ponto 2
- Ponto 3
```

### Tipos Comuns

- **feat:** Nova funcionalidade
- **fix:** Correção de bug
- **docs:** Documentação
- **style:** Formatação
- **refactor:** Refatoração
- **perf:** Performance
- **test:** Testes
- **chore:** Manutenção

### Exemplos

```bash
# Bom ✅
git commit -m "feat: adicionar filtro por data no dashboard"
git commit -m "fix: corrigir erro ao finalizar CCB com anotações vazias"
git commit -m "perf: otimizar cache de usuários para 30 minutos"

# Ruim ❌
git commit -m "mudanças"
git commit -m "fix"
git commit -m "atualizações várias"
```

---

## 🎓 DICAS E BOAS PRÁTICAS

### Commits

✅ **Faça commits pequenos e frequentes**
```bash
git commit -m "feat: adicionar validação de CPF"
git commit -m "feat: adicionar validação de email"
git commit -m "test: adicionar testes de validação"
```

❌ **Evite commits gigantes**
```bash
git commit -m "adicionar várias funcionalidades e correções"
```

---

### Branches

✅ **Use branches para funcionalidades**
```bash
git checkout -b feature/nova-funcionalidade
# trabalhar...
git checkout main
git merge feature/nova-funcionalidade
```

❌ **Evite trabalhar direto na main**
```bash
# trabalhar direto na main
git commit -m "mudanças"
git push origin main
```

---

### Mensagens

✅ **Seja descritivo**
```bash
git commit -m "fix: corrigir erro de timeout ao carregar base com +1000 registros"
```

❌ **Evite mensagens vagas**
```bash
git commit -m "fix bug"
```

---

## 🔗 RECURSOS ÚTEIS

### Documentação
- [Git Docs](https://git-scm.com/doc)
- [GitHub Docs](https://docs.github.com/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

### Ferramentas
- [GitKraken](https://www.gitkraken.com/) - GUI para Git
- [GitHub Desktop](https://desktop.github.com/) - Cliente oficial
- [SourceTree](https://www.sourcetreeapp.com/) - GUI gratuita

### Tutoriais
- [Learn Git Branching](https://learngitbranching.js.org/)
- [Git Immersion](https://gitimmersion.com/)
- [Oh My Git!](https://ohmygit.org/) - Jogo para aprender Git

---

## 📞 AJUDA

### Comandos de Ajuda

```bash
# Ajuda geral
git help

# Ajuda de comando específico
git help commit
git help push
git help branch

# Versão do Git
git --version
```

---

## ✅ CHECKLIST DE DEPLOY

```bash
# 1. Verificar mudanças
git status
git diff

# 2. Adicionar arquivos
git add app.py requirements.txt

# 3. Commit
git commit -m "feat: descrição"

# 4. Verificar antes de push
git log --oneline -1

# 5. Push
git push origin main

# 6. Verificar no GitHub
# Abrir repositório no navegador

# 7. Aguardar deploy no Render
# Verificar logs no Render Dashboard

# 8. Testar em produção
# Acessar URL do app
```

---

**Salve este arquivo como referência rápida!** 📚

**Dica:** Use `Ctrl+F` para buscar comandos específicos
