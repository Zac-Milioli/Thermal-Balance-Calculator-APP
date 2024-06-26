from utils.plot import *

st.sidebar.write('')
st.sidebar.header("**THERMAL BALANCE CALCULATOR**")
st.sidebar.divider()
st.sidebar.image(r"utils/lab_banner.png", width=300)

clear_cache()
clear_output_csv()
add_page_title()

col1, col2, col3 = st.columns(3)
if col2.button(label="Clear gallery", use_container_width=True):
    clear_output()
st.title("")

csv_file = st.file_uploader(label="Upload your result CSV", type="csv", accept_multiple_files=False)

notify_file = st.container()

st.title("")

if csv_file:
    try:
        dataframe = pd.read_csv(csv_file)
    except:
        notify_file.error("An error occured while reading the CSV file. Check your file format, name and content and try again", icon='⚠️')

    range_opt = st.selectbox(label="Coverage", options=["annual", "monthly"], index=0, placeholder="annual")

    try:    
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
            col1, col2, col3 = st.columns(3)
            if col2.form_submit_button(label='Create Heatmap', use_container_width=True):
                zones_opt = 0 if not zones_multiselect else zones_multiselect
                months_opt = 0 if not months_selected else months_selected
                filename = csv_file.name.replace(".csv", "")
                filename = f"{filename}_{datetime.now().strftime('%H-%M-%S_%d-%m')}"
                notify_heatmap = st.container()
                try:
                    new_heatmap = HeatMap(df=dataframe, target_type=type_opt, zones=zones_opt, months=months_opt, tight=use_tight, cbar_orientation=cbar_loc, filename=filename)
                    if range_opt == 'annual':
                        new_heatmap.annual()
                    elif range_opt == 'monthly':
                        new_heatmap.monthly()
                except Exception as e:
                    notify_heatmap.error(f'The following error occured while processing the files: {e}', icon='⚠️')
    except Exception as e:
        notify_file.error(f'ERROR: No month column detected in dataframe. Change the Coverage to match your dataframe type.', icon='⚠️')

globed = glob("output/*.png")
if len(globed) != 0:
    with zipfile.ZipFile(r'cache/outputs.zip', 'w') as meu_zip:
        for csv_file in globed:
            meu_zip.write(csv_file, arcname=csv_file)
    col1, col2, col3 = st.columns(3)
    with open(r'cache/outputs.zip', 'rb') as f:
        bytes = f.read()
        col2.download_button(
            label="Download Heatmaps",
            data=bytes,
            file_name='outputs.zip',
            mime='application/zip',
            use_container_width=True
        )

if len(globed) != 0:
    st.title("")
    st.caption("Heatmaps Gallery:")
    with st.container(border=True):
        globed = list(reversed(globed))
        ncols = min(2, len(globed))
        cols = st.columns(ncols)
        for i, img in enumerate(globed):
            cols[i % ncols].image(img)
