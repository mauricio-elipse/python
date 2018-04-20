# -*- coding: utf-8 -*-
"""Elipse Plant Manager - EPM Processor - Basic functions
Copyright (C) 2017 Elipse Software.
Distributed under the MIT License.
(See accompanying file LICENSE.txt or copy at http://opensource.org/licenses/MIT)
"""


__author__ = u"Maurício"
__copyright__ = "Copyright 2018, Elipse Software"
__credits__ = [u"Renan", u"Lucas"]
__license__ = "MIT"
__version__ = "0.0.7"
__maintainer__ = u"Maurício"
__email__ = "mauricio@elipse.com.br"
__status__ = "Production"
__docformat__ = 'reStructuredText'


import sys
import os
import datetime
import pytz
import re
import json
import io
import mimetypes
import base64
import shutil
from pathlib import Path
import pdfkit
from collections import OrderedDict
import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt
plt.style.use('ggplot')
#plt.ioff()
from selenium import webdriver

# ****** <Import dos Módulos do EPM Processor> ******
import epmprocessor as epr
import epmwebapi as epm
# ****** </Import dos Módulos do EPM Processor> ******


#### ***** <Configurações globais> *****
_SERVERMACHINE = False  # Indica se é para rodar no servidor (=True)
_PRINTDEBUG = True  # Indica se é para imprimir outputs em modo de depuração
_USEREPOSITORY = True  # indica se é para usar o repositório do EPM Webserver ao invés de arquivos no disco
_PHANTOMPATH = r'C:\Programas\phantomjs\bin\phantomjs.exe'  # local onde está instalado o phantomjs
#### ***** </Configurações globais> *****



#### ***** <Módulos para o EPM Processor> *****
@epr.applicationMethod('DailyACPowerCost')
def mspDailyACPowerCost(session, tagACCompressor, tagACPowerCost, kWhFactor=2.1,  timeZone='Brazil/East'):
    """.. rubric:: DailyACPowerCost

    Função para validar:

        * parâmetros informados como escalares ou lista
        * R/W-RT em Basic Variables
        * Exceução de simulação em um site externo (via *web scraping*)
        * Tratamento automático de Time Zone

        Esta função estima o **custo diário** decorrente do uso do ar condicionado, utilizando para tanto um fator de
        conversão (*kWhFactor*) de período de compressor ligado em kWh. De posse deste valor, segue-se para a estimativa
        no site da concessionária de energia via *web scraping*. O período em que o ar condicionado ficou
        ligado é obtido através de uma consulta agregada do tipo **DurationInStateNonZero**
        (OPC Foundation [#f1]_ ), utilizando *ProcessInterval* de 24 horas (hard-coded).

                    :param session: objeto *session* do EPM Processor
                    :param tagACCompressor: Basic Variable (ou lista de BVs) para fazer consulta histórica
                    :param tagACPowerCost: Basic Variable (ou lista de BVs) para escrever os resultados (via *write*)
                    :param kWhFactor: fator para converter um período de compressor ligado em kWh (padrão é 2.1)
                    :param timeZone: localização da zona de tempo do EPM Server [#f2]_ (padrão é ''Brazil/East'')
                    :type session: epmprocessor.ScopeSession
                    :type tagACCompressor: epmprocessor.epm.epmdataobject.EpmDataObject (or collections.OrderedDict)
                    :type tagACPowerCost: epmprocessor.epm.epmdataobject.EpmDataObject (or collections.OrderedDict)
                    :type kWhFactor: float
                    :type timeZone: string
                    :returns: estado da execução (Sucesso=True | Falha=False)
                    :rtype: epmprocessor.ScopeResult
                    :raises: MyExceptionClass


                    .. rubric:: APPLICATION

                    Para testar uma *Application*, é preciso informar um *session/Time Event* qualquer (em UTC), uma vez
                    que ela irá calcular o valor do custo estimado para o dia anterior ao informado.

                    Os parâmetros *tagACCompressor* e *tagACPowerCost* podem ser escalares ou listas. No caso de lista,
                    é preciso que as variáveis de leitura e de escrita sejam informadas nas suas respectivas listas de
                    maneira pareada.

                    Exemplo: *[readVar01, readVar02, ...]* e *[writeVar01, writeVar02, ...]*


                    .. rubric:: PRODUCTION

                    Esta função não utiliza os parâmetros: *Range* e *Processes Interval*, o dia do evento é utilizado
                    como referência para fazer a consulta ao dia anterior completo, ou seja, 24h. O resultado da
                    estimativa de custo será escrito na variável (ou lista de variáveis) informada(s) no parâmetro
                    *tagACPowerCost* com o *Timestamp* correspondente ao dia anterior do event à meia-noite (UTC).


                    .. epigraph:: **EPM Event**

                        Evento deve ser necessariamente de 24h (um dia), uma vez que toda a lógica do código foi
                        desenvolvida com esta premissa.

                    .. epigraph:: **Production Rules**

                        Recomenda-se selecionar as opções *Enable error configuration* e *Abort retries on new event*,
                        com a opção de 3 retentativas em caso de falha, aguardando 1 minuto entre elas.

                    .. epigraph:: **Range**

                        Parâmetro ignorado pela função, pode ser informado qualquer valor que não será utilizado.

                    .. epigraph:: **Processes Interval**

                        Parâmetro ignorado pela função, pode ser informado qualquer valor que não será utilizado.


                    .. rubric:: SIMULATION
                        Idem *PRODUCTION*.



                    .. note::
                        Fator de custo considerando impostos 0.483170 set/2017.

                        Site onde é feita aconsulta: `Simulação kWh - <http://www.ceee.com.br/pportal/ceee/Component/ListValorConta.aspx?>`_


                    .. warning::
                        Não precisa informar SESSION!

                        Não é necessário informar **Range** e **Process Interval**.

                        Em **Productions** é preciso associar a um evento diário (24h).

                        Não é feita distinção entre execuções de : *TEST*, *PRODUCTION* e *SIMULATION*, ou seja
                        o resultado sempre será escrita em uma Basic Variable em caso de sucesso na execução.


                    .. todo::
                        Validar outras consistências das duas entradas (=s, size=s, etc.).


                    .. rubric:: Notas de rodapé

                    .. [#f1] `OPC Foundation <https://opcfoundation.org/>`_
                    .. [#f2] `Time Zone - pytz <http://pytz.sourceforge.net/>`_


                    .. Três linhas em branco!
                    |
                    |
                    |
                    """

    # Verifica se é dicionário ou não
    isOrderdDict = False
    if type(tagACCompressor) == OrderedDict:
        isOrderdDict = True
    if not isOrderdDict and not isinstance(tagACCompressor, epm.epmdataobject.EpmDataObject):
        raise MyExceptionClass(u'oops! Erro no tipo de tag informado - não é lista nem tag!!!')
    tz = pytz.timezone(timeZone)
    timeEventUTC = session.timeEvent.replace(tzinfo=pytz.UTC)
    timeEventLoc = timeEventUTC.astimezone(tz)
    timeDifference = timeEventLoc.utcoffset().total_seconds()
    _localTime = datetime.timedelta(hours=abs(timeDifference/3600))
    processInterval = datetime.timedelta(days=1)
    reportDate = session.timeEvent.date() - processInterval
    iniTime = datetime.datetime.combine(reportDate, datetime.time(0)) + _localTime
    endTime = datetime.datetime.combine(session.timeEvent.date(), datetime.time(0)) + _localTime

    def checkZeroValueNConvert(dataValueObj):
        # Converte para horas
        duratinInHour = 0
        v = dataValueObj['Value'][0]
        if not np.isnan(v) and v != 0:
            duratinInHour = v / 3600000
        return duratinInHour

    try:
        queryPeriod = epm.QueryPeriod(iniTime, endTime)
        aggDurationNonZeroDetails = epm.AggregateDetails(processInterval, epm.AggregateType.DurationInStateNonZero)
        if not isOrderdDict:
            acCompDuration = tagACCompressor.historyReadAggregate(aggDurationNonZeroDetails, queryPeriod)
            vd = checkZeroValueNConvert(acCompDuration)
            v = vd * kWhFactor
        else:
            acCompDurationList = []
            for key, value in tagACCompressor.items():
                acCompDurationList.append(value.historyReadAggregate(aggDurationNonZeroDetails, queryPeriod))
            vdList = []
            for acCompDuration in acCompDurationList:
                vdList.append(checkZeroValueNConvert(acCompDuration))
            vList = np.array(vdList) * kWhFactor
    except:
        raise MyExceptionClass(u'oops! Erro na consulta agregada!')

    valSim = 0.0
    try:
        # Simula no site da concessionária
        phantomPath = Path(_PHANTOMPATH)
        if phantomPath.is_file():
            dr = webdriver.PhantomJS(executable_path=phantomPath._str)
        else:
            raise MyExceptionClass(u'oops! Não foi localizado driver PhantomJS!!!')
        dr.get('http://www.ceee.com.br/pportal/ceee/Component/ListValorConta.aspx?')
        val = dr.find_element_by_name('inpDsConsumo')
        val.send_keys(str(1).replace('.', ','))
        btt = dr.find_elements_by_tag_name('button')
        btt[0].click()
        r = dr.find_element_by_id('result')
        rVal = r.find_elements_by_tag_name('b')
        pos = rVal[0].text.find('R$ ')
        valSim = float(rVal[0].text[pos+3:].replace(',', '.'))
    except:
        raise MyExceptionClass(u'oops! Erro na simulação da concessionária!')

    try:
        if not isOrderdDict:
            if session.scopeContext == epr.ScopeContext.Test:
                print('Resultado: {valor} - {timestamp}'.format(valor=str(v * valSim),
                                                                timestamp=iniTime.isoformat()))
            else:  # Production ou Simulation
                tagACPowerCost.write(v * valSim, iniTime, 0)
        else:
            vCost = vList * valSim
            i = 0
            for key, value in tagACPowerCost.items():
                if session.scopeContext == epr.ScopeContext.Test:
                    print('Resultado: {valor} - {timestamp}'.format(valor=str(vCost[i]),
                                                                    timestamp=iniTime.isoformat()))
                else:  # Production ou Simulation
                    value.write(vCost[i], iniTime, 0)
                i += 1

        session.userCache['infos'] = json.dumps({"timeZone": timeZone, "kWhFactor":str (kWhFactor),
                                                 "iniLocalTime": iniTime.isoformat(), "unitDailyCost": str(valSim)})
    except:
        raise MyExceptionClass(u'oops! Deu algum erro na escrita do valor na Basic Variable!')
    return epr.ScopeResult(True)


