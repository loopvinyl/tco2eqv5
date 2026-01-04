# =========================
# IMPORTS
# =========================
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.signal import fftconvolve
import warnings

# =========================
# CONFIG STREAMLIT (TEM QUE SER PRIMEIRO)
# =========================
st.set_page_config(
    page_title="Simulador de Emissões CO₂eq",
    layout="wide"
)

# =========================
# CONFIG GERAL
# =========================
warnings.filterwarnings("ignore")
np.random.seed(50)
plt.rcParams["figure.dpi"] = 120

# =========================
# FUNÇÕES AUXILIARES
# =========================
def formatar_br(x):
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =========================
# SESSION STATE
# =========================
if "run_simulation" not in st.session_state:
    st.session_state.run_simulation = False

if "preco_carbono" not in st.session_state:
    st.session_state.preco_carbono = 85.50  # € fallback seguro

if "taxa_cambio" not in st.session_state:
    st.session_state.taxa_cambio = 5.50  # R$ fallback seguro

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("⚙️ Parâmetros")

    residuos_kg_dia = st.slider(
        "Resíduos (kg/dia)", 10, 1000, 100, 10
    )

    umidade_pct = st.slider(
        "Umidade (%)", 50, 90, 85
    )
    umidade = umidade_pct / 100

    anos_simulacao = st.slider(
        "Anos de simulação", 5, 30, 20
    )

    if st.button("🚀 Executar Simulação"):
        st.session_state.run_simulation = True

# =========================
# CONSTANTES
# =========================
T = 25
DOC = 0.15
MCF = 1
F = 0.5
OX = 0.1
k_ano = 0.06

GWP_CH4 = 79.7
GWP_N2O = 273

dias = anos_simulacao * 365
datas = pd.date_range(datetime.now().year, periods=dias, freq="D")

# =========================
# FUNÇÕES DE CÁLCULO
# =========================
def calcular_aterro(residuos):
    potencial = DOC * (0.0147 * T + 0.28) * MCF * F * (16 / 12) * (1 - OX)
    potencial_diario = residuos * potencial

    t = np.arange(1, dias + 1)
    kernel = np.exp(-k_ano * (t - 1) / 365) - np.exp(-k_ano * t / 365)
    ch4 = fftconvolve(np.ones(dias), kernel)[:dias] * potencial_diario

    n2o = np.full(dias, residuos * 0.000002)

    return ch4, n2o

def calcular_vermi(residuos):
    ch4 = np.full(dias, residuos * 0.00001)
    n2o = np.full(dias, residuos * 0.0000005)
    return ch4, n2o

# =========================
# TÍTULO
# =========================
st.title("🌱 Simulador de Emissões de tCO₂eq")

# =========================
# EXECUÇÃO
# =========================
if st.session_state.run_simulation:

    with st.spinner("Calculando..."):

        ch4_aterro, n2o_aterro = calcular_aterro(residuos_kg_dia)
        ch4_vermi, n2o_vermi = calcular_vermi(residuos_kg_dia)

        aterro_tco2 = (ch4_aterro * GWP_CH4 + n2o_aterro * GWP_N2O) / 1000
        vermi_tco2 = (ch4_vermi * GWP_CH4 + n2o_vermi * GWP_N2O) / 1000

        reducao = aterro_tco2.cumsum() - vermi_tco2.cumsum()

        total_evitado = reducao[-1]

    st.session_state.run_simulation = False

    # =========================
    # RESULTADOS
    # =========================
    st.subheader("📊 Resultados")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Emissões evitadas",
            f"{formatar_br(total_evitado)} tCO₂eq"
        )

    with col2:
        valor_eur = total_evitado * st.session_state.preco_carbono
        st.metric(
            "Valor (€)",
            f"€ {formatar_br(valor_eur)}"
        )

    with col3:
        valor_brl = valor_eur * st.session_state.taxa_cambio
        st.metric(
            "Valor (R$)",
            f"R$ {formatar_br(valor_brl)}"
        )

    # =========================
    # GRÁFICO
    # =========================
    fig, ax = plt.subplots()

    ax.plot(datas, reducao, label="Redução acumulada")
    ax.set_ylabel("tCO₂eq")
    ax.set_xlabel("Tempo")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)
