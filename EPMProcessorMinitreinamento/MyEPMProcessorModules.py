#-*- coding: utf-8 -*-
"""Elipse Plant Manager - EPM Processor - Basic functions
Copyright (C) 2017 Elipse Software.
Distributed under the MIT License.
(See accompanying file LICENSE.txt or copy at http://opensource.org/licenses/MIT)
"""


__author__ = u"Maurício"
__copyright__ = "Copyright 2017, Elipse Software"
__credits__ = [u"Renan", u"Lucas"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = u"Maurício"
__email__ = "mauricio@elipse.com.br"
__status__ = "Production"
__docformat__ = 'reStructuredText'


import sys
import datetime
import pytz
import json
from pathlib import Path
from collections import OrderedDict
import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt
plt.style.use('ggplot')
#plt.ioff()
from selenium import webdriver

# ****** <Import dos Módulos do EPM Processor> ******
import epmprocessor as epr
import epmprocessor.epm as epm
# ****** </Import dos Módulos do EPM Processor> ******


#### ***** <Configurações globais> *****
_SERVERMACHINE = False  # Indica se é para rodar no servidor (=True)
_PRINTDEBUG = True  # Indica se é para imprimir outputs em modo de depuração
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
    if not isOrderdDict and type(tagACCompressor) != epr.epm.epmdataobject.EpmDataObject:
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
        if not np.isnan(v) and v!= 0:
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
        if _SERVERMACHINE:
            phantomPath = Path(r'C:\temp\mspFiles\phantomjs\bin\phantomjs.exe')
        else:
            phantomPath = Path(r'C:\Programas\phantomjs\bin\phantomjs.exe')
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
        valSim =  float(rVal[0].text[pos+3:].replace(',', '.'))
    except:
        raise MyExceptionClass(u'oops! Erro na simulação da concessionária!')

    try:
        if not isOrderdDict:
            tagACPowerCost.write(v * valSim, iniTime, 0)
        else:
            vCost = vList * valSim
            i = 0
            for key, value in tagACPowerCost.items():
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
        predTag.historyUpdate(epmPredData)
    except:
        raise MyExceptionClass(u'oops! Erro na escrita dos dados preditos!')
    printOutput4Debug('Escrita ok!')
    session.userCache['infos'] = json.dumps({"processInterval": processIntervalSec, "nSamples":nSamples,
                                             "fitInfos":str(fitInfos)})
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

#### ***** </Funções/Classes utilizadas pelos módulos> *****

########################################################################################################################
########################################################################################################################

#### ***** <MAIN para testes locais> *****

def mainDailyACPowerCost():
    connection = epm.testepmconnection.TestEpmConnection('http://epm_processor_machine:44333',
                                                         'http://epm_processor_machine:44332',
                                                         'epm_user',
                                                         'epm_user_password')
    tagACCompressor = connection.getBasicVariable('1:ADM_ACCompr')
    tagACPowerCost = connection.getBasicVariable('1:ADM_ACCompDailyCost')
    eventTime = datetime.datetime(2018, 1, 3, 12, tzinfo=pytz.UTC)
    kWhFactor=2.1
    timeZone = 'Brazil/East'
    notUsed = datetime.timedelta(minutes=60*24)
    parametersMap = {}
    userCache = {}
    lastExecutedInfo = None
    session = epr.ScopeSession(eventTime, notUsed, notUsed, parametersMap, userCache, lastExecutedInfo)
    r = mspDailyACPowerCost(session, tagACCompressor, tagACPowerCost, kWhFactor, timeZone)
    print('Final da: mainDailyACPowerCost()')
    return r.succeeded


def mainmspRobustLinearRegression():
    eventTime = datetime.datetime(2018, 1, 2, 2, tzinfo=pytz.UTC)
    connection = epm.testepmconnection.TestEpmConnection('http://epm_processor_machine:44333',
                                                         'http://epm_processor_machine:44332',
                                                         'epm_user',
                                                         'epm_user_password')
    bv = connection.getBasicVariable('1:EPMDev_Temperature')
    bvPred = connection.getBasicVariable('1:EPMDev_Temperature_Pred')
    parametersMap = {}
    userCache = {}
    lastExecutedInfo = None
    session = epr.ScopeSession(eventTime, datetime.timedelta(minutes=30), datetime.timedelta(minutes=1), parametersMap,
                               userCache, lastExecutedInfo)
    r = mspRobustLinearRegression(session, bv, bvPred)


if __name__ == '__main__':
    print('Iniciando a depuração...')
    sys.exit(int(mainDailyACPowerCost() or 0))
    #sys.exit(int(mainmspRobustLinearRegression() or 0))


#### ***** </MAIN para testes locais> *****