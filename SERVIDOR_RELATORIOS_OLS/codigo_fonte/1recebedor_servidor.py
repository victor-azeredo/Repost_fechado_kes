import os
import time
import json
import sqlite3

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))

CAIXA_DE_CORREIO = os.path.abspath(os.path.join(DIRETORIO_ATUAL, '..', '..', 'CAIXA_DE_CORREIO'))

CAMINHO_BANCO = os.path.abspath(os.path.join(DIRETORIO_ATUAL, '..', 'banco_local', 'relatorios.db'))

# Garante que a infraestrutura física exista
os.makedirs(CAIXA_DE_CORREIO, exist_ok=True)
os.makedirs(os.path.dirname(CAMINHO_BANCO), exist_ok=True)

# ==========================================
# 2. MÓDULO DE INSERÇÃO (Banco de Dados)
# ==========================================
def inserir_chamados_itsm(cursor, lista_chamados):
    for chamado in lista_chamados:
        # INSERT OR REPLACE garante que chamados atualizados sobrescrevam os antigos
        cursor.execute('''
            INSERT OR REPLACE INTO chamados_itsm (
                chamado, aprovadores, tempo_resolucao, tempo_resposta, data_abertura,
                data_fechamento, data_resolucao, analista, nome_completo, prioridade,
                status, tipo_chamado, formulario, departamento, resumo, localizacao,
                categoria_original
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            chamado.get("Chamado"), 
            chamado.get("Aprovadores"), 
            chamado.get("Tempo de Resolução"), 
            chamado.get("Tempo de Resposta"), 
            chamado.get("Data Abertura"), 
            chamado.get("Data Fechamento"), 
            chamado.get("Data de Resolução"), 
            chamado.get("Analista"), 
            chamado.get("Nome completo"), 
            chamado.get("Prioridade"), 
            chamado.get("Status"), 
            chamado.get("Tipo chamado"), 
            chamado.get("Formulário"), 
            chamado.get("Departamento"), 
            chamado.get("Resumo"), 
            chamado.get("Localização"), 
            chamado.get("Categoria Original")
        ))

# ==========================================
# 3. O PROCESSADOR DA CAIXA DE CORREIO
# ==========================================
def varrer_caixa_de_correio():
    arquivos = os.listdir(CAIXA_DE_CORREIO)
    arquivos_json = [f for f in arquivos if f.endswith('.json')]

    if not arquivos_json:
        return # Caixa vazia, continua aguardando

    print(f"📥 Encontrados {len(arquivos_json)} pacotes de dados. Processando...")

    # Abre a conexão com o Banco de Dados KES
    conn = sqlite3.connect(CAMINHO_BANCO)
    cursor = conn.cursor()

    for arquivo_json in arquivos_json:
        caminho_json = os.path.join(CAIXA_DE_CORREIO, arquivo_json)
        
        try:
            # 1. Lê a lista de chamados do arquivo JSON
            with open(caminho_json, 'r', encoding='utf-8') as f:
                dados_chamados = json.load(f)

            # 2. Executa a inserção em lote
            inserir_chamados_itsm(cursor, dados_chamados)

            # 3. Sucesso! Confirma as alterações no banco e apaga o JSON processado
            conn.commit()
            os.remove(caminho_json)
            print(f"✅ Pacote '{arquivo_json}' processado. {len(dados_chamados)} chamados registrados no banco!")

        except Exception as e:
            conn.rollback() # Se der erro, desfaz a transação atual para não corromper o banco
            print(f"❌ Erro ao processar o pacote {arquivo_json}: {e}")

    # Fecha a conexão com o banco
    conn.close()

# ==========================================
# 4. O LOOP DE TRABALHO 24H
# ==========================================
if __name__ == "__main__":
    print("📡 Servidor Analítico KES Iniciado. Monitorando a Caixa de Correio...")
    while True:
        varrer_caixa_de_correio()
        time.sleep(100) # Checa a pasta a cada 5 segundos