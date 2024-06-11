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
import warnings
warnings.filterwarnings('ignore')

def clear_cache():
    globed = glob(r"cache/*")
    for i in globed:
        os.remove(i)
    open(r"cache/placeholder.txt", 'w').close()


def clear_output():
    globed = glob(r"output/*.csv")
    for i in globed:
        os.remove(i)
    globed = glob(r"output/*.png")
    for i in globed:
        os.remove(i)

pages_route = r'pages/'

show_pages([
    Page(f'wiki.py', 'Wiki', '📖'),
    Section('Apps', icon='💻'),
    Page(f'{pages_route}calculator.py', 'Calculator', '🧮', in_section=True),
    Page(f'{pages_route}plotter.py', 'Plotter', '📊', in_section=True)
])