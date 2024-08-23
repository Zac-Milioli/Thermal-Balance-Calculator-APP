from utils.calculate import *

clear_output_csv()
st.sidebar.write('')
st.sidebar.header("**CALCULADORA DE BALANÇO TÉRMICO**")
st.sidebar.divider()
st.sidebar.image(r"utils/lab_banner.png", width=300)
st.sidebar.title("")
st.sidebar.markdown("Ferramenta desenvolvida por [Zac Milioli](https://github.com/Zac-Milioli)")
st.sidebar.markdown("Teoria elaborada por Dra. [Letícia Eli](https://www.linkedin.com/in/letícia-gabriela-eli-347063b0)")
add_page_title(layout='wide')

st.warning("ATENÇÃO: É essencial que o usuário leia o **manual** e a **Wiki** antes de utilizar os Apps, pois a formatação dos arquivos deve seguir a documentação para funcionar", icon="💡")
st.title("")

sql_file = st.file_uploader("**Faça upload do seu arquivo SQL**", type="sql", accept_multiple_files=False,key='sql')

with st.form("form_calculator", border=False, clear_on_submit=True):
    notify_sql = st.container()
    worked = False
    if sql_file:
        try:
            with st.spinner("Lendo SQL..."):
                zones_list = read_db_for_zones(connection=save_and_connect_sql(sql_file))
                worked = True
        except:
            notify_sql.error("Um erro ocorreu ao processar o arquivo SQL", icon='⚠️')
            st.stop()
        
    if worked:
        col1, col2, col3 = st.columns(3)
        zone_option = col1.multiselect(label="Selecione as zonas", options=zones_list, placeholder="All Zones")
        type_option = col2.selectbox(label="Selecione o tipo", options=['convection', 'surface'], index=0, placeholder='convection')
        coverage_option = col3.selectbox(label="Selecione um período", options=['annual', 'monthly', 'daily'], index=0, placeholder='annual')
        csv_file = st.file_uploader("**Faça upload do seu CSV**", type="csv", accept_multiple_files=False,key='csv')
        notify_csv = st.container()
        st.title("")
        col1, col2, col3 = st.columns(3)
        if col2.form_submit_button("Calcular", use_container_width=True):
            if not csv_file:
                notify_csv.error("Você **deve** inserir um CSV para calcular", icon='⚠️')
            else:
                progress_bar = st.progress(0, text="Preparando arquivos (Dependendo do tamanho dos arquivos, isso pode levar algum tempo)")
                use_zones = "All" if not zone_option else zone_option
                try:
                    df = pd.read_csv(csv_file)
                    generate_df(input_dataframe=df, filename=csv_file.name, way=type_option, type_name=f"_{type_option}_", coverage=coverage_option, zone=use_zones, pbar=progress_bar)
                    progress_bar.progress(100, "Feito")
                    progress_bar.empty()
                except:
                    notify_csv.error(f"Um erro ocorreu ao processar o CSV", icon='⚠️')

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
            label="Baixar planilhas",
            data=bytes,
            file_name='outputs.zip',
            mime='application/zip',
            use_container_width=True
        )

if len(globed) != 0:
    st.title("")
    st.caption("Galeria de planilhas:")
    with st.container(border=True):
        ncols = min(2, len(globed))
        cols = st.columns(ncols)
        for i, df in enumerate(globed):
            cols[i % ncols].caption(df)
            cols[i % ncols].dataframe(pd.read_csv(df), use_container_width=True)