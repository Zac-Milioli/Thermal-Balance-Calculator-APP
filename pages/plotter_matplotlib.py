from utils.plot import *

st.sidebar.write('')
st.sidebar.header("**CALCULADORA DE BALANÇO TÉRMICO**")
st.sidebar.divider()
st.sidebar.image(r"utils/lab_banner.png", width=300)

clear_cache()
clear_output_csv()
add_page_title(layout='wide')

col1, col2, col3 = st.columns(3)
if col2.button(label="Limpar galeria", use_container_width=True):
    clear_output()
st.title("")

csv_file = st.file_uploader(label="Faça upload do seu CSV de resultados", type="csv", accept_multiple_files=False)

notify_file = st.container()

st.title("")

if csv_file:
    try:
        dataframe = pd.read_csv(csv_file)
    except:
        notify_file.error("Um erro ocorreu ao ler o CSV inserido. Verifique o formato do seu arquivo, nome e conteúdo e tente novamente", icon='⚠️')

    range_opt = st.selectbox(label="Período", options=["annual", "monthly"], index=0, placeholder="annual")

    try:    
        with st.form("form_plotter", border=False):
            zones_in_df = dataframe["zone"].unique()
            zones_multiselect = st.multiselect(label="Zonas", options=zones_in_df, placeholder="All Zones")
            col1, col2 = st.columns(2)
            type_opt = col1.selectbox(label="Tipo", options=["convection", "surface"], index=0, placeholder="convection")
            vals = {"Heat Exchange Index": "HEI", "Heat Exchange Values": "value [kWh]"}
            use = col2.selectbox(label="Plotar", options=list(vals.keys()), index=0)
            format_use = col2.number_input(label='Insira o número de casas após a vírgula desejados (Escolha -1 caso deseje não exibir os valores)', step=1, value=-1, min_value=-1, max_value=10)
            
            cbar_loc = col1.radio(label="Localização da barra de cores", options=["bottom", "right", "top", "left"], index=0, horizontal=True)
            use_tight = col1.checkbox(label="Tight layout (Espremer o gráfico para telas menores, pode haver sobreposição)")

            months_selected = False
            if range_opt == 'monthly':
                months_on_df = dataframe['month'].unique()
                months_selected = st.multiselect(label="Meses", options=months_on_df, placeholder="All year")
            
            st.title("")
            col1, col2, col3 = st.columns(3)
            if col2.form_submit_button(label='Criar Heatmap', use_container_width=True):
                annot_vals = True if format_use != -1 else False
                format_use = 2 if format_use == -1 else format_use 
                zones_opt = 0 if not zones_multiselect else zones_multiselect
                months_opt = 0 if not months_selected else months_selected
                filename = csv_file.name.replace(".csv", "")
                filename = f"{filename}_{datetime.now().strftime('%H-%M-%S_%d-%m')}"
                notify_heatmap = st.container()
                try:
                    new_heatmap = HeatMap(df=dataframe, target_type=type_opt, zones=zones_opt, months=months_opt, tight=use_tight, cbar_orientation=cbar_loc, filename=filename, values=vals[use], annotate=annot_vals, fmt=format_use)
                    if range_opt == 'annual':
                        new_heatmap.annual()
                    elif range_opt == 'monthly':
                        new_heatmap.monthly()
                except:
                    notify_heatmap.error(f'Um erro ocorreu ao gerar o Heatmap.', icon='⚠️')
    except:
        notify_file.error(f'ERRO: Coluna de meses não encontrada na planilha. Altere o período para se igualar à sua planilha.', icon='⚠️')

globed = glob("output/*.png")
if len(globed) != 0:
    with zipfile.ZipFile(r'cache/outputs.zip', 'w') as meu_zip:
        for csv_file in globed:
            meu_zip.write(csv_file, arcname=csv_file)
    col1, col2, col3 = st.columns(3)
    with open(r'cache/outputs.zip', 'rb') as f:
        bytes = f.read()
        col2.download_button(
            label="Baixar Heatmaps",
            data=bytes,
            file_name='outputs.zip',
            mime='application/zip',
            use_container_width=True
        )

if len(globed) != 0:
    st.title("")
    st.caption("Galeria de Heatmaps:")
    with st.container(border=True):
        globed = list(reversed(globed))
        ncols = min(2, len(globed))
        cols = st.columns(ncols)
        for i, img in enumerate(globed):
            cols[i % ncols].image(img)
