import math
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# =====================================================================
# INFORMAÇÕES DO DESENVOLVEDOR E CRÉDITOS
# =====================================================================
DEV_INFO = """
=====================================================================
          SISTEMA DE ANÁLISE DE ISOLAMENTO DE MOTORES
                 NORMA TÉCNICA IEEE 43
=====================================================================
Desenvolvido por: Milton Lucas Vasques Lopes
Qualificação: Graduando em Engenharia de Controle e Automação
Contato: (19) 99923-4083
Poços de Caldas - MG
=====================================================================
"""

def exibir_guia_rapido():
    """Exibe um resumo explicativo para guiar os técnicos em campo."""
    print("\n" + "="*69)
    print(" 📖 GUIA RÁPIDO DE REFERÊNCIA PARA O TÉCNICO")
    print("="*69)
    print("• Ponto de Orvalho: Se o motor estiver frio (próximo à temperatura")
    print("  do ponto de orvalho), a umidade do ar vira água nas bobinas.")
    print("  Isso mascara o teste, reprovando um motor que está bom.")
    print("• Fator Kt (40°C): A resistência cai pela metade a cada 10°C.")
    print("  O sistema corrige a medição para 40°C para podermos comparar")
    print("  o teste de hoje com os testes do mês ou ano passado.")
    print("• Índice de Polarização (PI): Mede a sujeira e umidade interna.")
    print("  PI < 1.5 = Bobina suja/úmida (risco). PI > 2.0 = Limpa e seca.")
    print("="*69 + "\n")

# =====================================================================
# FUNÇÕES MATEMÁTICAS E FÍSICAS
# =====================================================================

def calcular_ponto_orvalho(temp, umidade):
    """Calcula o ponto de orvalho usando a fórmula de Magnus-Tetens."""
    a = 17.27
    b = 237.3
    alpha = ((a * temp) / (b + temp)) + math.log(umidade / 100.0)
    ponto_orvalho = (b * alpha) / (a - alpha)
    return ponto_orvalho

def calcular_fator_correcao(temp_medicao):
    """Calcula o Fator de Correção (Kt) para a temperatura padrão de 40°C (IEEE 43)."""
    return 0.5 ** ((temp_medicao - 40) / 10)

def diagnostico_isolamento(res_1min_corrigida, pi):
    """Retorna o diagnóstico da saúde do isolamento."""
    if res_1min_corrigida > 5000:
        status_pi = "PI Ignorado (Resistência > 5000 MΩ - Excelente)"
    elif pi < 1.5:
        status_pi = "Alerta: PI Baixo (< 1.5)"
    elif 1.5 <= pi <= 2.0:
        status_pi = "PI Regular (1.5 a 2.0)"
    else:
        status_pi = "PI Bom/Excelente (> 2.0)"

    if res_1min_corrigida < 5:
        status_res = "PERIGOSO (< 5 MΩ)"
    elif res_1min_corrigida < 100:
        status_res = "REGULAR (5 a 100 MΩ)"
    elif res_1min_corrigida < 500:
        status_res = "BOM (100 a 500 MΩ)"
    else:
        status_res = "EXCELENTE (> 500 MΩ)"
        
    return status_res, status_pi

# =====================================================================
# FUNÇÕES DE ENTRADA DE DADOS
# =====================================================================

def obter_numero_valido(mensagem):
    while True:
        entrada = input(mensagem)
        entrada = entrada.replace(',', '.')
        try:
            return float(entrada)
        except ValueError:
            print("   ❌ Erro: Entrada inválida. Digite apenas números.")

# =====================================================================
# PROGRAMA PRINCIPAL
# =====================================================================

