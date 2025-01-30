# Pacotes e funções utilizadas no programa principal

# Pacotes

import os
import gdown
import pandas as pd
import time

# Funções

def baixar_diretorio() -> None:
  """
  Baixa do GitHub o diretório contendo os arquivos necessários ao funcionamento do programa
  """
  dir_path = '/content/gerar_xml_pdg'

  if not os.path.exists(dir_path):
    repo_url = 'https://github.com/paulobistenealexandrino/gerar_xml_pdg'
    os.system(f'git clone {repo_url}')

def baixar_xlsx(cod_processo: int) -> None:
  """
  Baixa o arquivo .xlsx de acordo com o processo do PDG

  Key arguments:
  cod_processo -- código do processo do PDG
  """
  if cod_processo in [1, 3, 5]:
    file_url = 'https://drive.google.com/uc?id=1uPXhKSj88wHG4H1hT7GgDPlIvb9PubX4'
    output_path = '/content/gerar_xml_pdg/temp/input-PDG-anual.xlsx'
  else:
    file_url = 'https://drive.google.com/uc?id=19_HBs_I6V2nDr3iMep09WrJ_XrEYOxGv'
    output_path = '/content/gerar_xml_pdg/temp/input-PDG-mensal.xlsx'

  gdown.download(file_url, output_path, quiet=True)

def preencher_rubricas(dados) -> str:
  """
  Gera as rubricas no formato XML

  Key arguments:
  dados -- dataframe contendo as informações do PDG
  """
  rubricas_preenchidas = ''

  for i in range(len(dados)):
    codigo = dados.iloc[i, 0]
    nome = dados.iloc[i, 1]
    valor = dados.iloc[i, 2]

    rubrica = f'''
      <ns1:rubrica codigo="{codigo}" nome="{nome}">
        <ns1:valor>{valor}</ns1:valor>
        <ns1:justificativa></ns1:justificativa>
      </ns1:rubrica>
      '''
    rubricas_preenchidas = rubricas_preenchidas + rubrica

  return rubricas_preenchidas

def preencher_meses(dados, cod_mes: int, acumulado: bool) -> str:
  """Organiza as rubricas por meses

  Key arguments:
  dados -- dataframe contendo as informações do PDG
  cod_mes -- número correspondente ao mês de referência do PDG
  acumulado -- define se os valores devem ser apresentados acumulados mês a mês
  """
  bloco_meses_preenchido = ''

  if acumulado == True:
    for i in range(0, cod_mes):
      mes = i + 1
      rubricas = preencher_rubricas(dados.iloc[:, [0, 1, mes + 1]])
      mes_preenchido = f'''
      <ns1:mes mes="{mes}">
        {rubricas}
      </ns1:mes>'''
      bloco_meses_preenchido = bloco_meses_preenchido + mes_preenchido

  else:
    mes = cod_mes
    rubricas = preencher_rubricas(dados.iloc[:, [0, 1, mes + 1]])
    bloco_meses_preenchido = f'''
      <ns1:mes mes="{mes}">
        {rubricas}
      </ns1:mes>'''

  return bloco_meses_preenchido

def descrever_processo(cod_processo: int) -> str:
  """
  Descreve cada processo do PDG ao informar seu código

  Key arguments:
  cod_processo -- código do processo do PDG
  """
  dict_processos = {1: 'programacao', 2: 'distribuicaoProgramacao', 3: 'reprogramacao',
                    4: 'distribuicaoReprogramacao', 5: 'remanejamento', 6: 'acompanhamento'}

  return dict_processos[cod_processo]

