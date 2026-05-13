# ⚡ Motor Insulation Analysis System (IEEE 43) / Sistema de Análise de Isolamento de Motores

🇺🇸 **English**
This project automates the analysis of insulation resistance tests in electric motors, providing professional Excel reports and technical diagnostics based on international standards.

🇧🇷 **Português**
Este projeto automatiza a análise de testes de resistência de isolamento em motores elétricos, gerando relatórios profissionais em Excel e diagnósticos técnicos baseados em normas internacionais.

---

## 🎯 Process Impact / Impacto no Processo
*   **Padronização:** Elimina erros de cálculo manual de Kt e PI durante inspeções em campo.
*   **Confiabilidade:** O alerta de Ponto de Orvalho previne diagnósticos falsos negativos causados por condensação temporária.
*   **Histórico:** A geração automática de planilhas e gráficos facilita a análise de tendências de degradação do isolamento ao longo do tempo.

---

## 🛠 Features / Funcionalidades

*   🌡️ **Temperature Correction (Kt) / Correção de Temperatura (Kt):** Automatically normalizes measurements to 40°C base according to IEEE 43. / *Normaliza automaticamente as medições para a base de 40°C conforme a norma IEEE 43.*
*   💧 **Dew Point Calculation / Cálculo de Ponto de Orvalho:** Uses the Magnus-Tetens formula to alert about condensation risks. / *Utiliza a fórmula de Magnus-Tetens para alertar sobre riscos de condensação.*
*   ⚡ **Polarization Index (PI) / Índice de Polarização (PI):** Calculates and diagnoses the PI to evaluate winding contamination. / *Calcula e diagnostica o PI para avaliar a contaminação do enrolamento.*
*   📊 **Professional Dashboard / Dashboard Profissional:** Exports data to a formatted Excel file with logarithmic charts. / *Exporta os dados para um Excel formatado com gráficos logarítmicos.*

---

## 📚 Technical Standards / Normas Técnicas
*   **IEEE 43-2013:** Recommended Practice for Testing Insulation Resistance of Electric Machinery.

---

## 🚀 How to use / Como usar

**1. Install dependencies / Instale as dependências:**
```bash
pip install -r requirements.txt
