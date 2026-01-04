# app.py - Versão otimizada
import os
import sys
import time
import requests
from bs4 import BeautifulSoup
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import seaborn as sns
from scipy import stats
from scipy.signal import fftconvolve
from functools import lru_cache
import warnings
from matplotlib.ticker import FuncFormatter
from SALib.sample.sobol import sample
from SALib.analyze.sobol import analyze

# Configurações de compatibilidade
if not sys.warnoptions:
    warnings.simplefilter("ignore")
    
np.random.seed(50)

# Configurações iniciais do Streamlit
st.set_page_config(
    page_title="Simulador de Emissões CO₂eq", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações do pandas
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

# Configurações do matplotlib
plt.rcParams['figure.dpi'] = 150
plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

sns.set_style("whitegrid")

# Continuação do seu código...
