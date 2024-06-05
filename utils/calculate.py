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


def save_and_connect_sql(file):
    db_path = "cache/database.sql"
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


# def read_db_and_build_dicts(sql, selected_zones, way: str) -> dict:
#     """Lê o arquivo .sql e constrói
#     os dicionários de valores que aparecem nas planilhas
#     e valores em que se transformam.
#     selected_zones: "All" ou lista de zonas
#     way: convection ou surface"""
#     conn = sqlite3.connect(sql)

#     cursor = conn.cursor()

#     if selected_zones != 'All':
#         selected_zones = ', '.join(f'"{zona}"' for zona in selected_zones)
#         cursor.execute(f"SELECT ZoneIndex, ZoneName FROM Zones WHERE ZoneName IN ({selected_zones});")
#     else:
#         cursor.execute("SELECT ZoneIndex, ZoneName FROM Zones;")
#     result = cursor.fetchall()
#     zones_dict = {}
#     for i in result:
#         zones_dict[i[1]] = i[0]
#     print(f'- Returned [bright_cyan]{zones_dict}[/bright_cyan]')
#     surfaces_dict = {}
#     for key, value in zones_dict.items():
#         print(f'[bright_magenta]/ Building dataframe of information for [bright_blue]{key}[/bright_blue] of value[/bright_magenta] {value}')
#         cursor.execute(f"SELECT ZoneIndex, SurfaceName, ClassName, Azimuth, ExtBoundCond FROM Surfaces WHERE ZoneIndex={value};")
#         result = cursor.fetchall()
#         surfaces_dict[key] = pd.DataFrame(result, columns=['ZoneIndex', 'SurfaceName', 'ClassName', 'Azimuth', 'ExtBoundCond'])
#         for idx in surfaces_dict[key].index:

#             if surfaces_dict[key].at[idx, 'ExtBoundCond'] == 0:
#                 surfaces_dict[key].at[idx, 'ExtBoundCond'] = 'ext'
#             else:
#                 surfaces_dict[key].at[idx, 'ExtBoundCond'] = 'int'
                
#             azimuth = surfaces_dict[key].at[idx, 'Azimuth']
#             if azimuth < 22.5 or azimuth >= 337.5:
#                 surfaces_dict[key].at[idx, 'Azimuth'] = 'north'
#             elif azimuth >= 22.5 and azimuth < 67.5:
#                 surfaces_dict[key].at[idx, 'Azimuth'] = 'northeast'
#             elif azimuth >= 67.5 and azimuth < 112.5:
#                 surfaces_dict[key].at[idx, 'Azimuth'] = 'east'
#             elif azimuth >= 112.5 and azimuth < 157.5:
#                 surfaces_dict[key].at[idx, 'Azimuth'] = 'southeast'
#             elif azimuth >= 157.5 and azimuth < 202.5:
#                 surfaces_dict[key].at[idx, 'Azimuth'] = 'south'
#             elif azimuth >= 202.5 and azimuth < 247.5:
#                 surfaces_dict[key].at[idx, 'Azimuth'] = 'southwest'
#             elif azimuth >= 247.5 and azimuth < 292.5:
#                 surfaces_dict[key].at[idx, 'Azimuth'] = 'west'
#             elif azimuth >= 292.5 and azimuth < 337.5:
#                 surfaces_dict[key].at[idx, 'Azimuth'] = 'northwest'

#             match surfaces_dict[key].at[idx, 'ClassName']:
#                 case 'Door':
#                     surfaces_dict[key].at[idx, 'ClassName'] = 'Wall'
#                 case 'Ceiling':
#                     surfaces_dict[key].at[idx, 'ClassName'] = 'Roof'
#     cursor.close()
#     conn.close()
#     print('- Building dictionary of names to rename...')
#     dicionario = {}
#     for zone, dataframe in surfaces_dict.items():
#         dicionario[zone] = {'convection': {}, 'surface': {}}
#         match way:
#             case 'convection':    
#                 for zone_specific, zone_transform in zone_addons.items():
#                     dicionario[zone]['convection'][f"{zone}:{zone_specific}"] = zone_transform
#         print('- Creating [bright_blue]surfaces[/bright_blue]...')
#         for idx in dataframe.index:
#             surf_name = dataframe.at[idx, 'SurfaceName']
#             surf_type = dataframe.at[idx, 'ClassName']
#             surf_bound = dataframe.at[idx, 'ExtBoundCond']
#             surf_azimuth = dataframe.at[idx, 'Azimuth']
#             match way:
#                 case 'convection':
#                     #convection
#                     if surf_type in ['Roof', 'Floor']:	
#                         dicionario[zone]['convection'][f'{surf_name}:{convection_addons["default"]}'] = f'convection?none_{surf_bound}{surf_type}'
#                     else:
#                         if surf_type in ['Window', 'GlassDoor']:
#                             dicionario[zone]['convection'][f'{surf_name}:{convection_addons["frame"]}'] = f'convection?{surf_azimuth}_frame'
#                         dicionario[zone]['convection'][f'{surf_name}:{convection_addons["default"]}'] = f'convection?{surf_azimuth}_{surf_bound}{surf_type}'
#                 case 'surface':
#                     #surface
#                     if surf_type not in ['Window', 'GlassDoor']:
#                         for surface_specific, surf_transf in surface_addons.items():
#                             if surf_type in ['Roof', 'Floor']:
#                                 dicionario[zone]['surface'][f'{surf_name}:{surface_specific}'] = f'{surf_transf}?none_{surf_bound}{surf_type}'
#                             else:
#                                 dicionario[zone]['surface'][f'{surf_name}:{surface_specific}'] = f'{surf_transf}?{surf_azimuth}_{surf_bound}{surf_type}'
#     print('- [bright_green]Finished reading database')
#     return dicionario