def main():
    print(DEV_INFO)
    exibir_guia_rapido()
    
    # 1. Coleta de Dados Gerais
    tag_motor = input(">> Digite o TAG do Motor: ").upper()
    temp_ambiente = obter_numero_valido(">> Temperatura AMBIENTE (°C): ")
    umidade = obter_numero_valido(">> Umidade Relativa do ar (%): ")
    temp_carcaca = obter_numero_valido(">> Temperatura da CARCAÇA do motor (°C): ")
    
    po = calcular_ponto_orvalho(temp_ambiente, umidade)
    kt = calcular_fator_correcao(temp_carcaca)
    margem = temp_carcaca - po 
    
    print("\n" + "-"*69)
    print(f"ANÁLISE PRELIMINAR - TAG: {tag_motor}")
    print(f"Ponto de Orvalho: {po:.1f}°C")
    print(f"Temperatura da Carcaça: {temp_carcaca}°C")
    
    if margem < 3:
        print(f"⚠️  ALERTA: Risco de condensação! A carcaça está apenas {margem:.1f}°C acima")
        print(f"    do ponto de orvalho (mínimo exigido é 3°C). A umidade pode")
        print(f"    condensar no bobinado e mascarar o teste com valores baixos falsos.")
    else:
        print(f"✅ Condição segura para teste. Margem: {margem:.1f}°C (mínimo é 3°C).")
        
    print(f"Fator de Correção (Kt 40°C): {kt:.3f} (Multiplicador de correção)")
    print("-" * 69 + "\n")

    nomes_testes = [
        "Bobina 1 p/ Terra", "Bobina 2 p/ Terra", "Bobina 3 p/ Terra",
        "Bobina 1 p/ Bobina 2", "Bobina 1 p/ Bobina 3", "Bobina 2 p/ Bobina 3"
    ]
    
    resultados_resumo = []
    dados_grafico = {'Minutos': list(range(1, 11))}
    
    print("--- INÍCIO DAS MEDIÇÕES ---")
    
    for teste in nomes_testes:
        resposta = input(f"\nRealizar teste [{teste}]? (S/N): ").strip().upper()
        
        if resposta != 'S':
            print(f"⏭️  Teste [{teste}] ignorado.")
            continue 
            
        print(f"Insira os valores em MΩ para [{teste}]:")
        valores_medidos = []
        
        for minuto in range(1, 11):
            valor = obter_numero_valido(f"   Minuto {minuto}: ")
            valores_medidos.append(valor)
            
        valores_corrigidos = [v * kt for v in valores_medidos]
        res_1min = valores_corrigidos[0]
        res_10min = valores_corrigidos[9]
        
        pi = (res_10min / res_1min) if res_1min > 0 else 0
        status_res, status_pi = diagnostico_isolamento(res_1min, pi)
        
        resultados_resumo.append({
            "Teste": teste,
            "Resistência 1min (40°C) MΩ": round(res_1min, 2),
            "Resistência 10min (40°C) MΩ": round(res_10min, 2),
            "Índice de Polarização (PI)": round(pi, 2),
            "Diagnóstico Isolamento": status_res,
            "Diagnóstico PI": status_pi
        })
        
        dados_grafico[f"{teste} (Corrigido)"] = valores_corrigidos

    if not resultados_resumo:
        print("\nNenhum teste foi realizado. Encerrando.")
        input("\nPressione Enter para sair...")
        return

    # Processamento de Arquivos
    print("\n⏳ Gerando gráfico e relatório profissional...")

    # Gráfico
    plt.figure(figsize=(10, 6))
    for teste, valores in dados_grafico.items():
        if teste != 'Minutos':
            plt.plot(dados_grafico['Minutos'], valores, marker='o', label=teste)
            
    plt.title(f"Curva de Resistência de Isolamento (40°C) - {tag_motor}")
    plt.xlabel("Tempo (Minutos)")
    plt.ylabel("Resistência (MΩ)")
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend()
    plt.yscale('log') 
    
    nome_imagem = f"Grafico_temp_{tag_motor}.png"
    plt.savefig(nome_imagem, dpi=300, bbox_inches='tight')
    plt.close()

    data_atual = datetime.now().strftime("%Y%m%d_%H%M")
    nome_excel = f"Relatorio_Isolamento_{tag_motor}_{data_atual}.xlsx"
    
    df_resumo = pd.DataFrame(resultados_resumo)
    df_dados_completos = pd.DataFrame(dados_grafico)
    
    info_geral = pd.DataFrame([{
        "TAG": tag_motor,
        "Responsável": "Milton Lucas Vasques Lopes",
        "Temp. Ambiente (°C)": temp_ambiente,
        "Umidade (%)": umidade,
        "Temp. Carcaça (°C)": temp_carcaca,
        "Fator Correção (Kt)": round(kt, 3),
        "Data do Teste": datetime.now().strftime("%d/%m/%Y %H:%M")
    }])

    glossario_excel = pd.DataFrame([
        {"Termo": "Ponto de Orvalho", "Definição": "Temperatura na qual a umidade do ar condensa. Se a carcaça estiver abaixo do PO + 3°C, há risco de falsa leitura."},
        {"Termo": "Fator Kt", "Definição": "Normaliza a medição para 40°C. Permite comparação histórica independente da temperatura atual."},
        {"Termo": "Índice PI", "Definição": "Razão 10min/1min. Avalia contaminação interna. Valores < 1.5 indicam necessidade de limpeza."},
        {"Termo": "Resistência", "Definição": "Integridade física do isolamento. Valores < 5 MΩ representam risco iminente de queima."}
    ])

    with pd.ExcelWriter(nome_excel, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet_diag = workbook.add_worksheet('Diagnóstico')
        writer.sheets['Diagnóstico'] = worksheet_diag
        
        # Estilos do Dashboard
        fmt_header = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#1F4E78', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        fmt_title = workbook.add_format({'bold': True, 'font_color': '#1F4E78', 'font_size': 14})
        fmt_center = workbook.add_format({'align': 'center', 'border': 1})
        fmt_wrap = workbook.add_format({'text_wrap': True, 'valign': 'top', 'border': 1})
        fmt_excelente = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100', 'bold': True, 'border': 1, 'align': 'center'})
        fmt_alerta = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006', 'bold': True, 'border': 1, 'align': 'center'})

        # Layout da Planilha
        worksheet_diag.hide_gridlines(2)
        worksheet_diag.write('A1', f'RELATÓRIO TÉCNICO DE ISOLAMENTO - {tag_motor}', fmt_title)
        
        # Info Geral
        for col_num, value in enumerate(info_geral.columns.tolist()):
            worksheet_diag.write(2, col_num, value, fmt_header)
            worksheet_diag.write(3, col_num, info_geral.iloc[0, col_num], fmt_center)

        # Resumo dos Testes
        worksheet_diag.write(5, 0, "RESULTADOS DOS ENSAIOS (CORRIGIDOS PARA 40°C)", fmt_title)
        for col_num, value in enumerate(df_resumo.columns.tolist()):
            worksheet_diag.write(6, col_num, value, fmt_header)

        for row_num, row_data in enumerate(df_resumo.values):
            for col_num, cell_value in enumerate(row_data):
                current_fmt = fmt_center
                if any(x in str(cell_value) for x in ["EXCELENTE", "Bom"]): current_fmt = fmt_excelente
                if any(x in str(cell_value) for x in ["Alerta", "PERIGOSO", "Baixo"]): current_fmt = fmt_alerta
                worksheet_diag.write(row_num + 7, col_num, cell_value, current_fmt)

        # Inserção do Gráfico
        worksheet_diag.insert_image('H1', nome_imagem, {'x_scale': 0.75, 'y_scale': 0.75})

        # Glossário
        start_g = 16
        worksheet_diag.write(start_g - 1, 0, "NOTAS TÉCNICAS", fmt_title)
        for row_num, row_data in enumerate(glossario_excel.values):
            worksheet_diag.write(start_g + row_num, 0, row_data[0], fmt_header)
            worksheet_diag.merge_range(start_g + row_num, 1, start_g + row_num, 5, row_data[1], fmt_wrap)

        # Ajuste de Colunas
        worksheet_diag.set_column('A:F', 22)
        worksheet_diag.set_row(16, 25); worksheet_diag.set_row(17, 25); worksheet_diag.set_row(18, 25); worksheet_diag.set_row(19, 25)

        # Aba de Dados Completos
        df_dados_completos.to_excel(writer, sheet_name='Dados Completos', index=False)
        writer.sheets['Dados Completos'].set_column('A:L', 15)

    if os.path.exists(nome_imagem):
        os.remove(nome_imagem)
    
    print(f"\n✅ SUCESSO: {nome_excel} gerado.")
    print("=====================================================================")
    print(" Obrigado por utilizar o sistema de análise.")
    print("=====================================================================")
    input("\nPressione [ENTER] para encerrar o programa...")

if __name__ == "__main__":
    main()