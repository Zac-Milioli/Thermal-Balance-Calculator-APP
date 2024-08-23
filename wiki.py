from utils.src import *

clear_cache()
clear_output()
st.write('#')
st.sidebar.write("")
st.sidebar.header("**CALCULADORA DE BALANÇO TÉRMICO**")
st.sidebar.divider()
st.sidebar.image(r"utils/lab_banner.png", width=300)
st.sidebar.title("")
st.sidebar.markdown("Ferramenta desenvolvida por [Zac Milioli](https://github.com/Zac-Milioli)")
st.sidebar.markdown("Teoria elaborada por Dra. [Letícia Eli](https://www.linkedin.com/in/letícia-gabriela-eli-347063b0)")
add_page_title(layout='wide')


st.markdown("""
# Como Utilizar a Ferramenta Thermal Balance Calculator

## O Objetivo da Ferramenta

A ferramenta Thermal Balance Calculator tem como objetivo demonstrar as trocas de calor que ocorrem nos ambientes de uma edificação, assim como calcular o valor do Heat Exchange Index (HEI), índice desenvolvido no artigo científico [https\://doi.org/10.1016/j.buildenv.2024.111606](https\://doi.org/10.1016/j.buildenv.2024.111606).

O balanço térmico é o que rege as interações térmicas que ocorrem nos ambientes de uma edificação e, portanto, determina a temperatura interna, influenciando na demanda por ar-condicionado, por exemplo. Dessa forma, compreender o balanço térmico e mensurar as trocas de calor pode auxiliar na tomada de decisão de quais estratégias construtivas podem melhorar o desempenho térmico de uma edificação.

## Tipos de Balanço Térmico

Esta ferramenta calcula dois tipos de balanço térmico\:

1. **Balanço térmico no ar (convecção/convection)**\: Analisa as trocas de calor que ocorrem entre o ar do ambiente e as suas superfícies, cargas internas, ventilação natural e sistema mecânico de climatização.
2. **Balanço térmico na superfície/surface (convecção, condução e radiação)**\: Analisa quais são as trocas de calor existentes em cada superfície opaca do ambiente. 

É possível obter cada um dos balanços térmicos para ambientes naturalmente ventilados, condicionados artificialmente e híbridos. 

Para garantir que o balanço térmico tenha sido calculado corretamente, a soma de todas as trocas de calor deve ser igual a zero (0) ou próxima a zero (0). Em casos com ventilação natural, o balanço térmico resultante não é zero (0).

""")

st.warning("Essa calculadora foi desenvolvida considerando simulações no EnergyPlus versão 22.2. Para outras versões, os cálculos podem não funcionar corretamente, em especial para versões anteriores à 9.4.")

st.markdown("""
## Configurações Importantes

### Permitir mais do que 250 colunas no arquivo .csv

Na simulação é importante permitir que o arquivo .csv com os dados de saída tenha mais do que 250 colunas. Para fazer isso, basta seguir os passos abaixo\:

""")

with st.container(border=True):
    st.markdown("""
    ### Passo 1\:
                
    No EP-Lauch, clicar em View e depois em Options.
    """)

    cols = st.columns([1,3,1])
    cols[1].image("utils/Passo 1.png")

    st.markdown("""
    ### Passo 2\:
                
    Em Options, clicar em Miscellaneous e marcar a opção Allow More Than 250 Columns.
    """)

    cols = st.columns([1,3,1])
    cols[1].image("utils/Passo 2.png")

    st.title("")
    st.markdown("""Pronto, estará tudo certo para obter os resultados.""")
    st.title("")

st.title("")

st.markdown("""
### Solicitar um arquivo de resultado .sql da simulação

Para a análise de ambos os balanços térmicos é necessário solicitar um arquivo .sql com os dados da simulação.

Para isso, deve-se criar um objeto na classe de objetos **Output\:SQLite**, conforme imagem abaixo.

""")

cols = st.columns([1,3,1])
cols[1].image("utils/variaveis_SQL.png")

st.title("")
st.title("")

