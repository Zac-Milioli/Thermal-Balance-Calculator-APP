from utils.src import *

zone_addons = {
    'Zone Total Internal Convective Heating Rate': 'convection?internal_gain',
    'AFN Zone Ventilation Sensible Heat Gain Rate': 'convection?vn_window_gain',
    'AFN Zone Ventilation Sensible Heat Loss Rate': 'convection?vn_window_loss',
    'AFN Zone Mixing Sensible Heat Gain Rate': 'convection?vn_interzone_gain',
    'AFN Zone Mixing Sensible Heat Loss Rate': 'convection?vn_interzone_loss',
    'Zone Air System Sensible Heating Rate': 'convection?heating_gain',
    'Zone Air System Sensible Cooling Rate': 'convection?cooling_loss'
}

convection_addons = {
    'default': 'Surface Inside Face Convection Heat Gain Rate',
    'frame': 'Surface Window Inside Face Frame and Divider Zone Heat Gain Rate'
}

surface_addons = {
    'Surface Inside Face Convection Heat Gain Rate': 'convection',
    'Surface Inside Face Conduction Heat Transfer Rate': 'conduction',
    'Surface Inside Face Solar Radiation Heat Gain Rate': 'solarrad',
    'Surface Inside Face Lights Radiation Heat Gain Rate': 'swlights',
    'Surface Inside Face Net Surface Thermal Radiation Heat Gain Rate': 'lwsurfaces',
    'Surface Inside Face Internal Gains Radiation Heat Gain Rate': 'lwinternal'
}

drybulb_rename = {'EXTERNAL': {'Environment': 'drybulb?temp_ext'}}

WALL = 'Wall'
FLOOR = 'Floor'
ROOF = 'Roof'

output_path = r'output/'
cache_path = r'cache/'
db_path = r'cache/database.sql'


def save_and_connect_sql(file):
    with open(db_path, "wb") as f:
        f.write(file.getbuffer())
    conn = sqlite3.connect(db_path)
    return conn


def read_db_for_zones(connection: sqlite3.Connection) -> list:
    cursor = connection.cursor()
    cursor.execute("SELECT ZoneName FROM Zones;")
    result = cursor.fetchall()
    connection.close()
    result = [i[0] for i in result]
    return result


