from utils.plot import *
st.sidebar.header("**THERMAL BALANCE CALCULATOR**")

clear_cache()
clear_output()
add_page_title()

csv_file = st.file_uploader(label="Upload your result CSV", type="csv", accept_multiple_files=False)

notify_file = st.container()

st.title("")

if csv_file:
    try:
        dataframe = pd.read_csv(csv_file)
    except:
        notify_file.error("An error occured while reading the CSV file. Check your file format, name and content and try again", icon='⚠️')

    range_opt = st.selectbox(label="Coverage", options=["annual", "monthly"], index=0, placeholder="annual")

    with st.form("form_plotter", border=False):
        zones_in_df = dataframe["zone"].unique()
        zones_multiselect = st.multiselect(label="Zones", options=zones_in_df, placeholder="All Zones")
        type_opt = st.selectbox(label="Type", options=["convection", "surface"], index=0, placeholder="convection")
        
        col1, col2 = st.columns(2)

        use_tight = col1.checkbox(label="Tight layout")
        cbar_loc = col2.radio(label="Color bar location", options=["bottom", "right", "top", "left"], index=0, horizontal=True)
        months_selected = False

        if range_opt == 'monthly':
            months_on_df = dataframe['month'].unique()
            months_selected = st.multiselect(label="Months", options=months_on_df, placeholder="All year")
        
        st.title("")
        if st.form_submit_button(label='Create HeatMap'):
            zones_opt = 0 if not zones_multiselect else zones_multiselect
            months_opt = 0 if not months_selected else months_selected
            filename = csv_file.name.replace(".csv", "")
            notify_heatmap = st.container()
            try:
                new_heatmap = HeatMap(df=dataframe, target_type=type_opt, zones=zones_opt, months=months_opt, tight=use_tight, cbar_orientation=cbar_loc, filename=filename)
                if range_opt == 'annual':
                    new_heatmap.annual()
                elif range_opt == 'monthly':
                    new_heatmap.monthly()
                
                globed = glob("output/*.png")
                st.image(image=globed[0])
            except Exception as e:
                notify_heatmap.error(e, icon='⚠️')
