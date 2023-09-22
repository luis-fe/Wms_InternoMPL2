import pandas as pd
from src.WMS_Producao import ConexaoPostgreMPL
import datetime
import pytz


def obterHoraAtual():
    fuso_horario = pytz.timezone('America/Sao_Paulo')
    agora = datetime.datetime.now(fuso_horario)
    hora_str = agora.strftime('%Y-%m-%d %H:%M:%S')
    return hora_str


def VerificarExisteApontamento(codpedido, usuario):
    conn = ConexaoPostgreMPL.conexao()
    codpedido = str(codpedido)
    query = pd.read_sql('select codpedido from "Reposicao".tags_separacao '
                        ' where codpedido = %s '
                        , conn, params=(codpedido,))
    conn.close()

    if query.empty:
        conn = ConexaoPostgreMPL.conexao()
        select = pd.read_sql('select * from "Reposicao".finalizacao_pedido fp'
                             ' where codpedido = %s ', conn, params=(codpedido,))
        if select.empty:
            print('teste')
            insert = 'insert into "Reposicao".finalizacao_pedido (codpedido, usuario, "dataInicio") values (%s , %s , %s)'
            datahora = obterHoraAtual()
            cursor = conn.cursor()
            cursor.execute(insert, (codpedido, usuario, datahora))
            conn.commit()
            conn.close()

        else:
            update = 'update "Reposicao".finalizacao_pedido' \
                     ' set usuario = %s , "dataInicio" = %s ' \
                     ' where codpedido = %s'
            datahora = obterHoraAtual()
            cursor = conn.cursor()
            cursor.execute(update, (usuario, datahora, codpedido))
            conn.commit()
            conn.close()

    else:
        print('ok')
def Buscar_Caixas():
    conn = ConexaoPostgreMPL.conexao()
    query = pd.read_sql('select tamanhocaixa as TamCaixa from "Reposicao".caixas',conn)
    conn.close()

    # Selecione a coluna 'coluna b' e converta em uma lista
    query = query['tamcaixa'].tolist()

    return query
def finalizarPedido(pedido, TamCaixa, quantidade ):
    conn = ConexaoPostgreMPL.conexao()
    datafinalizacao = obterHoraAtual()
    TamCaixa1 = TamCaixa[0]
    quantidade1 = quantidade[0]
    tamanhoVetor = len(TamCaixa)

    if tamanhoVetor == 1:
        TamCaixa2 = '0'
        quantidade2 = 0
    else:
        TamCaixa2 = TamCaixa[1]
        quantidade2 = quantidade[1]

    query = 'update  "Reposicao".finalizacao_pedido '\
                        'set "tamCaixa" = %s, qtdcaixa= %s, datafinalizacao= %s,'\
                        ' "tamcaixa2" = %s, qtdcaixa2= %s '\
                        'where codpedido = %s'

    cursor = conn.cursor()
    cursor.execute(query, (TamCaixa1,quantidade1,datafinalizacao,TamCaixa2,quantidade2,pedido,))
    conn.commit()
    conn.close()

    data = {
        'Status':
            True,
        'Mensagem': f'Pedido {pedido} finalizado com sucesso!',

    }

    return [data]


