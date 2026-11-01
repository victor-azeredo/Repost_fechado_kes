import pandas as pd
import json
import os

caminho_entrada = r"C:\Users\joao\OneDrive\Desktop\SERVIDOR_ANALITICO\SERVIDOR_RELATORIOS_OLS\excel_book\Chamados agosto26_v2.xlsx"
caminho_saida = r"C:\Users\joao\OneDrive\Desktop\SERVIDOR_ANALITICO\CAIXA_DE_CORREIO\carga_banco.json"

def varrer_e_gerar_json(caminho_in, caminho_out):
   
    df = pd.read_excel(caminho_in, sheet_name='Caixa de Entrada')
    
    if 'Motivo' in df.columns:
        df = df.drop(columns=['Motivo'])
        
    df = df.where(pd.notnull(df), None)

    registros = df.to_dict(orient='records')
    
    pacote_json = json.dumps(registros, ensure_ascii=False, indent=4)
    
    os.makedirs(os.path.dirname(caminho_out), exist_ok=True)
    
    with open(caminho_out, 'w', encoding='utf-8') as f:
        f.write(pacote_json)
        
    return registros

# 2. Executando o motor de ingestão
lista_de_chamados = varrer_e_gerar_json(caminho_entrada, caminho_saida)

# 3. VERIFICAÇÃO VISUAL NO TERMINAL
print("\n=== SUCESSO! ARQUIVO JSON GERADO ===")
print(f"Total de chamados convertidos: {len(lista_de_chamados)}")
print(f"Salvo em: {caminho_saida}\n")
print("Prévia dos 2 primeiros chamados extraídos para sua conferência:")

# Imprime apenas os dois primeiros para não poluir a tela inteira
print(json.dumps(lista_de_chamados[:2], ensure_ascii=False, indent=4))