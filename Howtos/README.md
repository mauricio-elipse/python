How to's...
=======

# Exemplos de gr�ficos polares

Aplicando as fun��es do arquivo windPlots a s�ries temporais de dire��o do vento e sua velocidade.
Polar Scatter Wind Direction
![polarScatterWindDirection](https://github.com/mauricio-elipse/python/tree/master/Howtos/figs/polarScatterWindDirection.PNG)
Wind Direction Pie Chart
![windDirectionPieChart](https://github.com/mauricio-elipse/python/tree/master/Howtos/figs/windDirectionPieChart.PNG)


# Exemplos de Interpola��o, ajuste de curvas e c�lculo de �reas

Exemplo pr�tico de utiliza��o de diversas fun��es do scipy: interpola��o, ajuste de curvas e c�lculos de �reas (integra��o).
Neste exemplo s�o comparadas as curvas da velocidade do vento com a corrspondente pot�ncia gerada por um aerogerador e calculada a �rea entre elas.
A curva de refer�ncia � obtida a partir de dados em um arquivo .CSV, enquanto a outra � determinada a partir de dados medidos.
As fun��es foram implementadas para fins did�ticos, exemplificando  passo a passo este caso pr�tico. A fun��o showResults apresenta os resultados ao final:
![Aerogenerator: Speed vs Power chart](https://github.com/mauricio-elipse/python/tree/master/Howtos/figs/aerogeneratorSpeedPower.png)
A sequ�ncia de execu��o sugerida est� no arquivo: ![Script aerogenerator: aerogen.txt](https://github.com/mauricio-elipse/python/tree/master/Howtos/misc/aerogen.txt)


# Exemplos de implementa��es de filtros de ru�dos de medida - uso por linha de comando.

Comandos a serem executados no console Python do EPM Dataset Analysis aplicados uma vari�vel de processo de nome *cpu*:

> import noiseFilteringExamples as nfe

> y1 = nfe.filter1st(cpu, 1, 1)

> plotValues('y1', y1)

> y2 = nfe.filtSignal(cpu)

> plotValues('y2', y2)

> y3 = nfe.filtMeanEpm(cpu, 12 )

> plotValues('y3', y3)

Noise Filtering Examples (EPM Datset Analysis)
![Noise Filtering Examples](https://github.com/mauricio-elipse/python/tree/master/Howtos/figs/noiseFilteringExample.PNG)
