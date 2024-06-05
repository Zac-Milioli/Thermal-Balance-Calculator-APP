from utils.calculate import *

st.sidebar.header("**THERMAL BALANCE CALCULATOR**")
add_page_title()

st.warning("NOTICE: It is essential that the user reads the **manual** or **Wiki** before using this website, as **file formats and naming should be exactly as the manual says**", icon="💡")
st.title("")

sql_file = st.file_uploader("**Upload your SQL**", type="sql", accept_multiple_files=False,key='sql')

with st.form("form_calculator", border=False):
    worked = False
    notify_sql = st.container()
    if sql_file:
        try:
            with st.spinner("Reading SQL..."):
                zones_list = read_db_for_zones(connection=save_and_connect_sql(sql_file))
                worked = True
        except:
            notify_sql.error("An error occured while processing the SQL", icon='⚠️')
            st.stop()
        
    if worked:
        col1, col2, col3 = st.columns(3)
        zone_option = col1.multiselect(label="Pick the zones", options=zones_list, placeholder="All Zones")
        type_option = col2.selectbox(label="Select the type", options=['convection', 'surface'], index=0, placeholder='convection')
        coverage_option = col3.selectbox(label="Choose a coverage", options=['annual', 'monthly', 'daily'], index=0, placeholder='annual')
        csv_file = st.file_uploader("**Upload your CSV**", type="csv", accept_multiple_files=False,key='csv')
        notify_csv = st.container()
        col1, col2, col3 = st.columns([1,1,0.4])
        if col2.form_submit_button("Calculate"):
            if not csv_file:
                notify_csv.error("You **must** insert a CSV file to calculate", icon='⚠️')
            else:
                filename = csv_file.name
                progress_text = "Calculating Heat Exchange Index (deppending on the file size, this might take a while)"
                progress_bar = st.progress(0, text=progress_text)
                try:
                    df = pd.read_csv(csv_file)
                    progress_bar.progress(60, text=progress_text)
                    st.dataframe(df)
                    progress_bar.progress(100, text="Finished")
                    progress_bar.empty()
                except:
                    notify_csv.error("An error occured while processing the CSV", icon='⚠️')
