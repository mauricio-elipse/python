GLOSSÁRIO
===================================================================================

.. glossary::
   :sorted:

   Session
       Este é um objeto do EPM Processor utilizado por todos os métodos.
   Method
       O termo método, no contexto do EPM Processor, pode ser entendido como uma função python que foi declarada com o
       *decorator* de método do EPM Processor .
   Process Interval
       Este é o intervalo de processamento utilizado nas consultas históricas com agregação a um EPM Server. Este termo
       é oriundo do padrão OPC UA (`OPC Foundation <https://opcfoundation.org/>`_).
       Este parâmetro está disponível para *Productions* e *Simulatins*.
   Range
       Este parâmetro corresponde ao período que se deseja aplicar em uma consulta histórica de uma *Production*. Em
       geral ele corresponde a difernça entre a data inicial da consulta (calculada a partir dele) e a data final da
       consulta (definida a partir de um evento do EPM).