@epr.applicationMethod('RobustLinearRegression')
def mspRobustLinearRegression(session, tag, predTag):
    """.. rubric:: RobustLinearRegression

        Função para validar:

            * R/W-histórico em Basic Variables - valores futuros (predição)
            * Geração de modelo em tempo de execução (Regressão Linear Robusta - scikit learn)
            * Tratamento automático de Time Zone

            Esta função estima o valor da temperatura em um sala 30 minutos à frente do evento de processamento da
             mesma. Ela utiliza uma técnica de Regressão Linear Robusta com dados de 1 hora passadas em relação
             ao evento de processamento.

                        :param session: objeto *session* do EPM Processor
                        :param tag: Basic Variable para fazer consulta histórica da última hora da temperatura
                        :param predTag: Basic Variable para escrever a predição da temperatura 30 minutos à frente
                                        (via *history update*)
                        :type session: epmprocessor.ScopeSession
                        :type tag: epmprocessor.epm.epmdataobject.EpmDataObject
                        :type predTag: epmprocessor.epm.epmdataobject.EpmDataObject
                        :returns: estado da execução (Sucesso=True | Falha=False)
                        :rtype: epmprocessor.ScopeResult
                        :raises: MyExceptionClass


                        .. rubric:: APPLICATION

                        Para testar uma *Application*, é preciso informar um *session/Time Event* qualquer (em UTC),
                        que ela irá calcular o valor estimado para a temperatura 30 minutos à frente.


                        .. rubric:: PRODUCTION

                        Esta função não utiliza os parâmetros: *Range* e *Processes Interval*. O resultado da
                        estimativa da temperatura 30 minutos à frente será escrito na variável informada no parâmetro
                        *predTag*.


                        .. epigraph:: **EPM Event**

                            Evento deve ser de 30 minutos para dar uma continuidade visual em gráficos de tendência.

                        .. epigraph:: **Production Rules**

                            Recomenda-se selecionar as opções *Enable error configuration* e *Abort retries on new event*,
                            com a opção de 3 retentativas em caso de falha, aguardando 1 minuto entre elas.

                        .. epigraph:: **Range**

                            Parâmetro ignorado pela função, pode ser informado qualquer valor que não será utilizado.

                        .. epigraph:: **Processes Interval**

                            Parâmetro ignorado pela função, pode ser informado qualquer valor que não será utilizado.


                        .. rubric:: SIMULATION
                            Idem *PRODUCTION*.



                        .. note::
                            Esta função serve apenas como validação de caso de uso do sistema, uma vez que não faz
                            sentido utilizar este tipo de modelagem para estimar temperaturas futuras em uma sala.


                        .. warning::
                            Não precisa informar SESSION!

                            Não é necessário informar **Range** e **Process Interval**.

                            Em **Productions** é preciso associar a um evento periódico de 30 minutos.

                            Não é feita distinção entre execuções de : *TEST*, *PRODUCTION* e *SIMULATION*, ou seja
                            o resultado sempre será escrita em uma Basic Variable em caso de sucesso na execução.


                        .. todo::
                            Validar outras consistências das duas entradas (=s, size=s, etc.).

                        .. Comment
                           Even more comment

                        .. Três linhas em branco!
                        |
                        |
                        |
                        """

    fitPeriod = 60
    predPeriod = 30
    processIntervalSec = 60*fitPeriod//60
    processInterval = datetime.timedelta(seconds=processIntervalSec)
    endTime = session.timeEvent
    iniTime = endTime - datetime.timedelta(seconds=60*fitPeriod)
    printOutput4Debug('INI-Time: {}, END-Time: {}, ProcessInterval: {}'.format(iniTime, endTime, processInterval))
    nSamples = 60*fitPeriod//processIntervalSec
    printOutput4Debug('# amostras: {}'.format(nSamples))
    try:
        queryPeriod = epm.QueryPeriod(iniTime, endTime)
        aggInterpDetails = epm.AggregateDetails(processInterval, epm.AggregateType.Interpolative)
        interpData = tag.historyReadAggregate(aggInterpDetails, queryPeriod)
    except:
        raise MyExceptionClass(u'oops! Erro na interpolação!')
    if len(interpData) < 2:
        session.usercache['infos'] = json.dumps({"processIntervalSeconds": processIntervalSec,
                                                 "nSamples": nSamples, "fitInfos": "NO DATA TO FIT!"})
        return scoperesult.scoperesult(True)
    timeDelta = np.linspace(0, nSamples, nSamples).reshape(nSamples, 1)
    base_estimator = linear_model.LinearRegression()
    model_ransac = linear_model.RANSACRegressor(base_estimator, min_samples=2, residual_threshold=5, random_state=0)
    try:
        fitInfos = model_ransac.fit(timeDelta, interpData['Value'])
    except:
       raise MyExceptionClass(u'oops! Erro no Fit dos dados!')
    printOutput4Debug('FIT: {}'.format(fitInfos))
    nSamplesPred = 60*predPeriod//processIntervalSec
    timeDeltaPred = np.linspace(timeDelta[-1],2*(nSamplesPred+timeDelta[-1]), nSamplesPred).reshape(nSamplesPred, 1)
    predData = model_ransac.predict(timeDeltaPred)
    desc = np.dtype([('Value', '>f8'), ('Timestamp', 'object'), ('Quality', 'i4')])
    epmPredData = np.empty(nSamplesPred, dtype=desc)
    epmPredData['Value'] = predData
    epmPredData['Quality'] = 0
    delta = datetime.timedelta(seconds=processIntervalSec)
    predTimestamp = np.arange(endTime+delta, 31*delta+endTime, delta)
    epmPredData['Timestamp'] = predTimestamp
    printOutput4Debug('Antes do W len(PredData): {}'.format(len(epmPredData['Value'])))
    try:
        if session.scopeContext == epr.ScopeContext.Test:
            print('Resultado: {valor} - {timestamp}'.format(valor=str(epmPredData['Value'][-1]),
                                                            timestamp=epmPredData['Timestamp'][-1].isoformat()))
        else:  # Production ou Simulation
            predTag.historyUpdate(epmPredData)
    except:
        raise MyExceptionClass(u'oops! Erro na escrita dos dados preditos!')
    printOutput4Debug('Escrita ok!')
    session.userCache['infos'] = json.dumps({"processInterval": processIntervalSec, "nSamples":nSamples,
                                             "fitInfos":str(fitInfos)})
    return epr.ScopeResult(True)


