"""
Script para migrar senhas antigas (texto plano) para senhas criptografadas (bcrypt)

ATENÇÃO: Execute este script APENAS UMA VEZ após fazer o deploy do novo sistema!

Como usar:
1. Configure as variáveis de ambiente SHEET_NAME e GOOGLE_CREDENTIALS
2. Execute: python migrar_senhas.py
3. O script irá:
   - Ler todas as senhas da planilha
   - Identificar senhas em texto plano
   - Criptografá-las com bcrypt
   - Atualizar a planilha
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import bcrypt

def hash_senha(senha):
    """Criptografa senha usando bcrypt"""
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def is_bcrypt_hash(senha):
    """Verifica se a senha já está em formato bcrypt"""
    return senha.startswith('$2b$') or senha.startswith('$2a$') or senha.startswith('$2y$')

def migrar_senhas():
    """Migra senhas de texto plano para bcrypt"""
    
    print("🔐 Iniciando migração de senhas...")
    
    # Configurações
    SHEET_NAME = os.environ.get("SHEET_NAME", "")
    google_creds_str = os.environ.get("GOOGLE_CREDENTIALS", "{}")
    
    if not SHEET_NAME or google_creds_str == "{}":
        print("❌ ERRO: Configure as variáveis de ambiente SHEET_NAME e GOOGLE_CREDENTIALS")
        return
    
    try:
        google_creds = json.loads(google_creds_str)
    except json.JSONDecodeError:
        print("❌ ERRO: GOOGLE_CREDENTIALS inválido")
        return
    
    # Conectar ao Google Sheets
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)
        client = gspread.authorize(creds)
        planilha = client.open(SHEET_NAME)
        sheet_usuarios = planilha.worksheet("USUARIOS")
        print("✅ Conectado ao Google Sheets")
    except Exception as e:
        print(f"❌ ERRO ao conectar: {e}")
        return
    
    # Carregar usuários
    try:
        dados = sheet_usuarios.get_all_values()
        print(f"📊 Encontrados {len(dados) - 1} usuários")
    except Exception as e:
        print(f"❌ ERRO ao carregar usuários: {e}")
        return
    
    if len(dados) <= 1:
        print("⚠️ Nenhum usuário encontrado")
        return
    
    # Processar cada usuário
    usuarios_migrados = 0
    usuarios_ja_criptografados = 0
    
    for idx, linha in enumerate(dados[1:], start=2):
        if len(linha) < 3:
            continue
        
        usuario = linha[0]
        senha = linha[1]
        perfil = linha[2]
        
        # Verifica se já está criptografada
        if is_bcrypt_hash(senha):
            print(f"✓ {usuario}: Senha já criptografada")
            usuarios_ja_criptografados += 1
            continue
        
        # Criptografa a senha
        try:
            senha_hash = hash_senha(senha)
            
            # Atualiza na planilha
            sheet_usuarios.update(f'B{idx}', [[senha_hash]])
            
            print(f"✅ {usuario}: Senha migrada com sucesso")
            usuarios_migrados += 1
            
        except Exception as e:
            print(f"❌ ERRO ao migrar {usuario}: {e}")
    
    # Resumo
    print("\n" + "="*50)
    print("📊 RESUMO DA MIGRAÇÃO")
    print("="*50)
    print(f"✅ Usuários migrados: {usuarios_migrados}")
    print(f"✓ Usuários já criptografados: {usuarios_ja_criptografados}")
    print(f"📊 Total de usuários: {len(dados) - 1}")
    print("="*50)
    
    if usuarios_migrados > 0:
        print("\n🎉 Migração concluída com sucesso!")
        print("⚠️ IMPORTANTE: Informe aos usuários que as senhas continuam as mesmas")
        print("   (o sistema detecta automaticamente o formato)")
    else:
        print("\n✓ Nenhuma migração necessária (todas as senhas já estão criptografadas)")

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           SCRIPT DE MIGRAÇÃO DE SENHAS                       ║
║                                                              ║
║  Este script irá criptografar todas as senhas em texto      ║
║  plano usando bcrypt.                                        ║
║                                                              ║
║  ATENÇÃO: Execute apenas UMA VEZ!                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    resposta = input("\n⚠️ Deseja continuar? (sim/não): ").strip().lower()
    
    if resposta in ['sim', 's', 'yes', 'y']:
        migrar_senhas()
    else:
        print("❌ Migração cancelada")
