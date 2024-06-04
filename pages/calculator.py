from wiki import *

st.sidebar.header("**THERMAL BALANCE CALCULATOR**")
add_page_title()

st.warning("NOTICE: It is essential that the user reads the **manual** or **Wiki** before using this website, as **file formats and naming should be exactly as the manual says**", icon="💡")
st.title("")

col1, col2 = st.columns(2)
csv_file = col1.file_uploader("**Upload your CSV**", type="csv", accept_multiple_files=False,key='csv')
sql_file = col2.file_uploader("**Upload your SQL**", type="sql", accept_multiple_files=False,key='sql')
st.title("")


@contextmanager
def sqlite_connect(db_bytes):
    fp = Path(str(uuid4()))
    fp.write_bytes(db_bytes.getvalue())
    conn = sqlite3.connect(str(fp))

    try:
        yield conn
    finally:
        conn.close()
        fp.unlink()


if csv_file and sql_file:
    col1, col2, col3 = st.columns([1,1,0.4])
    if col2.button("Calculate"):
        st.title("")
        notify_sql = st.container()
        notify_csv = st.container()

        with st.spinner("Reading SQL"):
            try:
                connection = sqlite_connect(sql_file)
                notify_sql.success("Successfully processed the SQL", icon='🎉')
            except:
                notify_sql.error("An error occured while processing the SQL", icon='⚠️')

        progress_text = "Calculating Heat Exchange Index (deppending on the file size, this might take a while)"
        progress_bar = st.progress(0, text=progress_text)
        try:
            st.title("")
            df = pd.read_csv(csv_file)
            progress_bar.progress(60, text=progress_text)
            st.dataframe(df)
            progress_bar.progress(100, text="Finished")
            notify_csv.success("Successfully calculated the Heat Exchange Index", icon='🎉')
            progress_bar.empty()
        except:
            notify_csv.error("An error occured while processing the CSV", icon='⚠️')
