import math
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import io

# =====================================================================
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# =====================================================================
st.set_page_config(page_title="Análise de Isolamento IEEE 43", layout="wide")

# =====================================================================
# FUNÇÕES MATEMÁTICAS E FÍSICAS (Mantidas intactas)
# =====================================================================
def calcular_ponto_orvalho(temp, umidade):
    a = 17.27
    b = 237.3
    alpha = ((a * temp) / (b + temp)) + math.log(umidade / 100.0)
    ponto_orvalho = (b * alpha) / (a - alpha)
    return ponto_orvalho

def calcular_fator_correcao(temp_medicao):
    return 0.5 ** ((temp_medicao - 40) / 10)

def diagnostico_isolamento(res_1min_corrigida, pi):
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
# INTERFACE DO USUÁRIO STREAMLIT
# =====================================================================
st.title("⚡ Sistema de Análise de Isolamento de Motores")
st.markdown("**Norma Técnica IEEE 43** | Desenvolvido por: Milton Lucas Vasques Lopes")

with st.expander("📖 GUIA RÁPIDO DE REFERÊNCIA PARA O TÉCNICO"):
    st.markdown("""
    * **Ponto de Orvalho:** Se o motor estiver frio, a umidade do ar vira água nas bobinas. Isso mascara o teste, reprovando um motor que está bom.
    * **Fator Kt (40°C):** A resistência cai pela metade a cada 10°C. O sistema corrige a medição para 40°C para comparação histórica.
    * **Índice de Polarização (PI):** Mede a sujeira e umidade interna. PI < 1.5 = Bobina suja/úmida (risco). PI > 2.0 = Limpa e seca.
    """)

# Início do formulário de entrada
with st.form("formulario_medicao"):
    st.subheader("1. Dados Gerais")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        tag_motor = st.text_input("TAG do Motor").upper()
    with col2:
        temp_ambiente = st.number_input("Temp. Ambiente (°C)", value=25.0, step=0.5)
    with col3:
        umidade = st.number_input("Umidade Relativa (%)", value=50.0, step=1.0)
    with col4:
        temp_carcaca = st.number_input("Temp. da Carcaça (°C)", value=30.0, step=0.5)

    st.subheader("2. Leituras de Resistência (MΩ)")
    st.info("Deixe em 0 os testes que não forem realizados.")
    
    nomes_testes = [
        "Bobina 1 p/ Terra", "Bobina 2 p/ Terra", "Bobina 3 p/ Terra",
        "Bobina 1 p/ Bobina 2", "Bobina 1 p/ Bobina 3", "Bobina 2 p/ Bobina 3"
    ]
    
    dados_digitados = {}
    
    # Cria uma linha de inputs para cada teste usando abas para não poluir a tela
    abas = st.tabs(nomes_testes)
    
    for i, teste in enumerate(nomes_testes):
        with abas[i]:
            st.markdown(f"**Valores para: {teste}**")
            cols_min = st.columns(10)
            valores_teste = []
            for min in range(10):
                with cols_min[min]:
                    val = st.number_input(f"{min+1} min", min_value=0.0, value=0.0, step=10.0, key=f"{teste}_{min}")
                    valores_teste.append(val)
            dados_digitados[teste] = valores_teste

    # Botão para processar
    submit_button = st.form_submit_button("Gerar Análise e Relatório")

