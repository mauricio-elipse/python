How to's...
=======

# Exemplos de gráficos polares

Aplicando as funções do arquivo windPlots a séries temporais de direção do vento e sua velocidade.
Polar Scatter Wind Direction
![polarScatterWindDirection](https://github.com/mauricio-elipse/python/tree/master/Howtos/figs/polarScatterWindDirection.PNG)
Wind Direction Pie Chart
![windDirectionPieChart](https://github.com/mauricio-elipse/python/tree/master/Howtos/figs/windDirectionPieChart.PNG)


# Exemplos de Interpolação, ajuste de curvas e cálculo de áreas

Exemplo prático de utilização de diversas funções do scipy: interpolação, ajuste de curvas e cálculos de áreas (integração).
Neste exemplo são comparadas as curvas da velocidade do vento com a corrspondente potência gerada por um aerogerador e calculada a área entre elas.
A curva de referência é obtida a partir de dados em um arquivo .CSV, enquanto a outra é determinada a partir de dados medidos.
As funções foram implementadas para fins didáticos, exemplificando  passo a passo este caso prático. A função showResults apresenta os resultados ao final:
![Aerogenerator: Speed vs Power chart](https://github.com/mauricio-elipse/python/tree/master/Howtos/figs/aerogeneratorSpeedPower.png)
A sequência de execução sugerida está no arquivo: ![Script aerogenerator: aerogen.txt](https://github.com/mauricio-elipse/python/tree/master/Howtos/misc/aerogen.txt)


# Exemplos de implementações de filtros de ruídos de medida - uso por linha de comando.

Comandos a serem executados no console Python do EPM Dataset Analysis aplicados uma variável de processo de nome *cpu*:

> import noiseFilteringExamples as nfe

> y1 = nfe.filter1st(cpu, 1, 1)

> plotValues('y1', y1)

> y2 = nfe.filtSignal(cpu)

> plotValues('y2', y2)

> y3 = nfe.filtMeanEpm(cpu, 12 )

> plotValues('y3', y3)

Noise Filtering Examples (EPM Datset Analysis)
![Noise Filtering Examples](https://github.com/mauricio-elipse/python/tree/master/Howtos/figs/noiseFilteringExample.PNG)