def gerar_xml_pdg_anual(ano: int, cod_processo: int) -> str:
  """
  Gera o arquivo XML para os processos anuais do PDG

  Key arguments:
  ano -- ano de referência do PDG
  cod_processo -- código do processo do PDG
  """
  baixar_xlsx(cod_processo)
  while True:
    try:
      input_pdg = pd.read_excel('/content/gerar_xml_pdg/temp/input-PDG-anual.xlsx')
      break
    except:
      time.sleep(2)

  processo = descrever_processo(cod_processo)
  rubricas = preencher_rubricas(input_pdg)

  xml_pdg_anual_preenchido = f'''
  <?xml version="1.0" encoding="UTF-8"?>
  <ns1:manterPDG
    xmlns:ns1="http://siest.planejamento.gov.br/xsd/pdg/2013/1/31">
    <ns1:paramPDG>
      <ns1:exercicio>{ano}</ns1:exercicio>
      <ns1:{processo}>
        <ns1:empresa codigo="7609" nome="7609 - ELETRONUCLEAR">
          <ns1:blocoOrcamentario>
            {rubricas}
          </ns1:blocoOrcamentario>
        </ns1:empresa>
      </ns1:{processo}>
    </ns1:paramPDG>
  </ns1:manterPDG>'''

  return xml_pdg_anual_preenchido

def gerar_xml_pdg_mensal(ano: int, cod_processo: int, cod_mes: int, acumulado: bool) -> str:
  """
  Gera o arquivo XML para os processos mensais do PDG

  Key arguments:
  ano -- ano de referência do PDG
  cod_processo -- código do processo do PDG
  cod_mes -- número correspondente ao mês de referência do PDG
  acumulado -- define se os valores devem ser apresentados acumulados mês a mês
  """
  baixar_xlsx(cod_processo)
  while True:
    try:
      input_pdg = pd.read_excel('/content/gerar_xml_pdg/temp/input-PDG-mensal.xlsx')
      break
    except:
      time.sleep(2)

  processo = descrever_processo(cod_processo)
  bloco_meses = preencher_meses(input_pdg, cod_mes, acumulado)

  xml_pdg_mensal_preenchido = f'''
  <?xml version="1.0" encoding="UTF-8"?>
  <ns1:manterPDG
    xmlns:ns1="http://siest.planejamento.gov.br/xsd/pdg/2013/1/31">
    <ns1:paramPDG>
      <ns1:exercicio>{ano}</ns1:exercicio>
      <ns1:{processo}>
        <ns1:empresa codigo="7609" nome="7609 - ELETRONUCLEAR">
          <ns1:blocoOrcamentario>
            <ns1:meses>
              {bloco_meses}
            </ns1:meses>
          </ns1:blocoOrcamentario>
        </ns1:empresa>
      </ns1:{processo}>
    </ns1:paramPDG>
  </ns1:manterPDG>
  '''

  return xml_pdg_mensal_preenchido

def gerar_xml_pdg(ano: int, cod_processo: int, cod_mes: int, acumulado: bool):
  """
  Gera o arquivo XML adequado para os diferentes processos do PDG

  Key arguments:
  ano -- ano de referência do PDG
  cod_processo -- código do processo do PDG
  cod_mes -- número correspondente ao mês de referência do PDG
  acumulado -- define se os valores devem ser apresentados acumulados mês a mês
  """
  if cod_processo in [1, 3, 5]:
    return gerar_xml_pdg_anual(ano, cod_processo)
  else:
    return gerar_xml_pdg_mensal(ano, cod_processo, cod_mes, acumulado)

def main():
  '''
  Função principal do programa
  '''
  # Ajusta os parâmetros
  ano = input('Insira o ano: ')
  cod_processo = int(input('Insira o código do processo: '))
  cod_mes = None
  acumulado = True
  
  if cod_processo in [2, 4, 6]:
    cod_mes = int(input('Insira o mês de referência: '))
  if cod_processo == 6:
    acumulado = bool(int(input('Os valores devem ser apresentados acumulados mês a mês? (Sim: 1/Não: 0): ')))
  else:
    acumulado = True

  # Gera o arquivo XML
  return gerar_xml_pdg(ano, cod_processo, cod_mes, acumulado)