# =====================================================================
# PROCESSAMENTO DE DADOS E GERAÇÃO DO EXCEL
# =====================================================================
if submit_button:
    if tag_motor == "":
        st.error("Por favor, preencha o TAG do motor antes de gerar a análise.")
    else:
        # Cálculos Preliminares
        po = calcular_ponto_orvalho(temp_ambiente, umidade)
        kt = calcular_fator_correcao(temp_carcaca)
        margem = temp_carcaca - po 
        
        st.divider()
        st.subheader(f"📊 Resultado da Análise: {tag_motor}")
        
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Ponto de Orvalho", f"{po:.1f} °C")
        col_res2.metric("Margem de Segurança", f"{margem:.1f} °C", delta="Risco Condensação" if margem < 3 else "Seguro", delta_color="inverse")
        col_res3.metric("Fator Correção (Kt)", f"{kt:.3f}")

        resultados_resumo = []
        dados_grafico = {'Minutos': list(range(1, 11))}
        testes_realizados = False
        
        for teste, valores in dados_digitados.items():
            # Só processa se o usuário digitou algo além de zero no primeiro minuto
            if any(v > 0 for v in valores): 
                testes_realizados = True
                valores_corrigidos = [v * kt for v in valores]
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

        if not testes_realizados:
            st.warning("Nenhum dado de medição foi inserido. Insira os valores para gerar o relatório.")
        else:
            # Gráfico salvo na memória (BytesIO)
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
            
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            plt.close()

            # Dataframes
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

            # Excel salvo na memória (BytesIO)
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                workbook = writer.book
                worksheet_diag = workbook.add_worksheet('Diagnóstico')
                writer.sheets['Diagnóstico'] = worksheet_diag
                
                fmt_header = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#1F4E78', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
                fmt_title = workbook.add_format({'bold': True, 'font_color': '#1F4E78', 'font_size': 14})
                fmt_center = workbook.add_format({'align': 'center', 'border': 1})
                fmt_wrap = workbook.add_format({'text_wrap': True, 'valign': 'top', 'border': 1})
                fmt_excelente = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100', 'bold': True, 'border': 1, 'align': 'center'})
                fmt_alerta = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006', 'bold': True, 'border': 1, 'align': 'center'})

                worksheet_diag.hide_gridlines(2)
                worksheet_diag.write('A1', f'RELATÓRIO TÉCNICO DE ISOLAMENTO - {tag_motor}', fmt_title)
                
                for col_num, value in enumerate(info_geral.columns.tolist()):
                    worksheet_diag.write(2, col_num, value, fmt_header)
                    worksheet_diag.write(3, col_num, info_geral.iloc[0, col_num], fmt_center)

                worksheet_diag.write(5, 0, "RESULTADOS DOS ENSAIOS (CORRIGIDOS PARA 40°C)", fmt_title)
                for col_num, value in enumerate(df_resumo.columns.tolist()):
                    worksheet_diag.write(6, col_num, value, fmt_header)

                for row_num, row_data in enumerate(df_resumo.values):
                    for col_num, cell_value in enumerate(row_data):
                        current_fmt = fmt_center
                        if any(x in str(cell_value) for x in ["EXCELENTE", "Bom", "Seguro"]): current_fmt = fmt_excelente
                        if any(x in str(cell_value) for x in ["Alerta", "PERIGOSO", "Baixo", "Ignorado"]): current_fmt = fmt_alerta
                        worksheet_diag.write(row_num + 7, col_num, cell_value, current_fmt)

                # Inserindo a imagem a partir da memória
                worksheet_diag.insert_image('H1', 'grafico.png', {'image_data': img_buffer, 'x_scale': 0.75, 'y_scale': 0.75})

                start_g = 16
                worksheet_diag.write(start_g - 1, 0, "NOTAS TÉCNICAS", fmt_title)
                for row_num, row_data in enumerate(glossario_excel.values):
                    worksheet_diag.write(start_g + row_num, 0, row_data[0], fmt_header)
                    worksheet_diag.merge_range(start_g + row_num, 1, start_g + row_num, 5, row_data[1], fmt_wrap)

                worksheet_diag.set_column('A:F', 22)
                worksheet_diag.set_row(16, 25); worksheet_diag.set_row(17, 25); worksheet_diag.set_row(18, 25); worksheet_diag.set_row(19, 25)

                df_dados_completos.to_excel(writer, sheet_name='Dados Completos', index=False)
                writer.sheets['Dados Completos'].set_column('A:L', 15)

            st.success("Análise concluída com sucesso! Clique no botão abaixo para baixar a planilha.")
            
            # Botão de Download na tela do Streamlit
            st.download_button(
                label="📥 Baixar Relatório em Excel",
                data=excel_buffer.getvalue(),
                file_name=f"Relatorio_Isolamento_{tag_motor}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
