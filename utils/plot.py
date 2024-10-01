from utils.src import *

Image.MAX_IMAGE_PIXELS = 178956970

surfaces_rename = {
    "conduction": "Conduction",
    "convection": "Convection",
    "lwinternal": "LW Rad.\nInternal Gains",
    "lwsurfaces": "LW Rad.\nSurfaces",
    "swlights": "SW Rad.\nLights",
    "solarrad": "Solar\nRad."
}

values_en_to_pt = {
    'HEI': "índice de troca de calor",
    'value [kWh]': "valor absoluto da troca de calor [kWh]"
}

num_to_month = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

class HeatMap:
    def __init__(self, df: pd.DataFrame, target_type: str, zones: list, months: list, cbar_orientation: str, filename: str, values: str, lang: str, annotate: bool, separate_zones: bool, fmt: int = 2, sizefont: float = 10, tight: bool = False):
        self.df = df
        self.target_type = target_type
        self.lang = lang
        self.separate_zones = separate_zones
        if self.lang == 'pt-BR':
            self.zone_lang = 'Zona'
            if self.target_type == 'convection':
                self.target_type_lang = 'convecção'
            elif self.target_type == 'surface':
                self.target_type_lang = 'superfície'
        else:
            self.zone_lang = 'Zone'
            self.target_type_lang = self.target_type
        self.filename = filename
        self.annotate = annotate
        self.fmt = f'.{fmt}f'
        self.values = values
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
                self.title = f'HeatMap of {self.target_type_lang}' if self.lang == "en-US" else f'Mapa de calor de {self.target_type_lang}'
        match self.months:
            case 0:
                pass
            case _:
                self.df = self.df.loc[self.df['month'].isin(self.months)]
        if self.target_type == 'surface' and not self.separate_zones:
            self.df['zone'] = self.df.apply(lambda row: f'{row["zone"]}|{row["flux"]}', axis=1)
        if self.cbar_orientation in ['top', 'bottom']:
            self.cbar_kws = {"location": self.cbar_orientation, 'shrink': 0.5}
            self.tight = False
        else:
            self.cbar_kws = {"location": self.cbar_orientation}
            self.tight = tight

    def plot_heatmap(self, data, ax, title, cbar_ax=None, month_plot: bool = False):
        colors = ["#FFFFFF", "#496DDB", "#00CC66", "#FFFF00", "#F98016", "#F2002B"] if self.target_type == 'convection' else ["#FFFFFF","#A8DADC","#1D3557","#FFBA49","#EC9A9A","#D13440"]
        cmap = LinearSegmentedColormap.from_list('Custom_cmap', colors)
        heatmap = sns.heatmap(data=data, vmax=self.max_val, annot=self.annotate, fmt=self.fmt, vmin=self.min_val, cmap=cmap, linewidths=0, xticklabels=True, yticklabels=True, cbar_ax=cbar_ax, cbar_kws=self.cbar_kws, ax=ax)
        heatmap.set_xlabel('')
        heatmap.set_ylabel('Heat Exchange' if self.lang == 'en-US' else "Trocas de calor")
        heatmap.set_title(title, fontsize=12)
        if cbar_ax is None:
            heatmap.collections[0].colorbar.set_label(self.cbar_name)
        heatmap.tick_params(left=False, bottom=True)
        if self.separate_zones and self.target_type != 'surface':
            ax.set_xticklabels([])
        else:
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontsize=self.sizefont)
        ax.set_yticklabels(ax.get_yticklabels(), fontsize=self.sizefont)
        if self.target_type == 'surface' or month_plot:
            labels = ax.get_xticklabels()
            flux_list = []
            months_list = []
            splited = []

            match (self.target_type, month_plot, self.separate_zones):
                case ('surface', True, False):
                    flux_names = [label.get_text().split('|')[1].split('?')[0] for label in labels]
                    flux_list = [surfaces_rename.get(flux, flux) for flux in flux_names]
                    splited = [label.get_text().split('|') for label in labels]
                    splited = [[name[0], name[1].replace('?', ' ')] for name in splited]
                    try:
                        splited = [[name[0], name[1].replace(name[1].split(' ')[0], surfaces_rename[name[1].split(' ')[0]])] for name in splited]
                    except KeyError:
                        splited = [[name[0], name[1].title()] for name in splited]

                case ('surface', True, True):
                    flux_names = [label.get_text().split('|')[1].split('?')[0] for label in labels]
                    flux_list = [surfaces_rename.get(flux, flux) for flux in flux_names]
                    months_num = [label.get_text().split('|')[1].split('?')[1] for label in labels]
                    months_list = [num_to_month.get(int(num)) for num in months_num]
                    splited = [label.get_text().split('|') for label in labels]
                    splited = [[name[0], name[1].replace('?', ' ')] for name in splited]
                    try:
                        splited = [[name[0], name[1].replace(name[1].split(' ')[0], surfaces_rename[name[1].split(' ')[0]])] for name in splited]
                    except KeyError:
                        splited = [[name[0], name[1].title()] for name in splited]

                case ('surface', False, _):
                    splited = [label.get_text().split('|') for label in labels]
                    flux_names = [label.get_text().split('|')[1].split('?')[0] for label in labels]
                    flux_list = [surfaces_rename.get(flux, flux) for flux in flux_names]
                    try:
                        splited = [[name[0], name[1].replace(name[1], surfaces_rename[name[1]])] for name in splited]
                    except KeyError:
                        splited = [[name[0], name[1].title()] for name in splited]

                case (_, True, _):
                    splited = [label.get_text().split('?') for label in labels]

            new_labels = [name[0] for name in splited]
            ax.set_xticklabels(new_labels, rotation=45, fontsize=self.sizefont)
            return flux_list, months_list

    def annual(self):
        if self.separate_zones:
            unique_zones = self.df['zone'].unique()
            num_zones = len(unique_zones)
            num_cols = 2
            num_rows = math.ceil(num_zones / num_cols)

            fig, axes = plt.subplots(num_rows, num_cols, figsize=(16, 6 * num_rows), sharex=False)
            axes = axes.flatten()

            if self.cbar_orientation in ['right', 'left']:
                cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7]) if self.cbar_orientation == 'right' else fig.add_axes([0.03, 0.15, 0.02, 0.7])
            else:
                cbar_ax = fig.add_axes([0.15, 0.85, 0.7, 0.02]) if self.cbar_orientation == 'top' else fig.add_axes([0.15, 0.03, 0.7, 0.02])

            if self.target_type == 'convection':
                for ax, zone in zip(axes, unique_zones):
                    zone_data = self.df[self.df['zone'] == zone]
                    zone_pivot = zone_data.pivot_table(index='gains_losses', columns='zone', values=self.values).fillna(0)
                    zone_pivot = self.order_sign(zone_pivot)
                    zone_parts = zone.split("|")
                    zone_title = zone_parts[0] if isinstance(zone_parts, list) else zone
                    title = f'{self.title} - {zone_title}'
                    self.plot_heatmap(zone_pivot, ax, title, cbar_ax=cbar_ax)
            else:
                for ax, zone in zip(axes, unique_zones):
                    zone_data = self.df[self.df['zone'] == zone]
                    zone_data['zone'] = zone_data.apply(lambda row: f'{row["zone"]}|{row["flux"]}', axis=1)
                    zone_pivot = zone_data.pivot_table(index='gains_losses', columns='zone', values=self.values).fillna(0)
                    zone_pivot = self.order_sign(zone_pivot)
                    zone_parts = zone.split("|")
                    zone_title = zone_parts[0] if isinstance(zone_parts, list) else zone
                    title = f'{self.title} - {zone_title}'
                    flux_type, _ = self.plot_heatmap(zone_pivot, ax, title, cbar_ax=cbar_ax)
                    print("\n\n\n")
                    print(f"{flux_type =}")
                    bottom_labels = [label.get_text() for label in ax.get_xticklabels()]
                    print(f"{bottom_labels =}")
                    print("\n\n\n")
                    top_labels = [flux_type.pop(0) for _ in bottom_labels if flux_type]
                    ax.set_xticks(ax.get_xticks())
                    ax.set_xticklabels(top_labels, rotation=45, fontsize=self.sizefont)

            for i in range(len(unique_zones), len(axes)):
                fig.delaxes(axes[i])

            plt.subplots_adjust(hspace=0.6, wspace=0.4)
            fig.suptitle(self.title, fontsize=16)

            cbar = fig.colorbar(axes[0].collections[0], cax=cbar_ax, orientation='horizontal' if self.cbar_orientation in ['top', 'bottom'] else 'vertical')
            cbar.set_label(self.cbar_name)
            cbar.outline.set_visible(False)

            if self.tight:
                plt.tight_layout(rect=[0, 0, 1, 0.96])

            plt.subplots_adjust(top=0.85)

            plt.savefig(f"output/{self.filename}.png", format="png", dpi=300)
        else:
            self.df = self.df[['gains_losses', 'zone', self.values]].pivot_table(index='gains_losses', columns='zone', values=self.values).fillna(0)
            if self.target_type == 'surface':
                flux_type = [zone.split('|')[1] for zone in self.df.columns]
                flux_type = [surfaces_rename.get(flux, flux) for flux in flux_type]
            self.df = self.order_sign(self.df)

            plt.figure(figsize=(16, 9))
            plt.grid(True)
            self.plot_heatmap(self.df, plt.gca(), self.title)

            if self.target_type == 'surface':
                ax = plt.gca()
                bottom_labels = [label.get_text() for label in ax.get_xticklabels()]
                top_labels = [flux_type.pop(0) for _ in bottom_labels]
                ax.set_xticks(ax.get_xticks())
                ax.set_xticklabels(bottom_labels, rotation=45, fontsize=self.sizefont)
                ax_secondary = ax.twiny()
                ax_secondary.set_xticks(ax.get_xticks())
                ax_secondary.set_xticklabels(top_labels, rotation=45, fontsize=self.sizefont)

            if self.tight:
                plt.tight_layout(rect=[0, 0, 1, 0.96])

            plt.subplots_adjust(top=0.85)

            plt.savefig(f"output/{self.filename}.png", format="png", dpi=300)

    def monthly(self):
        if self.separate_zones:
            unique_zones = self.df['zone'].unique()
            num_zones = len(unique_zones)
            num_cols = 1 if self.target_type == 'surface' else 2
            num_rows = math.ceil(num_zones / num_cols)

            fig_width = 28 if self.target_type == 'surface' else 16
            fig, axes = plt.subplots(num_rows, num_cols, figsize=(fig_width, 6 * num_rows), sharex=False)
            axes = axes.flatten()

            if self.cbar_orientation in ['right', 'left']:
                cbar_ax = fig.add_axes([0.93, 0.15, 0.02, 0.7]) if self.cbar_orientation == 'right' else fig.add_axes([0.05, 0.15, 0.02, 0.7])
            else:
                cbar_ax = fig.add_axes([0.15, 0.93, 0.7, 0.02]) if self.cbar_orientation == 'top' else fig.add_axes([0.15, 0.05 if self.target_type == 'convection' else 0.03, 0.7, 0.02])

            if self.target_type == 'convection':
                for ax, zone in zip(axes, unique_zones):
                    zone_data = self.df[self.df['zone'] == zone]
                    zone_pivot = zone_data.pivot_table(index='gains_losses', columns='month', values=self.values).fillna(0)
                    zone_pivot.columns = [num_to_month[int(col)] for col in zone_pivot.columns]
                    self.order_sign(zone_pivot)
                    title = f'{self.title} - {zone}'
                    flux_type, _ = self.plot_heatmap(zone_pivot, ax, title, cbar_ax=cbar_ax, month_plot=True)
                    ax.set_xticklabels(zone_pivot.columns, rotation=45, fontsize=self.sizefont)

            else:
                for ax, zone in zip(axes, unique_zones):
                    zone_data = self.df[self.df['zone'] == zone]
                    zone_data['zone'] = zone_data.apply(lambda row: f'{row["zone"]}|{row["flux"]}?{row["month"]}', axis=1)
                    zone_pivot = zone_data.pivot_table(index='gains_losses', columns='zone', values=self.values, sort=False).fillna(0)
                    zone_pivot = self.order_sign(zone_pivot)
                    zone_parts = zone.split("|")
                    zone_title = zone_parts[0] if isinstance(zone_parts, list) else zone
                    title = f'{self.title} - {zone_title}'
                    flux_type, months_list = self.plot_heatmap(zone_pivot, ax, title, cbar_ax=cbar_ax, month_plot=True)
                    ax_secondary = ax.twiny()
                    ax.set_xticks(ax.get_xticks())
                    ax.set_xticklabels(flux_type, rotation=90, fontsize=self.sizefont)
                    ax_secondary.set_xticks(ax.get_xticks())
                    ax_secondary.set_xticklabels(months_list, rotation=90, fontsize=self.sizefont)


            for i in range(len(unique_zones), len(axes)):
                fig.delaxes(axes[i])

            plt.subplots_adjust(hspace=0.6 if self.target_type == "convection" else 1, wspace=0.4 if self.target_type=='convection' else 0)
            fig.suptitle(self.title, fontsize=16)

            cbar = fig.colorbar(axes[0].collections[0], cax=cbar_ax, orientation='horizontal' if self.cbar_orientation in ['top', 'bottom'] else 'vertical')
            cbar.set_label(self.cbar_name)
            cbar.outline.set_visible(False)

            if self.tight:
                plt.tight_layout(rect=[0, 0, 1, 0.96])

            plt.subplots_adjust(top=0.85)

            plt.savefig(f"output/{self.filename}.png", format="png", dpi=300)
        else:
            self.df['zone'] = self.df.apply(lambda row: f'{row["zone"]}?{row["month"]}', axis=1)
            self.df = self.df[['gains_losses', 'zone', self.values]].pivot_table(index='gains_losses', columns='zone', values=self.values).fillna(0)
            self.df = self.df[sorted(self.df.columns, key=self.month_number)]
            self.order_sign(self.df)
            self.df.columns = [f'{column.split("?")[0]}?{num_to_month[int(column.split("?")[1])]} ({column.split("?")[1]})' for column in self.df.columns]

            unique_months = sorted(self.df.columns.str.split('?').str[1].unique(), key=lambda x: list(num_to_month.values()).index(x.split(' ')[0]))
            num_months = len(unique_months)
            num_cols = 1 if self.target_type == 'surface' else 2
            num_rows = math.ceil(num_months / num_cols)

            fig, axes = plt.subplots(num_rows, num_cols, figsize=(16, 6 * num_rows), sharex=False)
            axes = axes.flatten()

            if self.cbar_orientation in ['right', 'left']:
                cbar_ax = fig.add_axes([0.93, 0.15, 0.02, 0.7]) if self.cbar_orientation == 'right' else fig.add_axes([0.05, 0.15, 0.02, 0.7])
            else:
                cbar_ax = fig.add_axes([0.15, 0.93, 0.7, 0.02]) if self.cbar_orientation == 'top' else fig.add_axes([0.15, 0.05, 0.7, 0.02])

            for ax, month in zip(axes, unique_months):
                month_data = self.df.filter(like=f'?{month.split(" ")[0]}', axis=1)
                title = f'{self.title} - {month.split(" ")[0]}' if self.lang == 'en-US' else f'{self.title} - {month.split(" ")[0]}'
                flux_list = self.plot_heatmap(month_data, ax, title, cbar_ax=cbar_ax, month_plot=True)
                if self.target_type == 'surface':
                    bottom_labels = [label.get_text() for label in ax.get_xticklabels()]
                    top_labels = [flux_list.pop(0) for _ in bottom_labels]
                    
                    ax.set_xticks(ax.get_xticks())
                    ax.set_xticklabels(bottom_labels, rotation=45, fontsize=self.sizefont)
                    
                    ax_secondary = ax.twiny()
                    ax_secondary.set_xlim(ax.get_xlim())
                    ax_secondary.set_xticks(ax.get_xticks())
                    ax_secondary.spines['top'].set_position(('outward', 0))
                    ax_secondary.set_xticklabels(top_labels, rotation=80, fontsize=self.sizefont)
                    

            for i in range(len(unique_months), len(axes)):
                fig.delaxes(axes[i])

            plt.subplots_adjust(hspace=0.8, wspace=0.4)
            fig.suptitle(self.title, fontsize=16)

            cbar = fig.colorbar(axes[0].collections[0], cax=cbar_ax, orientation='horizontal' if self.cbar_orientation in ['top', 'bottom'] else 'vertical')
            cbar.set_label(self.cbar_name)
            cbar.outline.set_visible(False)

            if self.tight:
                plt.tight_layout(rect=[0, 0, 1, 0.96])

            plt.subplots_adjust(top=0.94)

            plt.savefig(f"output/{self.filename}.png", format="png", dpi=300)

    def month_number(self, column_name):
        month_num = int(column_name.split('?')[1])
        return month_num
    
    def order_sign(self, df):
        df_plus = df[[sign[-1] == '+' for sign in df.index]]
        df_mins = df[[sign[-1] == '-' for sign in df.index]]
        return pd.concat([df_plus, df_mins], axis=0)
    

