import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Dados simulados para reproduzir o gráfico
data = {
    'gains_losses': ['Carga Interna', 'Paredes Internas', 'Paredes Externas', 'Piso','Cobertura', 'Portas', 'Janelas', 'Aquecimento', 'Refrigeração'],
    'value [kWh]': [500, 1000, 3000, 1500, 500, 250, 250, 0, -5000]
}

# Criando o DataFrame
df = pd.DataFrame(data)

# Definindo as cores para cada barra
colors = ['#ffff99', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c','#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a']

# Criando o gráfico de barras
# plt.figure(figsize=(12, 6))
plt.grid(True)
bars = plt.bar(df['gains_losses'], df['value [kWh]'], color=colors)

# Adicionando título e rótulos
plt.title('Balanço Térmico no Ar do Dormitório 2- Ar Condicionado (AC) 100% das Horas no Ano')
plt.ylabel('Ganhos e Perdas no Ar da Zona [kWh]')
plt.xlabel('Ganhos e Perdas')

# Exibindo o gráfico
plt.show()