st.markdown("""
# UTILIZANDO A FERRAMENTA THERMAL BALANCE CALCULATOR

Para ambos os balanços térmicos, a ferramenta thermal balance calculator tem como resultado as trocas de calor do balanço térmico, assim como o Heat Exchange Index (HEI). Estes resultados são obtidos na aba “Calculadora”. Após a execução desta aba, é possível baixar um arquivo compactado com os arquivos .csv de resultados.

Após a execução da análise na aba “Calculadora”, é possível criar gráficos. Na aba “Plotar Dados (Matplotlib)” é possível obter os gráficos para as trocas de calor e na aba “Plotar Dados (Plotly)” para o HEI. Para a execução dos gráficos é necessário inserir o arquivo .csv obtido na aba “Calculadora”.

## A ABA “CALCULADORA”

Nesta aba deve ser inserido inicialmente o arquivo .sql obtido na simulação. Após a submissão desse arquivo na ferramenta, aparecem três campos que devem ser preenchidos\:

1. **Selecione as zonas**\: Se não for preenchido, a calculadora analisará todas as zonas térmicas presentes no arquivo de simulação, mas é possível escolher quais o usuário quer analisar. Isso evita que a calculadora fique sobrecarregada e também auxilia na posterior visualização.
2. **Selecione o tipo**\: Deve ser preenchido qual o balanço térmico desejado. Para o balanço térmico no ar (convecção), preencher **convection**; para o balanço térmico na superfície (convecção, condução e radiação), preencher **surface**.
3. **Selecione um período**\: Deve ser preenchido para indicar qual o tempo de análise desejado. Há três opções\: **annual** para o somatório anual das trocas de calor, **monthly** para o somatório mensal e **daily** para o somatório diário. Para o diário é calculado o somatório considerando o dia com a máxima e com a mínima temperatura externa, além dos dias com a maior e menor amplitude térmica.

Definidos os três campos acima, deve ser inserido o arquivo .csv da simulação para a obtenção do balanço térmico desejado. Abaixo quais os dados de saída a serem incluídos neste .csv para cada balanço térmico.

## DADOS DE SAÍDA A SEREM SOLICITADOS NA SIMULAÇÃO

Além do arquivo .sql, cada balanço térmico exige determinados dados de saída da simulação para que sejam calculadas as trocas de calor e, posteriormente, o HEI.

Nos próximos itens são exemplificados quais os dados exigidos para cada balanço térmico. Se o usuário quiser analisar ambos os balanços térmicos, é possível incluir na simulação os dados de saída das duas análises.

Todos os dados de saída devem ser incluídos na classe de objetos **Output\\:Variable** e serem solicitados na frequência de tempo horária, ou seja, o campo **Reporting Frequency** deve estar preenchido como **Hourly**.

Caso a edificação a ser analisada tenha muitas zonas térmicas e superfícies, é viável que seja informado o nome das zonas térmicas e das superfícies que serão analisadas. Para isso, no campo **Key Value** dos objetos da classe **Output\:Variable**, deverá ser inserido o nome exato da zona térmica, nos dados de saída de zonas térmicas (ver Tabela 1), e o nome exato das superfícies dessa zona térmica nos dados de saída referentes às superfícies. Esse passo pode ser trabalhoso, mas no caso de edificações grandes, irá reduzir o tempo de processamento da calculadora e o tamanho do arquivo .csv obtido na simulação.

### Dados de saída para o balanço térmico no ar (convecção) - convection

**Considerações importantes**\:

Para edificações naturalmente ventiladas, esta calculadora considera a simulação pelos objetos do Air Flow Network. Caso tenham sido utilizados Cracks para simular uma infiltração constante ou outro tipo de ventilação natural ou mecânica, esses não são considerados no balanço térmico desta calculadora.

Para edificações condicionadas artificialmente, esta calculadora considera somente a simulação do sistema ideal de carga térmica (Ideal Loads). Caso tenha sido modelado outro tipo de sistema, é preciso garantir que sejam obtidos os dados de saída **Zone Air System Sensible Heating Rate** e **Zone Air System Sensible Cooling Rate**.

**Dados de saída**\:

Ainda na simulação computacional, o usuário deverá incluir no seu arquivo os seguintes dados de saída na classe de objetos **Output\:Variable**\:

Tabela 1 - Dados de saída para a análise do balanço térmico no ar

            
| Variable Name                                        | Descrição do resultado                                                                                                            |
|------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| Zone Total Internal Convective Heating Rate          | É obtido para cada zona térmica. Representa os ganhos de calor por convecção devido às cargas internas (iluminação, equipamentos e pessoas). O resultado da troca de calor é sempre positivo, indicando que há ganho de calor por essa troca. |
| AFN Zone Ventilation Sensible Heat Gain Rate         | É obtido para cada zona térmica. Representa o ganho de calor sensível devido à ventilação natural pelas aberturas externas. O resultado da troca de calor é sempre positivo, indicando que há ganho de calor por essa troca. |
| AFN Zone Ventilation Sensible Heat Loss Rate         | É obtido para cada zona térmica. Representa a perda de calor sensível devido à ventilação natural pelas aberturas externas. O resultado da troca de calor é sempre negativo, indicando que há perda de calor por essa troca. |
| AFN Zone Mixing Sensible Heat Gain Rate              | É obtido para cada zona térmica. Representa o ganho de calor sensível devido à troca de ar entre os ambientes adjacentes. O resultado da troca de calor é sempre positivo, indicando que há ganho de calor por essa troca. |
| AFN Zone Mixing Sensible Heat Loss Rate              | É obtido para cada zona térmica. Representa a perda de calor sensível devido à troca de ar entre os ambientes adjacentes. O resultado da troca de calor é sempre negativo, indicando que há perda de calor por essa troca. |
| Zone Air System Sensible Heating Rate                | É obtido para cada zona térmica. Representa a carga térmica sensível a ser adicionada ao ambiente pelo sistema mecânico de climatização. O resultado da troca de calor é sempre positivo, indicando que há ganho de calor por essa troca. |
| Zone Air System Sensible Cooling Rate                | É obtido para cada zona térmica. Representa a carga térmica sensível a ser removida do ambiente pelo sistema mecânico de climatização. O resultado da troca de calor é sempre negativo, indicando que há perda de calor por essa troca. |
| Surface Inside Face Convection Heat Gain Rate        | É obtido para cada superfície. Representa a troca de calor por convecção entre o ar da zona térmica e a superfície. O resultado da troca de calor pode ser positivo ou negativo. Se positivo, indica que essa superfície está inserindo calor no ar da zona térmica. |
| Surface Window Inside Face Frame and Divider Zone Heat Gain Rate | É obtido para cada superfície com esquadria. Representa as trocas de calor que ocorrem entre as esquadrias e o ar da zona térmica. O resultado da troca de calor pode ser positivo ou negativo. Se positivo, indica que essa superfície está inserindo calor no ar da zona térmica. |
""")