@epr.applicationMethod('FloorPdfReport')
def mspFloorPdfReport(session, floorObjs, floor, filesPath, fileName, timeZone):
    """.. rubric:: FloorPdfReport

        Função para validar:

            * utilização de objetos do EPM como parâmetros (navegação na estrutura hierárquica de dados)
            * geração automática de relatórios em PDF (estatísticas descritivas) a partir de um template de relatório em HTML
            * Tratamento automático de Time Zone

            Esta função gera relatórios mensais com informações sobre a temperatura e uso do ar condicionado para todas
            as salas modeladas para um dado andar com automação. O relatório está no formato PDF e é disponibilizado em
            um local da rede onde todos possam acessar (HD ou repositório do EPM Webserver). Cada relatório segue um
            padrão de nomenclatura de arquivo indicando o andar ao qual pertence, o ano e mês de referência.
            O conteúdo é uma tabela com informações estatísticas descritivas de cada uma das salas, seguido de um gráfico
            do tipo Box-Plot das temperaturas das mesmas, um gráfico de barras indicando o tempo médio diário do
            ar-condicionado ligado em cada uma das salas e, por fim, um gráfico com as temperaturas mínimas e máximas
            de cada uma das salas.

                        :param session: objeto *session* do EPM Processor
                        :param floorObjs: informar qual o tipo de *Objeto do Elipse Data Model* deve ser utilizado.
                               Este parâmetro sempre deverá ser do tipo **Floor** a não ser que a modelagem na automação
                               seja alterada.
                        :param floor: Informar um filtro para identificar o andar desejado. No caso da Elipse-RS, existem
                               apenas 3 andares: *Floor10*, *Floor11* e *Floor12*
                        :param filesPath: local para salvar o relatório gerado (disco|repositório).
                        :param fileName: nome do arquivo HTML de template utilizado para gerar o relatório em PDF.
                        :param timeZone: define o Time Zone onde se localiza o EPM Server. Por padrão: *'Brazil/East'*
                        :type session: epmprocessor.ScopeSession
                        :type floorObjs: OrderedDict com objetos Floor modelado pelo Elipse Data Model.
                        :type floor: string
                        :type filesPath: string
                        :type fileName: string
                        :type timeZone: string
                        :returns: estado da execução (Sucesso=True | Falha=False)
                        :rtype: epmprocessor.ScopeResult
                        :raises: MyExceptionClass


                        .. rubric:: APPLICATION

                        Para testar uma *Application*, é preciso informar um *session/Time Event* qualquer (em UTC),
                        que ela irá gerar um relatório para o mês anterior ao do evento.
                        Esta função não utiliza os parâmetros: *Range* e *Processes Interval*.

                        .. rubric:: PRODUCTION

                        Esta função não utiliza os parâmetros: *Range* e *Processes Interval*. O relatóri em PDF é
                        gerado para o mês anterior ao do evento.


                        .. epigraph:: **EPM Event**

                            Evento deve ser de mensal, podendo definir qualquer dia, uma vez que ele serve apenas como
                            referência para gerar o relatório do mês anterior, supostamente com todos os dados
                            necessários já disponíveis (mês completo).

                        .. epigraph:: **Production Rules**

                            Recomenda-se selecionar as opções *Enable error configuration* e *Abort retries on new event*,
                            com a opção de 3 retentativas em caso de falha, aguardando 1 minuto entre elas.

                        .. epigraph:: **Range**

                            Parâmetro ignorado pela função, pode ser informado qualquer valor que não será utilizado.

                        .. epigraph:: **Processes Interval**

                            Parâmetro ignorado pela função, pode ser informado qualquer valor que não será utilizado.


                        .. note::
                            É necessário que o arquivo de template esteja disponível e siga as regras de nomenclatura,
                            pois o nome do arquivo gerado utiliza o do template como referência.

                            Para usar este método, é necessário que os dados sigam a seguinte modelagem feita através
                            do **Elipse Data Model**, conforme exemplificado na imagem a seguir:

                        .. image:: ElipseDataModel.PNG
                           :alt: Elipse Data Model
                           :height: 300pt
                           :align: center

                        .. warning::
                            O parâmetro *filesPath* deve corresponder a um local com permissões de escrita para que o
                            relatório possa ser salvo no caso de dispoição em disco. Na utilização do repositório, basta
                            informar um local válido.

                            Não é necessário informar **Range** e **Process Interval**.


                        .. todo::
                            Validar outras consistências das entradas (=s, size=s, etc.).

                            Tratar eventuais problemas com a utilização do arquivo de template (não existir, etc.).

                            Tratar eventuais problemas com a escrita dos relatórios PDF no local informado.

                        .. Comment
                           Even more comments


                        .. Três linhas em branco!

                        |
                        |
                        |
                        """

    roomsObj = list(floorObjs.values())[0]
    tmpRE = re.search(r'\[Elipse\-\w{2}\]', roomsObj.path)
    if tmpRE:
        elipseSite = tmpRE.group()
    else:
        raise MyExceptionClass(u'oops! Erro no nome do site da Elipse!')
    roomPrettyName = {('[Elipse-RS]', 'Floor10', 'Room1'): 'ADM',
                      ('[Elipse-RS]', 'Floor10', 'Room2'): 'TI',
                      ('[Elipse-RS]', 'Floor10', 'Room3'): 'Meeting10th',
                      ('[Elipse-RS]', 'Floor10', 'Room4'): 'EPM',
                      ('[Elipse-RS]', 'Floor11', 'Room1'): 'Power',
                      ('[Elipse-RS]', 'Floor11', 'Room2'): 'Servers',
                      ('[Elipse-RS]', 'Floor11', 'Room3'): 'Meeting11th',
                      ('[Elipse-RS]', 'Floor11', 'Room4'): 'E3',
                      ('[Elipse-RS]', 'Floor12', 'Room1'): 'Auditorium',
                      ('[Elipse-RS]', 'Floor12', 'Room2'): 'Training',
                      ('[Elipse-RS]', 'Floor12', 'Room3'): 'Meeting12th',
                      ('[Elipse-RS]', 'Floor12', 'Room4'): 'Dev-12'}
    rooms = ['']*4
    mapBVList = OrderedDict({'$Temp': [0]*4, '$VentON': [0]*4, '$Compr': [0]*4})
    itTemp, itAComp, itACVent = (0, 0, 0)

    def roomPath2IdxOrder(strPath):
        return int(strPath[strPath.find('Room')+4:strPath.find('Room')+5])
    # Navegando na estrutura de dados do andar para montar o mapBVList
    for roomsList in roomsObj.enumObjects().values():
        print('*SALA: ' + roomsList.path)
        idxOrder = roomPath2IdxOrder(roomsList.path) - 1
        rooms[idxOrder] = roomPrettyName[elipseSite, floor, roomsList.name]
        for room in roomsList.enumObjects().values():
            printOutput4Debug('------>' + room.path)
            if room.type == 'Temperature':
                for itemProperty in room.enumProperties().values():
                    if exactMatch(itemProperty.name, 'Measurement'):
                        printOutput4Debug(itemProperty.name)
                        mapBVList['$Temp'][idxOrder] = itemProperty
            elif room.type == 'AirConditioner':
                for itemProperty in room.enumProperties().values():
                    if exactMatch(itemProperty.name, 'Compressor'):
                        printOutput4Debug(itemProperty.name)
                        mapBVList['$Compr'][idxOrder] = itemProperty
                    elif exactMatch(itemProperty.name, 'Ventilation'):
                        printOutput4Debug(itemProperty.name)
                        mapBVList['$VentON'][idxOrder] = itemProperty

    # Inicialização do dataMap
    dataMap = {'$s1Tmin': -1, '$s1Tmax': -1, '$s1Tavg': -1, '$s1Tstd': -1, '$s1VentON': -1, '$s1ComprON': -1,
               '$s1Tcv': -1,
               '$s2Tmin': -1, '$s2Tmax': -1, '$s2Tavg': -1, '$s2Tstd': -1, '$s2VentON': -1, '$s2ComprON': -1,
               '$s2Tcv': -1,
               '$s3Tmin': -1, '$s3Tmax': -1, '$s3Tavg': -1, '$s3Tstd': -1, '$s3VentON': -1, '$s3ComprON': -1,
               '$s3Tcv': -1,
               '$s4Tmin': -1, '$s4Tmax': -1, '$s4Tavg': -1, '$s4Tstd': -1, '$s4VentON': -1, '$s4ComprON': -1,
               '$s4Tcv': -1}
    tz = pytz.timezone(timeZone)
    timeEventUTC = session.timeEvent.replace(tzinfo=pytz.UTC)
    timeEventLoc = timeEventUTC.astimezone(tz)
    timeDifference = timeEventLoc.utcoffset().total_seconds()
    _localTime = datetime.timedelta(hours=abs(timeDifference / 3600))
    eventDate = session.timeEvent.date().replace(day=1)
    reportDate = (eventDate - datetime.timedelta(days=1)).replace(day=1)
    iniTime = datetime.datetime.combine(reportDate, datetime.time(0)) + _localTime
    endTime = datetime.datetime.combine(eventDate, datetime.time(0)) + _localTime
    processInterval = datetime.timedelta(days=1)
    try:
        queryPeriod = epm.QueryPeriod(iniTime, endTime)
        aggTimeAvgDetails = epm.AggregateDetails(processInterval, epm.AggregateType.TimeAverage)
        aggDurationNonZeroDetails = epm.AggregateDetails(processInterval, epm.AggregateType.DurationInStateNonZero)
        dataValueTemp =[]
        dataValueVent =[]
        dataValueComp =[]
        for key, tagList in mapBVList.items():
            if key == '$Temp':
                for tag in tagList:
                    if type(tag) != type(None):
                        dataValueTemp.append(tag.historyReadAggregate(aggTimeAvgDetails, queryPeriod)['Value'])
                    else:
                        dataValueTemp.append(np.array([0]))
            elif key == '$VentON':
                for tag in tagList:
                     if type(tag) != type(None):
                         dataValueVent.append(tag.historyReadAggregate(aggDurationNonZeroDetails, queryPeriod)['Value']/60000)
                     else:
                        dataValueVent.append(np.array([0]))
            else:
                for tag in tagList:
                    if type(tag) != type(None):
                        dataValueComp.append(tag.historyReadAggregate(aggDurationNonZeroDetails, queryPeriod)['Value']/60000)
                    else:
                        dataValueComp.append(np.array([0]))
    except:
        raise MyExceptionClass(u'oops! Erro nas consultas agregadas!')

    def checkArray(v, func):
        return func(v) if v.size > 0 else None

    ratio = lambda a, b: None if not b or a == None else a / b

    dataMap['$s1Tmin'] = checkArray(dataValueTemp[0], np.min)
    dataMap['$s1Tmax'] = checkArray(dataValueTemp[0], np.max)
    dataMap['$s1Tavg'] = checkArray(dataValueTemp[0], np.mean)
    dataMap['$s1Tstd'] = checkArray(dataValueTemp[0], np.std)
    dataMap['$s1VentON'] = checkArray(dataValueVent[0], np.mean)
    dataMap['$s1ComprON'] = checkArray(dataValueComp[0], np.mean)
    dataMap['$s1Tcv'] = ratio(dataMap['$s1ComprON'], dataMap['$s1VentON'])
    dataMap['$s2Tmin'] = checkArray(dataValueTemp[1], np.min)
    dataMap['$s2Tmax'] = checkArray(dataValueTemp[1], np.max)
    dataMap['$s2Tavg'] = checkArray(dataValueTemp[1], np.mean)
    dataMap['$s2Tstd'] = checkArray(dataValueTemp[1], np.std)
    dataMap['$s2VentON'] = checkArray(dataValueVent[1], np.mean)
    dataMap['$s2ComprON'] = checkArray(dataValueComp[1], np.mean)
    dataMap['$s2Tcv'] = ratio(dataMap['$s2ComprON'], dataMap['$s2VentON'])
    dataMap['$s3Tmin'] = checkArray(dataValueTemp[2], np.min)
    dataMap['$s3Tmax'] = checkArray(dataValueTemp[2], np.max)
    dataMap['$s3Tavg'] = checkArray(dataValueTemp[2], np.mean)
    dataMap['$s3Tstd'] = checkArray(dataValueTemp[2], np.std)
    dataMap['$s3VentON'] = checkArray(dataValueVent[2], np.mean)
    dataMap['$s3ComprON'] = checkArray(dataValueComp[2], np.mean)
    dataMap['$s3Tcv'] = ratio(dataMap['$s3ComprON'], dataMap['$s3VentON'])
    dataMap['$s4Tmin'] = checkArray(dataValueTemp[3], np.min)
    dataMap['$s4Tmax'] = checkArray(dataValueTemp[3], np.max)
    dataMap['$s4Tavg'] = checkArray(dataValueTemp[3], np.mean)
    dataMap['$s4Tstd'] = checkArray(dataValueTemp[3], np.std)
    dataMap['$s4VentON'] = checkArray(dataValueVent[3], np.mean)
    dataMap['$s4ComprON'] = checkArray(dataValueComp[3], np.mean)
    dataMap['$s4Tcv'] = ratio(dataMap['$s4ComprON'], dataMap['$s4VentON'])
    tmpdateStr = reportDate.isoformat()
    yymm = tmpdateStr[2:4] + tmpdateStr[5:7]

    # Definindo o gerenciador do repositório
    epmConn = getFirstFromODict(session.connections)
    epResourceManager = epmConn.getProcessorResourcesManager()
    imgTmpFolder = epResourceManager.getResource(u'mspfiles/images/temp')

    # Criando os gráficos
    #  *** Boxplot ***
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(7, 4), dpi=300)
    axes.boxplot(dataValueTemp, labels=rooms)
    if _USEREPOSITORY:
        bufBoxplot = io.BytesIO()
        fig.savefig(bufBoxplot, format='png')
        bufBoxplot.seek(0)
        resource = imgTmpFolder.upload('figBoxplot.png', bufBoxplot, 'Resource enviada pelo processor',
                                       mimetypes.types_map['.png'], overrideFile=True)
    else:
        fig.savefig(filesPath + '\\figBoxplot.png')

    # *** Barchart ***
    fig2, axes2 = plt.subplots(nrows=1, ncols=1, figsize=(7, 4), dpi=300)
    absTimeCompON = [dataValueComp[0].mean(), dataValueComp[1].mean(), dataValueComp[2].mean(),
                     dataValueComp[3].mean()]
    axes2.bar(range(len(absTimeCompON)), absTimeCompON, align='center')
    plt.ylabel('minutos')
    plt.xticks(range(len(absTimeCompON)), rooms)
    if _USEREPOSITORY:
        bufCompOnPercent = io.BytesIO()
        fig2.savefig(bufCompOnPercent, format='png')
        bufCompOnPercent.seek(0)
        resource = imgTmpFolder.upload('figCompOnPercent.png', bufCompOnPercent, 'Resource enviada pelo processor',
                                       mimetypes.types_map['.png'], overrideFile=True)
    else:
        fig2.savefig(filesPath + '\\figCompOnPercent.png')
    # *** Barchart MinMax ***
    fig3, axes3 = plt.subplots(nrows=1, ncols=1, figsize=(7, 4), dpi=300)
    tempsMin= [dataValueTemp[0].min(), dataValueTemp[1].min(), dataValueTemp[2].min(), dataValueTemp[3].min()]
    tempsMax = [dataValueTemp[0].max(), dataValueTemp[1].max(), dataValueTemp[2].max(),dataValueTemp[3].max()]
    pos = np.arange(len(tempsMin))
    barWidth = 0.35
    axes3.bar(pos - barWidth/2, tempsMin, barWidth, color='SkyBlue', label='MIN')
    axes3.bar(pos + barWidth/2, tempsMax, barWidth, color='IndianRed', label='MAX')
    plt.ylabel('Temperatura (°C)')
    plt.xticks(range(len(tempsMin)), rooms)
    if _USEREPOSITORY:
        bufMinMax= io.BytesIO()
        fig3.savefig(bufMinMax, format='png')
        bufMinMax.seek(0)
        resource = imgTmpFolder.upload('figMaxMinAC.png', bufMinMax, 'Resource enviada pelo processor',
                                       mimetypes.types_map['.png'], overrideFile=True)
        generatePdfReportRepository(session, dataMap, floor[-2:], rooms, yymm, filesPath, fileName)
    else:
        fig2.savefig(filesPath + '\\figMaxMinAC.png')
        generatePdfReport(dataMap, floor[-2:], rooms, yymm, filesPath, fileName)

    return epr.ScopeResult(True)

