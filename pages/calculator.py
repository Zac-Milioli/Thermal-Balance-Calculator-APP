from utils.calculate import *

clear_output()
st.sidebar.header("**THERMAL BALANCE CALCULATOR**")
add_page_title()

st.warning("NOTICE: It is essential that the user reads the **manual** or **Wiki** before using this website, as **file formats and naming should be exactly as the manual says**", icon="💡")
st.title("")

sql_file = st.file_uploader("**Upload your SQL**", type="sql", accept_multiple_files=False,key='sql')

with st.form("form_calculator", border=False, clear_on_submit=True):
    st.session_state['form_filled'] = False
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
        coverage_option = col3.selectbox(label="Choose a coverage", options=['annual', 'monthly', 'daily'], index=0, placeholder='annual')
        csv_file = st.file_uploader("**Upload your CSV**", type="csv", accept_multiple_files=False,key='csv')
        notify_csv = st.container()
        col1, col2, col3 = st.columns([1,1,0.4])
        if col2.form_submit_button("Calculate"):
            if not csv_file:
                notify_csv.error("You **must** insert a CSV file to calculate", icon='⚠️')
            else:
                progress_bar = st.progress(0, text="Seting up files (deppending on the files size, this might take a while)")
                use_zones = "All" if not zone_option else zone_option
                try:
                    df = pd.read_csv(csv_file)
                    generate_df(input_dataframe=df, filename=csv_file.name, way=type_option, type_name=f"_{type_option}_", coverage=coverage_option, zone=use_zones, pbar=progress_bar)
                    progress_bar.progress(100, "Done")
                    globed = glob(f"{output_path}*.csv")
                    st.title('')
                    # if len(globed) == 1:    
                    #     df = pd.read_csv(globed[0])
                    #     st.caption(globed[0].split('\\')[-1])
                    #     st.dataframe(df)
                    # else:
                    #     df1 = pd.read_csv(globed[0])
                    #     df2 = pd.read_csv(globed[1])
                    #     df3 = pd.read_csv(globed[2])
                    #     df4 = pd.read_csv(globed[3])
                    #     col1, col2 = st.columns(2)
                    #     col1.caption(globed[0].split('\\')[-1])
                    #     col1.dataframe(df1, height=250)
                    #     col2.caption(globed[1].split('\\')[-1])
                    #     col2.dataframe(df2, height=250)
                    #     col1.caption(globed[2].split('\\')[-1])
                    #     col1.dataframe(df3, height=250)
                    #     col2.caption(globed[3].split('\\')[-1])
                    #     col2.dataframe(df4, height=250)
                    progress_bar.empty()
                    st.session_state['form_filled'] = True
                except Exception as e:
                    notify_csv.error(f"An error occured while processing the CSV ({e})", icon='⚠️')

if st.session_state['form_filled']:
    with zipfile.ZipFile(r'cache/outputs.zip', 'w') as meu_zip:
        for csv_file in globed:
            meu_zip.write(csv_file, arcname=csv_file)

    with open(r'cache/outputs.zip', 'rb') as f:
        bytes = f.read()
        st.download_button(
            label="Download outputs",
            data=bytes,
            file_name='outputs.zip',
            mime='application/zip'
        )