class BarPlot:
    def __init__(self, data: pd.DataFrame, target_type: str, filename: str, lang: str, all_in_one: bool, zones: list = "All zones", months: list = "All year", values: str = "value [kWh]", tight: bool = False):
        self.data = data
        self.zones = zones
        self.months = months
        self.filename = filename
        self.all_in_one = all_in_one
        self.values = values
        self.lang = lang
        self.y_name = self.values if self.lang == 'en-US' else values_en_to_pt[self.values]
        self.tight = tight
        self.target_type = target_type
        if self.lang == 'pt-BR':
            self.zone_lang = 'Zona'
            if self.target_type == 'convection':
                self.target_type_lang = 'convecção'
            elif self.target_type == 'surface':
                self.target_type_lang = 'superfície'
        else:
            self.zone_lang = 'Zone'
            self.target_type_lang = self.target_type
        match self.zones:
            case 0:
                self.data = self.data.loc[self.data['zone'] != 'EXTERNAL']
                self.title = f'Total BarPlot of {self.target_type_lang}' if self.lang == 'en-US' else f'Gráfico de barras total de {self.target_type_lang}'
            case _:
                self.data = self.data.loc[self.data['zone'].isin(self.zones)]    
                self.title = f'BarPlot of {self.target_type_lang}' if self.lang == 'en-US' else f'Gráfico de barras de {self.target_type_lang}'
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

        if self.all_in_one:
            bar_colors = self.data['zone'].map(color_map)
            plt.figure(figsize=(16, 9))
            plt.grid(True)
            bars = plt.bar(self.data['gains_losses'], self.data[self.values], color=bar_colors)
            plt.title(self.title)
            plt.ylabel(self.y_name)
            plt.xlabel('Gains and Losses' if self.lang == 'en-US' else "Ganhos e Perdas")
            plt.xticks(rotation=25)
            plt.axhline(0, color='red', linewidth=2)

            handles = [plt.Rectangle((0,0),1,1, color=color_map[zone]) for zone in unique_zones]
            labels = [zone for zone in unique_zones]
            plt.legend(handles, labels, title='Zones' if self.lang == 'en-US' else 'Zonas', loc='upper right')

            if self.tight:
                plt.tight_layout(rect=[0, 0, 1, 0.96])

            plt.savefig(f"output/{self.filename}.png", format="png", dpi=300)
        else:
            num_zones = len(unique_zones)
            num_cols = 2 
            num_rows = math.ceil(num_zones / num_cols)

            fig, axes = plt.subplots(num_rows, num_cols, figsize=(20, 5 * num_rows), sharex=False)
            axes = axes.flatten()

            for ax, zone in zip(axes, unique_zones):
                zone_data = self.data[self.data['zone'] == zone]
                bar_colors = zone_data['zone'].map(color_map)
                bars = ax.bar(zone_data['gains_losses'], zone_data[self.values], color=bar_colors)
                ax.set_title(f'{self.title} - {self.zone_lang} {zone}', fontsize=12)
                ax.set_ylabel(self.y_name)
                ax.axhline(0, color='red', linewidth=2)
                ax.grid(True)
                ax.set_xticks(range(len(zone_data['gains_losses'])))
                ax.set_xticklabels(zone_data['gains_losses'], rotation=45, ha='right')

            for i in range(len(unique_zones), len(axes)):
                fig.delaxes(axes[i])

            handles = [plt.Rectangle((0,0),1,1, color=color_map[zone]) for zone in unique_zones]
            labels = [zone for zone in unique_zones]
            fig.legend(handles, labels, title='Zones' if self.lang == 'en-US' else 'Zonas', loc='upper right')

            plt.subplots_adjust(hspace=0.6, wspace=0.4)
            fig.suptitle(self.title, fontsize=16)

            if self.tight:
                plt.tight_layout(rect=[0, 0, 1, 0.96])

            plt.savefig(f"output/{self.filename}.png", format="png", dpi=300)