st.title("")

st.markdown("""
Os nomes presentes na coluna Variable Name da tabela acima devem ser colocados no campo Variable Name. 
Preencher o Reporting Frequency como Hourly para obter os valores horários. 

Abaixo um exemplo de preenchimento da classe Output\:Variable. Devem ser preenchidos no mínimo nove objetos, um para cada dado de saída da Tabela 1.

""")

cols = st.columns([1,15,1])
cols[1].image("utils/Variaveis_BT_ar.png")

st.title('')

st.markdown("""
Caso a sua edificação tenha muitas zonas térmicas e superfícies, sugerimos que você informe o nome das zonas térmicas e das superfícies que você deseja analisar.

Para isso, no campo Key Value dos objetos da classe Output\:Variable, você irá inserir o nome exato da zona térmica, nos dados de saída de zonas térmicas (ver Tabela 1), e o nome exato das superfícies dessa zona térmica nos dados de saída referentes às superfícies. Esse passo pode ser trabalhoso, mas no caso de edificações grandes, irá reduzir o tempo de processamento da calculadora e o tamanho do arquivo .csv.

## Dados de saída para o balanço térmico na superfície (convecção, condução e radiação) - surface

Ainda na simulação computacional, o usuário deverá incluir no seu arquivo os seguintes dados de saída na classe de objetos Output\:Variable:

### Tabela 2 - Dados de saída para a análise do balanço térmico na superfície

| Variable Name                                         | Descrição do resultado                                                                                                             |
|-------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| Surface Inside Face Convection Heat Gain Rate         | É obtido para cada superfície. Representa a troca de calor por convecção entre o ar da zona térmica e a superfície. O resultado da troca de calor pode ser positivo ou negativo. Se positivo, indica que essa superfície está removendo calor do ar da zona térmica.  |
| Surface Inside Face Conduction Heat Transfer Rate     | É obtido para cada superfície. Representa a troca de calor por condução entre o ar da zona térmica e a superfície. O resultado da troca de calor pode ser positivo ou negativo. Se positivo, indica que essa superfície está recebendo calor do interior do sistema construtivo. |
| Surface Inside Face Solar Radiation Heat Gain Rate    | É obtido para cada superfície. Representa a radiação solar absorvida pela superfície. O resultado da troca de calor é sempre positivo. |
| Surface Inside Face Lights Radiation Heat Gain Rate   | É obtido para cada superfície. Representa a radiação absorvida pela superfície e advinda da iluminação instalada. O resultado da troca de calor é sempre positivo. |
| Surface Inside Face Net Surface Thermal Radiation Heat Gain Rate | É obtido para cada superfície. Representa a troca de calor por radiação entre as superfícies da zona térmica. O resultado da troca de calor pode ser positivo ou negativo. Se positivo, indica que essa superfície está absorvendo calor por radiação de outras superfícies. |
| Surface Inside Face Internal Gains Radiation Heat Gain Rate | É obtido para cada superfície. Representa a radiação absorvida pela superfície e advinda das cargas internas. O resultado da troca de calor é sempre positivo. |
""")

