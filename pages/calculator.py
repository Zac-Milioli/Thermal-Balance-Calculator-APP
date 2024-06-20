from utils.calculate import *

clear_output_csv()
st.sidebar.header("**THERMAL BALANCE CALCULATOR**")
st.sidebar.divider()
st.sidebar.image(r"utils/lab_banner.png", width=300)
st.sidebar.subheader("")
add_page_title()

st.warning("NOTICE: It is essential that the user reads the **manual** or **Wiki** before using this website, as **file formats and naming should be exactly as the manual says**", icon="💡")
st.title("")

sql_file = st.file_uploader("**Upload your SQL**", type="sql", accept_multiple_files=False,key='sql')

with st.form("form_calculator", border=False, clear_on_submit=True):
    notify_sql = st.container()
    worked = False
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
        coverage_option = col3.selectbox(label="Choose a timestep", options=['annual', 'monthly', 'daily'], index=0, placeholder='annual')
        csv_file = st.file_uploader("**Upload your CSV**", type="csv", accept_multiple_files=False,key='csv')
        notify_csv = st.container()
        st.title("")
        col1, col2, col3 = st.columns(3)
        if col2.form_submit_button("Calculate", use_container_width=True):
            if not csv_file:
                notify_csv.error("You **must** insert a CSV file to calculate", icon='⚠️')
            else:
                progress_bar = st.progress(0, text="Seting up files (deppending on the files size, this might take a while)")
                use_zones = "All" if not zone_option else zone_option
                try:
                    df = pd.read_csv(csv_file)
                    generate_df(input_dataframe=df, filename=csv_file.name, way=type_option, type_name=f"_{type_option}_", coverage=coverage_option, zone=use_zones, pbar=progress_bar)
                    progress_bar.progress(100, "Done")
                    progress_bar.empty()
                except Exception as e:
                    notify_csv.error(f"The following error occured while processing the CSV: {e}", icon='⚠️')

globed = glob(f"{output_path}*.csv")
if len(globed) != 0:
    st.title('')
    with zipfile.ZipFile(r'cache/outputs.zip', 'w') as meu_zip:
        for csv_file in globed:
            meu_zip.write(csv_file, arcname=csv_file)
    col1, col2, col3 = st.columns(3)
    with open(r'cache/outputs.zip', 'rb') as f:
        bytes = f.read()
        col2.download_button(
            label="Download Dataframes",
            data=bytes,
            file_name='outputs.zip',
            mime='application/zip',
            use_container_width=True
        )

if len(globed) != 0:
    st.title("")
    st.caption("Dataframes Gallery:")
    with st.container(border=True):
        ncols = min(2, len(globed))
        cols = st.columns(ncols)
        for i, df in enumerate(globed):
            st.caption(df)
            cols[i % ncols].dataframe(pd.read_csv(df))