import streamlit as st
import pandas as pd
import sqlite3
from glob import glob
import os
from st_pages import Page, Section, show_pages, add_page_title

def clear_cache():
    globed = glob(r"cache/*")
    for i in globed:
        os.remove(i)
    open(r"cache/placeholder.txt", 'w').close()

pages_route = r'pages/'
assets_route = r'assets/'
show_pages([
    Page(f'wiki.py', 'Wiki', '📖'),
    Section('Apps', icon='💻'),
    Page(f'{pages_route}calculator.py', 'Calculator', '🧮', in_section=True),
    Page(f'{pages_route}plotter.py', 'Plotter', '📊', in_section=True)
])
st.sidebar.header("**THERMAL BALANCE CALCULATOR**")


def wiki_page():
    add_page_title()
    st.header("Title")
    st.markdown("Text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text")
    st.markdown("Text text text text text text text text text text text text text text text text text text")
    st.header("Title")
    st.markdown("Text text text text text text text text text text text text text text text text text text text text text text text text text text text text text")
    st.markdown("Text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text")
    st.header("Title")
    st.markdown("Text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text")
    st.markdown("Text text text text text text text text text text text text text text text text text text")
    st.header("Title")
    st.markdown("Text text text text text text text text text text text text text text text text text text text text text text text text text text text text text")
    st.markdown("Text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text")
    st.header("Title")
    st.markdown("Text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text")
    st.markdown("Text text text text text text text text text text text text text text text text text text")
    st.header("Title")
    st.markdown("Text text text text text text text text text text text text text text text text text text text text text text text text text text text text text")
    st.markdown("Text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text")
    st.header("Title")
    st.markdown("Text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text")
    st.markdown("Text text text text text text text text text text text text text text text text text text")
    st.header("Title")
    st.markdown("Text text text text text text text text text text text text text text text text text text text text text text text text text text text text text")
    st.markdown("Text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text text")


if __name__ == "__main__":
    clear_cache()
    wiki_page()