#### ***** </Módulos para o EPM Processor> *****

########################################################################################################################
########################################################################################################################

#### ***** <Funções/Classes utilizadas pelos módulos> *****

class MyExceptionClass(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def printOutput4Debug(msg):
    global _PRINTDEBUG
    print(msg) if _PRINTDEBUG else None

def getFirstFromODict(od):
    return next(iter(od.values())) if isinstance(od, OrderedDict) or isinstance(od, dict) else None

def getEPMConnection(connectionsMap, epmWebserver):
    for k, v in connectionsMap.items():
        if k == epmWebserver:
            return v
    else:
        return None

def getEncodedImageFromRepository(epResourceManager, fileImageName):
    #\TODO: fazer tratamento de exceções no caso de não achar as imagens!
    imageResource = epResourceManager.getResource(fileImageName)
    imageIO = imageResource.download(epm.DownloadType.Binary)
    imageIO.seek(0)
    figEncoded = base64.b64encode(imageIO.read())
    return figEncoded

def exactMatch(str1, str2):
    res = re.findall('\\b'+str2+'\\b', str1, flags=re.IGNORECASE)
    if len(res) > 0:
        return True
    else:
        return False

def generatePdfReport(dataMap, floor, rooms, yymm, filesPath, fileName):
    vars = ['$andar', '$reportDate', '$sala1', '$sala2', '$sala3', '$sala4',
            '$s1Tmin', '$s1Tmax', '$s1Tavg', '$s1Tstd', '$s1VentON', '$s1ComprON',
            '$s2Tmin', '$s2Tmax', '$s2Tavg', '$s2Tstd', '$s2VentON', '$s2ComprON',
            '$s3Tmin', '$s3Tmax', '$s3Tavg', '$s3Tstd', '$s3VentON', '$s3ComprON',
            '$s4Tmin', '$s4Tmax', '$s4Tavg', '$s4Tstd', '$s4VentON', '$s4ComprON']
    pdfFileName = fileName.replace('NN', floor)
    pdfFileName = pdfFileName.replace('YYMM', yymm)
    pdfFileName = pdfFileName.replace('_template.html', '.pdf')
    # </Preparando nome do arquivo PDF>
    path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    options = {
        'quiet': '',
        'page-size': 'A4',
        'margin-top': '1.5cm',
        'margin-right': '1.5cm',
        'margin-bottom': '1.5cm',
        'margin-left': '1.5cm',
        'encoding': "UTF-8"
        }
    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    reportPath = filesPath + '\\pdfReports'
    reportDate = yymm
    f = open(filesPath + '\\' + fileName, 'r')
    fileData = f.read()
    f.close()
    newdata = fileData.replace(vars[0], floor)
    newdata = newdata.replace(vars[1], reportDate)
    for i in range(6, len(vars)):
        newdata = newdata.replace(vars[i], str(dataMap[vars[i]]))
    for i in range(4):
        newdata = newdata.replace(vars[2:6][i], rooms[i])
    f = open(reportPath+'\\tmpRelatorioMensal.html', 'w')
    f.write(newdata)
    f.close()
    shutil.copy(filesPath +'\\bannerEPM.png', reportPath+'\\bannerEPM.png')
    shutil.copy(filesPath +'\\figBoxplot.png', reportPath+'\\figBoxplot.png')
    shutil.copy(filesPath +'\\figCompOnPercent.png', reportPath+'\\figCompOnPercent.png')
    pdfkit.from_url(reportPath+'\\tmpRelatorioMensal.html', reportPath+'\\' + pdfFileName, configuration=config)
    # Removendo arquivos temporários
    os.remove(reportPath+'\\tmpRelatorioMensal.html')
    os.remove(reportPath+'\\bannerEPM.png')
    os.remove(reportPath+'\\figBoxplot.png')
    os.remove(reportPath+'\\figCompOnPercent.png')

def generatePdfReportRepository(session, dataMap, floor, rooms, yymm, filesPath, fileName):
    epmConn = getEPMConnection(session.connections, 'dili')
    epResourceManager = epmConn.getProcessorResourcesManager()
    figBannerEncoded = getEncodedImageFromRepository(epResourceManager,
                                                     fileImageName=u'mspfiles/images/bannerEPM.png')
    figBoxPlotEncoded = getEncodedImageFromRepository(epResourceManager,
                                                      fileImageName=u'mspfiles/images/temp/figBoxplot.png')
    figCompPercentEncoded = getEncodedImageFromRepository(epResourceManager,
                                                          fileImageName=u'mspfiles/images/temp/figCompOnPercent.png')
    figMinMaxEncoded = getEncodedImageFromRepository(epResourceManager,
                                                     fileImageName=u'mspfiles/images/temp/figMaxMinAC.png')

    vars = ['$andar', '$reportDate', '$sala1', '$sala2', '$sala3', '$sala4',
            '$s1Tmin', '$s1Tmax', '$s1Tavg', '$s1Tstd', '$s1VentON', '$s1ComprON', '$s1Tcv',
            '$s2Tmin', '$s2Tmax', '$s2Tavg', '$s2Tstd', '$s2VentON', '$s2ComprON', '$s2Tcv',
            '$s3Tmin', '$s3Tmax', '$s3Tavg', '$s3Tstd', '$s3VentON', '$s3ComprON', '$s3Tcv',
            '$s4Tmin', '$s4Tmax', '$s4Tavg', '$s4Tstd', '$s4VentON', '$s4ComprON', '$s4Tcv']
    pdfFileName = fileName.replace('NN', floor)
    pdfFileName = pdfFileName.replace('YYMM', yymm)
    if _USEREPOSITORY:
        pdfFileName = pdfFileName.replace('_templateRepo.html', '.pdf')
    else:
        pdfFileName = pdfFileName.replace('_template.html', '.pdf')
    # </Preparando nome do arquivo PDF>
    path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    options = {
        'quiet': '',
        'page-size': 'A4',
        'margin-top': '1.5cm',
        'margin-right': '1.5cm',
        'margin-bottom': '1.5cm',
        'margin-left': '1.5cm',
        'encoding': "UTF-8"
        }
    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    reportPath = epResourceManager.getResource(u'mspfiles/reports')
    if session.scopeContext == epr.ScopeContext.Test:
        reportPath = epResourceManager.getResource(u'mspfiles/reports/temp')
    elif session.scopeContext == epr.ScopeContext.Simulation:
        reportPath = epResourceManager.getResource(u'mspfiles/reports/simulated')
    reportDate = yymm
    # Carrega o HTML template do repositório
    htmlTemplateResource = epResourceManager.getResource(u'mspfiles/reports/templates/NNthFloorReport_YYMM_templateRepo.html')
    fileData = htmlTemplateResource.download(epm.DownloadType.Text)
    # Substituindo as variáveis do template pelos valores
    newdata = fileData.replace(vars[0], floor)
    newdata = newdata.replace(vars[1], reportDate)
    for i in range(6, len(vars)):
        newdata = newdata.replace(vars[i], str(dataMap[vars[i]]))
    for i in range(4):
        newdata = newdata.replace(vars[2:6][i], rooms[i])
    # <Adicionando as imagens>
    newdata = newdata.replace('bannerEPM.png', figBannerEncoded.decode('utf-8'))
    newdata = newdata.replace('figBoxplot.png', figBoxPlotEncoded.decode('utf-8'))
    newdata = newdata.replace('figCompOnPercent.png', figCompPercentEncoded.decode('utf-8'))
    newdata = newdata.replace('figMaxMinAC.png', figMinMaxEncoded.decode('utf-8'))

    pdfFile = pdfkit.from_string(input=newdata, output_path=False, configuration=config, options=options)
    resource = reportPath.upload(pdfFileName, io.BytesIO(pdfFile),
                                 'Relatório PDF enviado pelo processor.',
                                 mimetypes.types_map['.pdf'], overrideFile=True)

    # Deletando as imagens temporariamente criadas
    epResourceManager.getResource(u'mspfiles/images/temp/figBoxplot.png').delete()
    epResourceManager.getResource(u'mspfiles/images/temp/figCompOnPercent.png').delete()
    epResourceManager.getResource(u'mspfiles/images/temp/figMaxMinAC.png').delete()


#### ***** </Funções/Classes utilizadas pelos módulos> *****

########################################################################################################################
########################################################################################################################

#### ***** <MAIN para testes locais> *****

def mainDailyACPowerCost(connections):
    # *** Definindo o objeto SESSION ***
    eventTime = datetime.datetime(2017, 10, 24, 12, tzinfo=pytz.UTC)
    notUsed = datetime.timedelta(minutes=60 * 24)
    parametersMap = {}
    userCache = {}
    lastExecutedInfo = None  # epr.ExecutionInfo(dt.datetime.now, ScopeResult(True))
    scopeResult = epr.ScopeContext.Test
    session = epr.ScopeSession(timeEvent=eventTime, range=notUsed, processInterval=notUsed,
                               parametersMap=parametersMap, userCache=userCache, lastExecutedInfo=lastExecutedInfo,
                               connectionsMap=connections, scopeContext=scopeResult)

    # *** Definindo demais parâmetros ***
    connection = getFirstFromODict(connections)
    tagACCompressor = getFirstFromODict(connection.getBasicVariables(['ADM_ACCompr']))
    tagACPowerCost = getFirstFromODict(connection.getBasicVariables(['ADM_ACCompDailyCost']))
    kWhFactor = 2.1
    timeZone = 'Brazil/East'

    # *** Chamando o método para testar ***
    r = mspDailyACPowerCost(session, tagACCompressor, tagACPowerCost, kWhFactor, timeZone)
    return r.succeeded

def mainmspRobustLinearRegression(connections):
    # *** Definindo o objeto SESSION ***
    eventTime = datetime.datetime(2018, 1, 2, 2, tzinfo=pytz.UTC)
    range = datetime.timedelta(minutes=30)
    processInterval = datetime.timedelta(minutes=1)
    parametersMap = {}
    userCache = {}
    lastExecutedInfo = None  # epr.ExecutionInfo(dt.datetime.now, ScopeResult(True))
    scopeResult = epr.ScopeContext.Test
    session = epr.ScopeSession(timeEvent=eventTime, range=range, processInterval=processInterval,
                               parametersMap=parametersMap, userCache=userCache, lastExecutedInfo=lastExecutedInfo,
                               connectionsMap=connections, scopeContext=scopeResult)

    # *** Definindo demais parâmetros ***
    connection = getFirstFromODict(connections)
    bv = getFirstFromODict(connection.getBasicVariables(['EPMDev_Temperature']))
    bvPred = getFirstFromODict(connection.getBasicVariables(['EPMDev_Temperature_Pred']))

    # *** Chamando o método para testar ***
    r = mspRobustLinearRegression(session, bv, bvPred)
    return r.succeeded

def mainPdfReport(connections):
    print('Iniciando o main...')
    # *** Definindo o objeto SESSION ***
    eventTime = datetime.datetime(2017, 10, 15, tzinfo=pytz.UTC)
    notUsed = datetime.timedelta(minutes=60*24)
    parametersMap = {}
    userCache = {}
    lastExecutedInfo = None
    scopeResult = epr.ScopeContext.Test
    session = epr.ScopeSession(timeEvent=eventTime, range=notUsed, processInterval=notUsed,
                               parametersMap=parametersMap, userCache=userCache, lastExecutedInfo=lastExecutedInfo,
                               connectionsMap=connections, scopeContext=scopeResult)

    # *** Definindo demais parâmetros ***
    # Mapeamento das salas dos sites da Elipse
    roomPrettyName={('[Elipse-RS]', 'Floor10', 'Room1'): 'ADM',
                    ('[Elipse-RS]', 'Floor10', 'Room2'): 'TI',
                    ('[Elipse-RS]', 'Floor10', 'Room3'): 'Meeting10th',
                    ('[Elipse-RS]', 'Floor10', 'Room4'): 'EPM',
                    ('[Elipse-RS]', 'Floor11', 'Room1'): 'Power',
                    ('[Elipse-RS]', 'Floor11', 'Room2'): 'Servers',
                    ('[Elipse-RS]', 'Floor11', 'Room3'): 'Meeting11th',
                    ('[Elipse-RS]', 'Floor11', 'Room4'): 'E3',
                    ('[Elipse-RS]', 'Floor12', 'Room1'): 'Auditorium',
                    ('[Elipse-RS]', 'Floor12', 'Room2'): 'Training',
                    ('[Elipse-RS]', 'Floor12', 'Room3'): 'Meeting12th',
                    ('[Elipse-RS]', 'Floor12', 'Room4'): 'Dev-12'}

    # Função para criar a lista com os objetos do EPM para utilização no relatório
    def makeBVList(floor='', elipseSite=None, basePath=None, connection=None, roomPrettyName=roomPrettyName):
        rooms=['']*4
        if len(floor) > 0:
            mapBVList = OrderedDict({'$Temp':[0]*4, '$VentON':[0]*4, '$Compr':[0]*4})
            itTemp, itAComp, itACVent = (0,0,0)
            floorStr = '/' + floor
            floorPath = basePath + elipseSite + floorStr
            floorObjs = connection.getObjects([floorPath])
            def roomPath2IdxOrder(strPath):
                return int(strPath[strPath.find('Room')+4:strPath.find('Room')+5])
            # Navegando na estrutura de dados do andar
            roomsObj = list(floorObjs.values())[0]
            for roomsList in roomsObj.enumObjects().values():
                print('*SALA: ' + roomsList.path)
                idxOrder = roomPath2IdxOrder(roomsList.path) - 1
                rooms[idxOrder] = roomPrettyName[elipseSite, floor, roomsList.name]
                for room in roomsList.enumObjects().values():
                    print('------>' + room.path)
                    if room.type == 'Temperature':
                        for itemProperty in room.enumProperties().values():
                            if exactMatch(itemProperty.name, 'Measurement'):
                                print(itemProperty.name)
                                mapBVList['$Temp'][idxOrder]= itemProperty
                    elif room.type == 'AirConditioner':
                        for itemProperty in room.enumProperties().values():
                            if exactMatch(itemProperty.name, 'Compressor'):
                                print(itemProperty.name)
                                mapBVList['$Compr'][idxOrder] = itemProperty
                            elif exactMatch(itemProperty.name, 'Ventilation'):
                                print(itemProperty.name)
                                mapBVList['$VentON'][idxOrder] = itemProperty
        else:
            rooms=['ADM', 'TI', 'Meeting10th', 'EPM']
            mapBVList = {'$Temp':[getFirstFromODict(connection.getBasicVariables(['ADM_Temperature'])),
                                  getFirstFromODict(connection.getBasicVariables(['TI_Temperature'])),
                                  getFirstFromODict(connection.getBasicVariables(['MeetingRoom10th_Temperature'])),
                                  getFirstFromODict(connection.getBasicVariables(['EPMDev_Temperature']))],
                         '$VentON':[getFirstFromODict(connection.getBasicVariables(['ADM_ACVent'])),
                                    None,
                                    getFirstFromODict(connection.getBasicVariables(['MeetingRoom10th_ACVent'])),
                                    getFirstFromODict(connection.getBasicVariables(['EPM_ACVent']))],
                         '$Compr':[getFirstFromODict(connection.getBasicVariables(['ADM_ACCompr'])),
                                   None,
                                   getFirstFromODict(connection.getBasicVariables(['MeetingRoom10th_ACCompr'])),
                                   getFirstFromODict(connection.getBasicVariables(['EPM_ACCompr']))]}
        return mapBVList, rooms, floorObjs
    # <Parâmetros>
    connection = getFirstFromODict(connections)
    elipseSite = '[Elipse-RS]'
    floor ='Floor10'
    basePath = '/Models/ElipseDataModel/DataModel/Elipse/'
    if _USEREPOSITORY:
        filesPath = 'mspfiles/reports'
        fileName = 'NNthFloorReport_YYMM_templateRepo.html'
    else:
        filesPath = r'F:\GDrive\Projects\EPMProcessorMinitreinamento\htmlTemplate'
        fileName = 'NNthFloorReport_YYMM_template.html'
    timeZone = 'Brazil/East'
    # </Parâmetros>
    mapBVList, rooms, floorObjs = makeBVList(floor, elipseSite, basePath, connection)

    # *** Chamando o método para testar ***
    r = mspFloorPdfReport(session, floorObjs, floor, filesPath=filesPath, fileName=fileName, timeZone=timeZone)
    return r.succeeded


if __name__ == '__main__':
    print('Iniciando os testes...')
    connection = epm.EpmConnection('http://epm_processor_machine:44333',
                                   'http://epm_processor_machine:44332',
                                   'epm_user',
                                   'epm_user_password')
    connections = {'epm_processor_machine': connection}

    # Descomentar a linha de interesse para Debug
    #sys.exit(int(not mainDailyACPowerCost(connections)) or 0)
    #sys.exit(int(not mainmspRobustLinearRegression(connections)) or 0)
    sys.exit(int(not mainPdfReport(connections)) or 0)


#### ***** </MAIN para testes locais> *****