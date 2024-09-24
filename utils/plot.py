from utils.src import *

num_to_month = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
surfaces_rename = {
    "conduction": "Conduction",
    "convection": "Convection",
    "lwinternal": "LW Rad.\nInternal Gains",
    "lwsurfaces": "LW Rad.\nSurfaces",
    "swlights": "SW Rad.\nLights",
    "solarrad": "Solar\nRad."
}


class HeatMap:
    def __init__(self, df: pd.DataFrame, target_type: str, zones: list, months: list, cbar_orientation: str, filename: str, values: str, lang: str, annotate: bool, fmt: int = 2, sizefont: float = 10, tight: bool = False):
        self.df = df
        self.target_type = target_type
        self.lang = lang
        if self.lang == 'pt-BR':
            if self.target_type == 'convection':
                self.target_type_lang = 'convecção'
            elif self.target_type == 'surface':
                self.target_type_lang = 'superfície'
        else:
            self.target_type_lang = self.target_type
        self.filename = filename
        self.annotate = annotate
        self.fmt = f'.{fmt}f'
        self.values = values
        values_en_to_pt = {
            'HEI': "valor absoluto da troca de calor",
            'value [kWh]': "valor [kWh]"
        }
        self.cbar_name = self.values if self.lang == 'en-US' else values_en_to_pt[self.values]
        if self.values == 'HEI':
            self.max_val = 1
            self.min_val = 0
        else:
            self.max_val = None
            self.min_val = None
        self.df['gains_losses'] = self.df['gains_losses'].apply(lambda name: name.replace("_", " ").title())
        self.df['gains_losses'] = self.df.apply(lambda row: f'{row["gains_losses"]} +' if row['heat_direction'] == 'gain' else f'{row["gains_losses"]} -', axis=1)
        self.zones = zones
        self.sizefont = sizefont
        self.months = months
        self.cbar_orientation = cbar_orientation
        match self.zones:
            case 0:
                self.df = self.df.loc[self.df['zone'] != 'EXTERNAL']
                self.title = f'Total HeatMap of {self.target_type_lang}' if self.lang == "en-US" else f'Mapa de calor total de {self.target_type_lang}'
            case _:
                self.df = self.df.loc[self.df['zone'].isin(self.zones)]    
                self.title = f'HeatMap of {self.target_type_lang} for zones {", ".join(self.zones)}' if self.lang == "en-US" else f'Mapa de calor de {self.target_type_lang} das zonas {", ".join(self.zones)}'
        match self.months:
            case 0:
                pass
            case _:
                self.df = self.df.loc[self.df['month'].isin(self.months)]
        if self.target_type == 'surface':
            self.df['zone'] = self.df.apply(lambda row: f'{row["zone"]}|{row["flux"]}', axis=1)
        if self.cbar_orientation in ['top', 'bottom']:
            self.cbar_kws = {"location": self.cbar_orientation, 'shrink': 0.5}
            self.tight = False
        else:
            self.cbar_kws = {"location": self.cbar_orientation}
            self.tight = tight

    def plot_heatmap(self, month_plot: bool = False) -> sns.heatmap:
        plt.figure(figsize=(16, 9))
        colors = ["#FFFFFF", "#496DDB", "#00CC66", "#FFFF00", "#F98016", "#F2002B"] if self.target_type == 'convection' else ["#FFFFFF","#A8DADC","#1D3557","#FFBA49","#EC9A9A","#D13440"]
        cmap = LinearSegmentedColormap.from_list('Custom_cmap', colors)
        heatmap = sns.heatmap(data=self.df, vmax=self.max_val, annot=self.annotate, fmt=self.fmt, vmin=self.min_val, cmap=cmap, linewidths=1, xticklabels=True, yticklabels=True, cbar_kws = self.cbar_kws)
        heatmap.set_xlabel('')
        heatmap.set_ylabel('Heat Exchange' if self.lang == 'en-US' else "Trocas de calor")
        heatmap.set_title(self.title)
        heatmap.collections[0].colorbar.set_label(self.cbar_name)
        heatmap.tick_params(left=False, bottom=True)
        plt.xticks(rotation=90, fontsize=self.sizefont)
        plt.yticks(fontsize=self.sizefont)
        if self.target_type == 'surface' or month_plot:
            ax = plt.gca()
            labels = ax.get_xticklabels()
            if self.target_type == 'surface' and month_plot:
                splited = [label.get_text().split('|') for label in labels]
                splited = [[name[0], name[1].replace('?',' ')] for name in splited]
                try:
                    splited = [[name[0], name[1].replace(name[1].split(' ')[0], surfaces_rename[name[1].split(' ')[0]])] for name in splited]
                except:
                    splited = [[name[0], name[1].title()] for name in splited]
            elif self.target_type == 'surface':
                splited = [label.get_text().split('|') for label in labels]
                try:
                    splited = [[name[0], name[1].replace(name[1], surfaces_rename[name[1]])] for name in splited]
                except:
                    splited = [[name[0], name[1].title()] for name in splited]
            elif month_plot:
                splited = splited = [label.get_text().split('?') for label in labels]
            new_labels = [name[0] for name in splited]
            heatmap.set_xticklabels(new_labels, rotation=90, fontsize=self.sizefont)
            ax2 = ax.twiny()
            ax2.set_xticks(ax.get_xticks())
            new_labels2 = [name[1] for name in splited]
            ax2.set_xticklabels(new_labels2, rotation=90, fontsize=self.sizefont)
            ax.xaxis.tick_bottom()
            ax2.xaxis.tick_top()
            ax.tick_params(bottom=False) 
        if self.tight:
            plt.tight_layout()
        plt.savefig(f"output/{self.filename}.png", format="png")

    def month_number(self, column_name):
        month_num = int(column_name.split('?')[1])
        return month_num
    
    def order_sign(self):
        df_plus = self.df[[sign[-1] == '+' for sign in self.df.index]]
        df_mins = self.df[[sign[-1] == '-' for sign in self.df.index]]
        self.df = pd.concat([df_plus, df_mins], axis=0)

    def annual(self) -> sns.heatmap:
        self.df = self.df[['gains_losses', 'zone', self.values]].pivot_table(index='gains_losses', columns='zone', values=self.values).fillna(0)
        self.order_sign()
        self.plot_heatmap()
        

    def monthly(self) -> sns.heatmap:
        self.df['zone'] = self.df.apply(lambda row: f'{row["zone"]}?{row["month"]}', axis=1)
        self.df = self.df[['gains_losses', 'zone', self.values]].pivot_table(index='gains_losses', columns='zone', values=self.values).fillna(0)
        self.df = self.df[sorted(self.df.columns, key=self.month_number)]
        self.order_sign()
        self.df.columns = [f'{column.split("?")[0]}?{column.split("?")[1].replace(column.split("?")[1], num_to_month[int(column.split("?")[1])])}' for column in self.df.columns]
        self.plot_heatmap(month_plot=True)


