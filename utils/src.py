import streamlit as st
import pandas as pd
import sqlite3
from glob import glob
import os
from st_pages import Page, Section, show_pages, add_page_title
from datetime import datetime, timedelta
import numpy as np
import traceback
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import zipfile
import warnings
warnings.filterwarnings('ignore')

def clear_cache():
    globed = glob(r"cache/*.csv")
    for i in globed:
        os.remove(i)
    globed = glob(r"cache/*.png")
    for i in globed:
        os.remove(i)


def clear_output():
    globed = glob(r"output/*.csv")
    for i in globed:
        os.remove(i)
    globed = glob(r"output/*.png")
    for i in globed:
        os.remove(i)


def clear_output_csv():
    globed = glob(r"output/*.csv")
    for i in globed:
        os.remove(i)


pages_route = r'pages/'

show_pages([
    Page(f'wiki.py', 'Wiki', '📖'),
    Section('Apps', icon='💻'),
    Page(f'{pages_route}calculator.py', 'Calculadora', '🧮', in_section=True),
    Page(f'{pages_route}plotter.py', 'Plotar Dados', '📊', in_section=True)
])