def read_db_and_build_dicts(selected_zones, way: str, pbar: st.progress) -> dict:
    """Lê o arquivo .sql e constrói
    os dicionários de valores que aparecem nas planilhas
    e valores em que se transformam.
    selected_zones: "All" ou lista de zonas
    way: convection ou surface
    pbar: barra de progresso
    """
    pbar.progress(8, "Connecting to the SQL and reading the tables...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if selected_zones != 'All':
        selected_zones = ', '.join(f'"{zona}"' for zona in selected_zones)
        cursor.execute(f"SELECT ZoneIndex, ZoneName FROM Zones WHERE ZoneName IN ({selected_zones});")
    else:
        cursor.execute("SELECT ZoneIndex, ZoneName FROM Zones;")
    result = cursor.fetchall()
    zones_dict = {}
    for i in result:
        zones_dict[i[1]] = i[0]
    surfaces_dict = {}
    for key, value in zones_dict.items():
        cursor.execute(f"SELECT ZoneIndex, SurfaceName, ClassName, Azimuth, ExtBoundCond FROM Surfaces WHERE ZoneIndex={value};")
        result = cursor.fetchall()
        surfaces_dict[key] = pd.DataFrame(result, columns=['ZoneIndex', 'SurfaceName', 'ClassName', 'Azimuth', 'ExtBoundCond'])
        for idx in surfaces_dict[key].index:

            if surfaces_dict[key].at[idx, 'ExtBoundCond'] == 0:
                surfaces_dict[key].at[idx, 'ExtBoundCond'] = 'ext'
            else:
                surfaces_dict[key].at[idx, 'ExtBoundCond'] = 'int'
                
            azimuth = surfaces_dict[key].at[idx, 'Azimuth']
            if azimuth < 22.5 or azimuth >= 337.5:
                surfaces_dict[key].at[idx, 'Azimuth'] = 'north'
            elif azimuth >= 22.5 and azimuth < 67.5:
                surfaces_dict[key].at[idx, 'Azimuth'] = 'northeast'
            elif azimuth >= 67.5 and azimuth < 112.5:
                surfaces_dict[key].at[idx, 'Azimuth'] = 'east'
            elif azimuth >= 112.5 and azimuth < 157.5:
                surfaces_dict[key].at[idx, 'Azimuth'] = 'southeast'
            elif azimuth >= 157.5 and azimuth < 202.5:
                surfaces_dict[key].at[idx, 'Azimuth'] = 'south'
            elif azimuth >= 202.5 and azimuth < 247.5:
                surfaces_dict[key].at[idx, 'Azimuth'] = 'southwest'
            elif azimuth >= 247.5 and azimuth < 292.5:
                surfaces_dict[key].at[idx, 'Azimuth'] = 'west'
            elif azimuth >= 292.5 and azimuth < 337.5:
                surfaces_dict[key].at[idx, 'Azimuth'] = 'northwest'

            match surfaces_dict[key].at[idx, 'ClassName']:
                case 'Door':
                    surfaces_dict[key].at[idx, 'ClassName'] = 'Wall'
                case 'Ceiling':
                    surfaces_dict[key].at[idx, 'ClassName'] = 'Roof'
    cursor.close()
    conn.close()
    pbar.progress(14, "Building utility objects from SQL data...")
    dicionario = {}
    for zone, dataframe in surfaces_dict.items():
        dicionario[zone] = {'convection': {}, 'surface': {}}
        match way:
            case 'convection':    
                for zone_specific, zone_transform in zone_addons.items():
                    dicionario[zone]['convection'][f"{zone}:{zone_specific}"] = zone_transform
        for idx in dataframe.index:
            surf_name = dataframe.at[idx, 'SurfaceName']
            surf_type = dataframe.at[idx, 'ClassName']
            surf_bound = dataframe.at[idx, 'ExtBoundCond']
            surf_azimuth = dataframe.at[idx, 'Azimuth']
            match way:
                case 'convection':
                    #convection
                    if surf_type in ['Roof', 'Floor']:	
                        dicionario[zone]['convection'][f'{surf_name}:{convection_addons["default"]}'] = f'convection?none_{surf_bound}{surf_type}'
                    else:
                        if surf_type in ['Window', 'GlassDoor']:
                            dicionario[zone]['convection'][f'{surf_name}:{convection_addons["frame"]}'] = f'convection?{surf_azimuth}_frame'
                        dicionario[zone]['convection'][f'{surf_name}:{convection_addons["default"]}'] = f'convection?{surf_azimuth}_{surf_bound}{surf_type}'
                case 'surface':
                    #surface
                    if surf_type not in ['Window', 'GlassDoor']:
                        for surface_specific, surf_transf in surface_addons.items():
                            if surf_type in ['Roof', 'Floor']:
                                dicionario[zone]['surface'][f'{surf_name}:{surface_specific}'] = f'{surf_transf}?none_{surf_bound}{surf_type}'
                            else:
                                dicionario[zone]['surface'][f'{surf_name}:{surface_specific}'] = f'{surf_transf}?{surf_azimuth}_{surf_bound}{surf_type}'
    clear_cache()
    return dicionario


def rename_cols(columns_list: list, df: pd.DataFrame, way: str, dicionario: dict, pbar: st.progress) -> pd.DataFrame:
    """Renomeia todas as colunas e gera as listas de configurações"""
    wanted_list = ['drybulb?temp_ext', 'Date/Time']
    pbar.progress(16, "Renaming columns...")
    for specific_zone in dicionario:
        for item in columns_list:
                for new_name in dicionario[specific_zone][way]:
                    if new_name in item:
                        oficial = f"{specific_zone}_{dicionario[specific_zone][way][new_name]}"
                        df = df.rename(columns={item: oficial})
                        wanted_list.append(oficial)
    searchword, new_name = list(drybulb_rename['EXTERNAL'].keys())[0], drybulb_rename['EXTERNAL']['Environment']
    columns_list = df.columns
    for item in columns_list:
        if searchword in item:
            df = df.rename(columns={item: new_name})
    pbar.progress(19, "Building more utility objects...")
    dont_change_list = ['drybulb?temp_ext']
    for item in wanted_list:
        if item.endswith('loss') or item.endswith('gains') or item.endswith('gain') or item.endswith('cooling') or item.endswith('heating'):
            dont_change_list.append(item)
    dont_change_list = list(set(dont_change_list))

    ref_multiply_list = ["heating", "vn_window_gain", "vn_interzone_gain", "frame", "internal"]
    multiply_list = []
    for item in ref_multiply_list:
        for i in wanted_list:
            if item in i:
                multiply_list.append(i)
    multiply_list = list(set(multiply_list))

    return df, wanted_list, dont_change_list, multiply_list


def sum_separated(coluna) -> pd.Series:
    """
    Soma separadamente os positivos e os negativos, retornando um objeto 
    Series contendo em uma coluna os positivos e em outra os negativos de cada linha
    """
    positivos = coluna[coluna >= 0].sum()
    negativos = coluna[coluna < 0].sum()
    return pd.Series([positivos, negativos])


def divide(df: pd.DataFrame, dont_change_list: list) -> pd.DataFrame:
    """
    Divide algumas colunas em gain e loss. Ao fim, adiciona às colunas os nomes de 
    gains_losses e value
    """
    divided = pd.DataFrame()
    col = df.columns
    windows_and_frames = {}
    for column in col:
        if column in dont_change_list:
            pass
        elif column in ["Window", "GlassDoor"]:
            azimuth_boundsurface = column.split("_")[-1]
            configs_name = column.replace(azimuth_boundsurface, "frame")
            windows_and_frames[f"{configs_name}_gain"] = f"{column}_gain"
            windows_and_frames[f"{configs_name}_loss"] = f"{column}_loss"
    for column in col:
        if column in dont_change_list:
            divided[column] = df[column]
        else:
            divided[f'{column}_gain'] = df[column].apply(lambda item: item if item>0 else 0)
            divided[f'{column}_loss'] = df[column].apply(lambda item: item if item<0 else 0)
    divided = divided.rename(columns=windows_and_frames)
    divided = divided.groupby(level=0, axis=1).sum()
    divided = divided.reset_index()
    divided = divided.drop(columns='index', axis=1)
    divided = divided.sum().reset_index()
    divided.columns = ['gains_losses', 'value']
    return divided


def invert_values(dataframe: pd.DataFrame, way: str, multiply_list: list) -> pd.DataFrame:
    """Multiplica as colunas específicas por -1."""
    if way == 'convection':
        df_copy = dataframe.copy()
        colunas = list(df_copy.columns)
        colunas.remove('Date/Time')
        for coluna in colunas:
            for item in multiply_list:
                if item not in coluna:
                    df_copy[coluna] = df_copy[coluna] *-1
    else:
        df_copy = dataframe.copy()
    return df_copy


def renamer_and_formater(df: pd.DataFrame, way: str, zones_dict: dict, pbar: st.progress) -> pd.DataFrame:
    """
    Recebe o dataframe e uma lista de zonas, então manipula-o renomeando cada lista de 
    colunas e excluindo as colunas desnecessárias 
    """
    columns_list = df.columns
    df, wanted_list, dont_change_list, multiply_list = rename_cols(columns_list=columns_list, df=df, way=way, dicionario=zones_dict, pbar=pbar)
    columns_list = df.columns
    unwanted_list = []
    pbar.progress(23, "Editing columns...")
    for item in columns_list:
        if item not in wanted_list:
            unwanted_list.append(item)
    df = df.drop(columns=unwanted_list, axis=1)
    return df, dont_change_list, multiply_list


def basic_manipulator(df: pd.DataFrame, dont_change_list: list) -> pd.DataFrame:
    """Faz o procedimento básico para todos os dataframes serem manipulados"""
    df = df.drop(columns='Date/Time', axis=1)
    df = df.apply(sum_separated)
    df = divide(df, dont_change_list=dont_change_list)
    return df


def zone_breaker(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renomeia cada item da coluna zone para sua respectiva zona, renomeia 
    também o gains_losses para remover a zona nele aplicada
    """
    for j in df.index:
        if drybulb_rename['EXTERNAL']['Environment'] in df.at[j, 'gains_losses']:
            df.at[j, 'zone'] = 'EXTERNAL'
        else:
            zones = df.at[j, 'gains_losses'].split('_')[0]
            lenght = (len(zones)+1)
            new_name = df.at[j, 'gains_losses'][lenght:]
            df.at[j, 'zone'] = zones
            df.at[j, 'gains_losses'] = new_name
    return df


def concatenator() -> pd.DataFrame:
    """
    Concatena todos os itens dentro de organizer e retorna o 
    dataframe resultante
    """
    glob_organizer = glob(cache_path+'*.csv')
    df = pd.read_csv(glob_organizer[0], sep=',')
    glob_organizer.pop(0)
    for item in glob_organizer:
        each_df = pd.read_csv(item, sep=',')
        df = pd.concat([df, each_df], axis=0, ignore_index=True)
    df = df.drop(columns='Unnamed: 0', axis=1)
    clear_cache()
    return df


def way_breaker(df: pd.DataFrame) -> pd.DataFrame:
    """
    Irá formatar o arquivo adicionando adequadamente o tipo de
    forma de transmissão de calor
    """
    df.loc[:, 'flux'] = 'Empty'
    for i in df.index:
            splited = df.at[i, 'gains_losses'].split('?')
            df.at[i, 'flux'] = splited[0]
            df.at[i, 'gains_losses'] = splited[1] 
    return df


def heat_direction_breaker(df: pd.DataFrame) -> pd.DataFrame:
    """
    Irá formatar o arquivo adicionando adequadamente o sentido de transferência de calor
    """
    df.loc[:, 'heat_direction'] = 'no direction'
    verification = drybulb_rename['EXTERNAL']['Environment'].split('?')[-1]
    for j in df.index:
        name = df.at[j, 'gains_losses']
        if verification in name:
            continue
        else:
            heat_direction = name.split('_')[-1]
            lenght = (len(heat_direction)+1)
            new_name = name[:-lenght]
            df.at[j, 'heat_direction'] = heat_direction
            df.at[j, 'gains_losses'] = new_name
    return df


def days_finder(date_str: str) -> list:
    """Busca e retorna uma lista contendo o dia, dia anterior e 
    dia seguinte ao evento"""
    date_str_splt = date_str.split(' ')
    if date_str_splt[0] == '':
        date_obj = datetime.strptime(date_str_splt[1], '%m/%d')
    else:
        date_obj = datetime.strptime(date_str_splt[0], '%m/%d')
    date_str = date_obj.strftime('%m/%d')
    day_bf = (date_obj - timedelta(days=1)).strftime('%m/%d')
    day_af = (date_obj + timedelta(days=1)).strftime('%m/%d')
    days_list = [date_str, day_bf, day_af]
    return days_list


def daily_manipulator(df: pd.DataFrame, days_list: list, name: str, way: str, zone: list, dont_change_list: list, pbar: st.progress, legend: str) -> pd.DataFrame:
    """Manipula e gera os dataframes para cada datetime 
    dentro do período do evento"""
    new_daily_df = df.copy()
    # MÉTODO ANTIGO
    # count_len_for_pbar = 1/len(new_daily_df.index)
    # pbar_state = 0.0
    # for j in new_daily_df.index:
    #     date_splited = new_daily_df.at[j, 'Date/Time'].split(' ')[1]
    #     # pbar.progress(pbar_state, f"Processing date {date_splited} for {legend}")
    #     if date_splited not in days_list:
    #         new_daily_df = new_daily_df.drop(j, axis=0)
    #     # pbar_state += count_len_for_pbar
    pbar.progress(50, "Separating the correct timestamp...")
    mask = new_daily_df['Date/Time'].str.split(' ').str.get(1).isin(days_list)
    new_daily_df = new_daily_df[mask]
    days = new_daily_df['Date/Time'].unique()
    count_len_for_pbar = 1/len(days)
    pbar_state = 0.0
    for unique_datetime in days:
        pbar.progress(pbar_state, f"Calculating heat exchange index for {unique_datetime}")
        pbar_state += count_len_for_pbar
        df_daily = new_daily_df[new_daily_df['Date/Time'] == unique_datetime]
        soma = basic_manipulator(df=df_daily, dont_change_list=dont_change_list)
        soma.loc[:, 'case'] = name
        soma.loc[:, 'Date/Time'] = unique_datetime
        soma.loc[:, 'zone'] = 'no zone'
        soma = zone_breaker(df=soma)
        soma = way_breaker(df=soma)
        soma = heat_direction_breaker(df=soma)
        for row in soma.index:
            day = str(soma.at[row, 'Date/Time']).strip()
            soma.at[row, 'day'] = day[3:5]
        soma.loc[:, 'month'] = 'no month'
        for row in soma.index:
            month = str(soma.at[row, 'Date/Time'])
            soma.at[row, 'month'] = month.split('/')[0].strip()
        soma.loc[:, 'hour'] = 'no hour'
        for row in soma.index:
            hour = str(soma.at[row, 'Date/Time'])
            soma.at[row, 'hour'] = hour[8:10]
        unique_datetime = unique_datetime.replace('/', '-').replace('  ', '_').replace(' ', '_').replace(':', '-')
        soma = hei_organizer(df=soma, way=way, zone=zone)
        soma.to_csv(cache_path+'_datetime'+unique_datetime+'.csv', sep=',')
    df_total = concatenator()
    df_total = df_total[['Date/Time', 'month', 'day', 'hour', 'flux', 'zone', 'gains_losses', 'value', 'HEI', 'case']]
    return df_total


def calculate_module_total_and_hei(df: pd.DataFrame) -> pd.DataFrame:
    """Cálculo do HEI em si
    df: pd.DataFrame"""
    module_total = df.groupby('zone')['absolute'].transform('sum')
    df['HEI'] = df['absolute'] / module_total
    return df


def hei_organizer(df: pd.DataFrame, way: str, zone) -> pd.DataFrame:
    """
    Prepara a planilha para o cálculo do HEI.
    df (pd.DataFrame): O dataframe contendo os dados a serem organizados.
    way (str): O método de organização, pode ser 'convection' ou 'surface'.
    zone: A zona a ser considerada, pode ser 'All' ou uma lista de zonas.
    """
    df['absolute'] = df['value'].abs()
    df['HEI'] = np.nan
    if zone == 'All':
        zones_to_consider = df['zone'].unique()
    else:
        zones_to_consider = zone
    if way == 'convection':
        for local in zones_to_consider:
            df.loc[df['zone'] == local] = calculate_module_total_and_hei(df.loc[df['zone'] == local])
    if way == 'surface':
        for local in zones_to_consider:
            for superficie in df['gains_losses'].unique():
                if WALL in superficie or FLOOR in superficie or ROOF in superficie:
                    mask = (df['zone'] == local) & (df['gains_losses'] == superficie)
                    df.loc[mask] = calculate_module_total_and_hei(df.loc[mask])
    df = df.drop(['absolute'], axis=1)
    return df


def generate_df(input_dataframe: pd.DataFrame, filename: str, way: str, type_name: str, zone, coverage: str, pbar: st.progress):
    """
    Irá gerar os dataframes, separando por zona.
    input_dataframe: objeto dataframe
    filename: nome do arquivo
    way: convection/surface
    type_name: _convection_/_surface_
    zone: lista de zonas (SALA, DORM1, DORM2) ou string
    coverage: annual/monthly/daily
    pbar: barra de progresso
    """
    input_dataframe = input_dataframe.dropna()
    dicionario = read_db_and_build_dicts(selected_zones=zone, way=way, pbar=pbar)
    if zone == 'All':
        zones_for_name = 'All-Zones'
    else:
        zones_for_name = []
        for key in dicionario.keys():
            zones_for_name.append(key)
        zones_for_name = '-'.join(zones_for_name)
    input_dataframe, dont_change_list, multiply_list = renamer_and_formater(df=input_dataframe, way=way, zones_dict=dicionario, pbar=pbar)
    # São agrupadas e somadas as colunas iguais
    pbar.progress(26, "Calculating the sum of equal columns...")
    input_dataframe = input_dataframe.groupby(level=0, axis=1).sum()
    input_dataframe = input_dataframe.reset_index()
    pbar.progress(28, "Removing unused columns...")
    input_dataframe = input_dataframe.drop(columns='index', axis=1)
    pbar.progress(30, "Inverting the values of specific columns...")
    input_dataframe = invert_values(dataframe=input_dataframe, way=way, multiply_list=multiply_list)
    # Verifica o tipo de dataframe selecionado e cria-o
    match coverage:
        case 'annual':
            pbar.progress(40, "Separating positives from negatives...")
            soma = basic_manipulator(df=input_dataframe, dont_change_list=dont_change_list)
            soma.loc[:, 'case'] = filename
            soma.loc[:, 'zone'] = 'no zone'
            pbar.progress(50, "Separating zones...")
            soma = zone_breaker(df=soma)
            pbar.progress(60, "Separating heat flux...")
            soma = way_breaker(df=soma)
            pbar.progress(60, "Separating gains from losses...")
            soma = heat_direction_breaker(df=soma)
            pbar.progress(90, "Calculating heat exchange index...")
            soma = hei_organizer(df=soma, way=way, zone=zone)
            clear_cache()
            soma['value'] = soma['value'] / 1000
            soma = soma.rename(columns={'value': 'value [kWh]'})
            soma['gains_losses'] = soma['gains_losses'].str.replace("none_", "")
            soma.to_csv(output_path+'annual_'+zones_for_name+type_name+filename, sep=',', index=False)
        case 'monthly':
            pbar.progress(40, "Separating months...")
            input_dataframe.loc[:, 'month'] = 'no month'
            for row in input_dataframe.index:
                month = str(input_dataframe.at[row, 'Date/Time'])
                input_dataframe.at[row, 'month'] = month.split('/')[0].strip()
            months = input_dataframe['month'].unique()
            for unique_month in months:
                pbar.progress(40+int(unique_month)*4, f"Calculating Heat Exchange Index for month {unique_month}")
                df_monthly = input_dataframe[input_dataframe['month'] == unique_month]
                df_monthly = df_monthly.drop(columns='month', axis=1)
                soma = basic_manipulator(df=df_monthly, dont_change_list=dont_change_list)
                soma.loc[:, 'case'] = filename
                soma.loc[:, 'month'] = unique_month
                soma.loc[:, 'zone'] = 'no zone'
                soma = zone_breaker(df=soma)
                soma = way_breaker(df=soma)
                soma = heat_direction_breaker(df=soma)
                soma = hei_organizer(df=soma, way=way, zone=zone)
                soma.to_csv(cache_path+'_month'+unique_month+'.csv', sep=',')
            pbar.progress(90, "Joining all months...")
            df_total = concatenator()
            clear_cache()
            df_total['value'] = df_total['value'] / 1000
            df_total = df_total.rename(columns={'value': 'value [kWh]'})
            df_total['gains_losses'] = df_total['gains_losses'].str.replace("none_", "")
            df_total.to_csv(output_path+'monthly_'+zones_for_name+type_name+filename, sep=',', index=False)
        case 'daily':
            ## Max
            pbar.progress(40, "Searching for day with maximum value...")
            max_temp_idx = input_dataframe[drybulb_rename['EXTERNAL']['Environment']].idxmax()
            date_str = input_dataframe.loc[max_temp_idx, 'Date/Time']
            days_list = days_finder(date_str=date_str)
            pbar.progress(47, "Maximum value found...")
            df_total = daily_manipulator(df=input_dataframe, days_list=days_list, name=filename, way=way, zone=zone, dont_change_list=dont_change_list, pbar=pbar, legend="day with maximum value")
            clear_cache()
            df_total['value'] = df_total['value'] / 1000
            df_total = df_total.rename(columns={'value': 'value [kWh]'})
            df_total['gains_losses'] = df_total['gains_losses'].str.replace("none_", "")
            df_total.to_csv(output_path+'max_daily_'+zones_for_name+type_name+filename, sep=',', index=False)
            
            ## Min
            pbar.progress(54, "Searching for day with minimum value...")
            min_temp_idx = input_dataframe[drybulb_rename['EXTERNAL']['Environment']].idxmin()
            date_str = input_dataframe.loc[min_temp_idx, 'Date/Time']
            days_list = days_finder(date_str=date_str)
            pbar.progress(61, "Minimum value found...")
            df_total = daily_manipulator(df=input_dataframe, days_list=days_list, name=filename, way=way, zone=zone, dont_change_list=dont_change_list, pbar=pbar, legend="day with minimum value")
            clear_cache()
            df_total['value'] = df_total['value'] / 1000
            df_total = df_total.rename(columns={'value': 'value [kWh]'})
            df_total['gains_losses'] = df_total['gains_losses'].str.replace("none_", "")
            df_total.to_csv(output_path+'min_daily_'+zones_for_name+type_name+filename, sep=',', index=False)
        
            ## Max and Min amp locator
            pbar.progress(68, "Searching for day with maximum and minimum amplitudes...")
            df_amp = input_dataframe.copy()
            df_amp.loc[:, 'date'] = 'no date'
            for row in df_amp.index:
                date = str(df_amp.at[row, 'Date/Time']).strip()
                df_amp.at[row, 'date'] = date[0:5]
            max_amp = {'date': None, 'value': 0, 'index': 0}
            min_amp = {'date': None, 'value': 1000, 'index': 0}
            dates_list = df_amp['date'].unique()
            for days in dates_list:
                df_day = df_amp[df_amp['date'] == days]
                max_daily = df_day[drybulb_rename['EXTERNAL']['Environment']].max()
                idx_daily = df_day[drybulb_rename['EXTERNAL']['Environment']].idxmax()
                min_daily = df_day[drybulb_rename['EXTERNAL']['Environment']].min()
                total = abs(max_daily - min_daily)
                if total > max_amp['value']:
                    max_amp['date'] = days
                    max_amp['value'] = total
                    max_amp['index'] = idx_daily
                if total < min_amp['value']:
                    min_amp['date'] = days
                    min_amp['value'] = total
                    min_amp['index'] = idx_daily
            pbar.progress(75, "Days found...")

            # Max amp
            date_str = input_dataframe.loc[max_amp['index'], 'Date/Time']
            days_list = days_finder(date_str=date_str)
            pbar.progress(82, "Maximum amplitude found...")
            df_total = daily_manipulator(df=input_dataframe, days_list=days_list, name=filename, way=way, zone=zone, dont_change_list=dont_change_list, pbar=pbar, legend="day with maximum amplitude")
            clear_cache()
            df_total['value'] = df_total['value'] / 1000
            df_total = df_total.rename(columns={'value': 'value [kWh]'})
            df_total['gains_losses'] = df_total['gains_losses'].str.replace("none_", "")
            df_total.to_csv(output_path+'max_amp_daily_'+zones_for_name+type_name+filename, sep=',', index=False)
            
            # Min amp
            date_str = input_dataframe.loc[min_amp['index'], 'Date/Time']
            days_list = days_finder(date_str=date_str)
            pbar.progress(90, "Minimum amplitude found...")
            df_total = daily_manipulator(df=input_dataframe, days_list=days_list, name=filename, way=way, zone=zone, dont_change_list=dont_change_list, pbar=pbar, legend="day with minimum amplitude")
            clear_cache()
            df_total['value'] = df_total['value'] / 1000
            df_total = df_total.rename(columns={'value': 'value [kWh]'})
            df_total['gains_losses'] = df_total['gains_losses'].str.replace("none_", "")
            df_total.to_csv(output_path+'min_amp_daily_'+zones_for_name+type_name+filename, sep=',', index=False)
            pbar.progress(95, "Finishing...")
