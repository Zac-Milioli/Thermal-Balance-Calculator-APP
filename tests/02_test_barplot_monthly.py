import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Dados simulados para reproduzir o gráfico
data = {
    'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    'Carga Interna': [50, 45, 48, 52, 55, 53, 56, 58, 60, 62, 61, 59],
    'Paredes Internas': [60, 58, 61, 64, 67, 65, 68, 70, 72, 73, 71, 69],
    'Paredes Externas': [200, 190, 195, 205, 210, 200, 215, 220, 225, 230, 220, 210],
    'Piso': [70, 65, 68, 72, 75, 70, 73, 76, 78, 80, 78, 76],
    'Cobertura': [20, 18, 19, 21, 22, 20, 23, 24, 25, 26, 24, 23],
    'Portas': [10, 9, 9.5, 10.5, 11, 10, 11.5, 12, 12.5, 13, 12.5, 12],
    'Janelas': [10, 9, 9.5, 10.5, 11, 10, 11.5, 12, 12.5, 13, 12.5, 12],
    'Aquecimento': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'Refrigeração': [-400, -380, -390, -410, -420, -400, -430, -440, -450, -460, -450, -440]
}

# Criando o DataFrame
df = pd.DataFrame(data)

# Definindo as cores para cada categoria
colors = ['#ffff99', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c','#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a']

# Plotando o gráfico de barras empilhadas
df.set_index('month').plot(kind='bar', stacked=True, color=colors, figsize=(14, 7))

# Adicionando título e rótulos
plt.title('Balanço Térmico no Ar do Dormitório 1 - Ar Condicionado (AC) 100% das Horas no Ano')
plt.ylabel('Ganhos e Perdas no Ar da Zona [kWh]')
plt.xlabel('Mês')

# Exibindo a legenda fora do gráfico
plt.grid(True)
plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))

# Exibindo o gráfico
plt.show()