st.title("")

st.markdown("""
Os nomes presentes na coluna Variable Name da tabela acima devem ser colocados no campo Variable Name. 
Preencher o Reporting Frequency como Hourly para obter os valores horários.

Abaixo um exemplo de preenchimento da classe Output\:Variable. Devem ser preenchidos no mínimo seis objetos, um para cada dado de saída da Tabela 2.
""")

cols = st.columns([1,15,1])
cols[1].image("utils/variaveis_BT_surface.png")

st.title('')

st.markdown("""
Caso a sua edificação tenha muitas zonas térmicas e superfícies, sugerimos que você informe o nome das zonas térmicas e das superfícies que você deseja analisar.

Para isso, no campo Key Value dos objetos da classe Output\:Variable, você irá inserir o nome exato da zona térmica, nos dados de saída de zonas térmicas (ver Tabela 1), e o nome exato das superfícies dessa zona térmica nos dados de saída referentes às superfícies. Esse passo pode ser trabalhoso, mas no caso de edificações grandes, irá reduzir o tempo de processamento da calculadora e o tamanho do arquivo .csv.

# GRÁFICOS

Além do arquivo .csv com os dados numéricos do balanço térmico, é possível obter gráficos com o valor das trocas de calor e do Heat Exchange Index (HEI). 
Para isso, atualmente, pode ser usado o criador automático de gráficos com “Matplotlib” que fornece gráficos no formato mapa de calor (heatmap).

Para o funcionamento dos gráficos de mapa de calor o usuário deverá inserir o arquivo .csv obtido na aba “Calculadora” e escolher dentre as opções abaixo:

- **Período**\: Da mesma forma que na aba “Calculadora” existem três períodos a serem escolhidos\: annual, monthly e daily. É importante destacar que caso o arquivo inserido seja annual, deverá ser escolhido o período annual para a criação do gráfico, se for mensal, o período monthly e diário o período daily.
- **Zonas**\: Devem ser escolhidas as zonas térmicas a serem analisadas. Importante destacar que devem ser escolhidas zonas presentes no arquivo .csv inserido na aba “Plotar Dados”.
- **Tipo**\: Se o .csv inserido é do balanço térmico de convecção (convection) ou da superfície (surface).
- **Plotar**\: Neste campo o usuário informa se quer plotar o gráfico da troca de calor ou do Heat Exchange Index (HEI). Se for das trocas de calor, deverá inserir Heat Exchange Values, se for do HEI, Heat Exchange Index.
- **Localização da barra de cores**\: O usuário pode definir onde a legenda será inserida no gráfico.
- **Insira o número de casas após a vírgula desejados**\: Esse é o arredondamento dos valores a serem indicados no **gráfico**(apenas visual). -1 é valor padrão que serve para não exibir os valores.
- **Meses**\: Se a análise escolhida for Monthly, é possível colocar no gráfico todos os meses (não é recomendado, o gráfico fica com a formatação ruim) ou definir quais meses devem ser analisados.
- **Tight layout**\: Serve para forçar o mapa de calor gerado a ser "espremido" o máximo possível (apenas visual). Uso não recomendado para mapas de calor com muitas informações pois pode haver sobreposição de legendas. No geral, recomenda-se não utilizar essa opção.
""")

st.title("")

st.markdown("""
Por fim, basta clicar em
""")

st.button("Criar Heatmap")

st.markdown("""
É possível desenvolver mais de um gráfico em sequência, basta inserir os arquivos .csv que desejar e escolher seus atributos normalmente. Toda vez que o botão de "Criar Heatmap" for pressionado o novo gráfico será adicionado à "Galeria de Heatmaps".
            
Caso seja necessário baixar, é possível também. Basta clicar no botão "Baixar Heatmaps" que um arquivo .zip com todos os gráficos gerados será entregue ao usuário. 
""")

st.markdown("""
# Teste a calculadora sem fazer simulações

Caso queira experimentar a calculadora antes de aplicar suas próprias simulações, preparamos alguns arquivos teste que podem ser usados para explorar as diferentes funções que esta calculadora oferece. Basta baixar, descompactar o arquivo e usar os CSV e SQL que foram disponibilizados. 
""")

col1, col2, col3 = st.columns(3)
with open(r'utils/Test Files.zip', 'rb') as f:
    bytes = f.read()
    col2.download_button(
        label="Baixar arquivos teste",
        data=bytes,
        file_name='Test Files.zip',
        mime='application/zip',
        use_container_width=True
    )