class BarPlot:
    def __init__(self, data: pd.DataFrame, target_type: str, filename: str, lang: str, zones: list = "All zones", months: list = "All year", values: str = "value [kWh]", tight: bool = False):
        self.data = data
        self.zones = zones
        self.months = months
        self.filename = filename
        self.values = values
        self.lang = lang
        values_en_to_pt = {
            'HEI': "valor absoluto da troca de calor",
            'value [kWh]': "valor [kWh]"
        }
        self.y_name = self.values if self.lang == 'en-US' else values_en_to_pt[self.values]
        self.tight = tight
        self.target_type = target_type
        if self.lang == 'pt-BR':
            if self.target_type == 'convection':
                self.target_type_lang = 'convecção'
            elif self.target_type == 'surface':
                self.target_type_lang = 'superfície'
        else:
            self.target_type_lang = self.target_type
        match self.zones:
            case 0:
                self.data = self.data.loc[self.data['zone'] != 'EXTERNAL']
                self.title = f'Total BarPlot of {self.target_type_lang}' if self.lang == 'en-US' else f'Gráfico de barras total de {self.target_type_lang}'
            case _:
                self.data = self.data.loc[self.data['zone'].isin(self.zones)]    
                self.title = f'BarPlot of {self.target_type_lang} for zones {", ".join(self.zones)}' if self.lang == 'en-US' else f'Gráfico de barras de {self.target_type_lang} para as zonas {", ".join(self.zones)}'
        match self.months:
            case 0:
                pass
            case _:
                self.data = self.data.loc[self.data['month'].isin(self.months)]


    def annual(self):
        color_scheme = 'gist_rainbow'
        unique_zones = self.data['zone'].unique()
        palette = sns.color_palette(color_scheme, len(unique_zones))
        color_map = dict(zip(unique_zones, palette))

        bar_colors = self.data['zone'].map(color_map)

        plt.figure(figsize=(16, 9))
        plt.grid(True)
        bars = plt.bar(self.data['gains_losses'], self.data[self.values], color=bar_colors)
        plt.title(self.title)
        plt.ylabel(self.y_name)
        plt.xlabel('Gains and Losses' if self.lang == 'en-US' else "Ganhos e Perdas")
        plt.xticks(rotation=25)

        handles = [plt.Rectangle((0,0),1,1, color=color_map[zone]) for zone in unique_zones]
        labels = [zone for zone in unique_zones]
        plt.legend(handles, labels, title='Zones' if self.lang == 'en-US' else 'Zonas')

        if self.tight:
            plt.tight_layout(True)
        plt.savefig(f"output/{self.filename}.png", format="png")

