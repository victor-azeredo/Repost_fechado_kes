import sqlite3
import os

# ==========================================
# 1. MAPEAMENTO DE PASTAS
# ==========================================
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
PASTA_BANCO = os.path.join(DIRETORIO_ATUAL, '..', 'banco_local')
CAMINHO_BANCO = os.path.join(PASTA_BANCO, 'banco_kes.db') # Arquivo de banco exclusivo da KES

# ==========================================
# 2. FUNÇÃO DE CRIAÇÃO DO BANCO E TABELAS
# ==========================================
def inicializar_banco():
    if not os.path.exists(PASTA_BANCO):
        os.makedirs(PASTA_BANCO)

    conn = sqlite3.connect(CAMINHO_BANCO)
    cursor = conn.cursor()

    # --- TABELA 1: SERVICE DESK (CHAMADOS ITSM - KES) ---
    # Chave Primária: Número do chamado (Ex: INC2026001365)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chamados_itsm (
            chamado TEXT PRIMARY KEY,
            aprovadores INTEGER,
            tempo_resolucao TEXT,
            tempo_resposta TEXT,
            data_abertura TEXT,
            data_fechamento TEXT,
            data_resolucao TEXT,
            analista TEXT,
            nome_completo TEXT,
            prioridade TEXT,
            status TEXT,
            tipo_chamado TEXT,
            formulario TEXT,
            departamento TEXT,
            resumo TEXT,
            localizacao TEXT,
            categoria_original TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print(f"✅ Sucesso! Banco de dados KES gerado limpo e exclusivo em: {CAMINHO_BANCO}")

if __name__ == "__main__":
    inicializar_banco()