import pandas as pd
import ConexaoPostgreMPL

def DetalhaPedido(codPedido):
    # 1- Filtrando o Pedido na tabela de pedidosSku
    conn = ConexaoPostgreMPL.conexao()

    skus1 = pd.read_sql('select codigopedido, desc_tiponota  , codcliente ||' + "'-'" + '|| desc_cliente as cliente  '
                        ',codrepresentante  ||' + "'-'" + '|| desc_representante  as repres, agrupamentopedido '
                    'from "Reposicao".filaseparacaopedidos f  where codigopedido= ' + "'" + codPedido + "'"
                       , conn)

    if skus1.empty:
        # Olha Para os Pedidos de Transferencia
            skus = pd.read_sql("select descricaopedido as codigopedido, 'transferencia' as desc_tiponota,"
                               " 'transferencia de Naturezas' as cliente  "
                                ",'transferencia de Naturezas' as repres, "
                                'codigopedido as agrupamentopedido '
                                'from "Reposicao"."pedidosTransferecia" f  '
                                "where situacao = 'aberto'" 
                                ' and descricaopedido= ' + "'" + codPedido + "'"
                       , conn)
    else:

            skus = skus1

    grupo = pd.read_sql('select agrupamentopedido '
                        'from "Reposicao".filaseparacaopedidos f  where codigopedido= ' + "'" + codPedido + "'"
                        , conn)
    DetalhaSku = pd.read_sql(
        "select  produto as reduzido, sum(qtdesugerida) , (sum(qtdesugerida) - sum(necessidade))||'/'||sum(qtdesugerida) as concluido_X_total, endereco as endereco, sum(necessidade) as a_concluir , "
        'sum(qtdesugerida) as total, (sum(qtdesugerida) - sum(necessidade)) as qtdrealizado'
        ' from "Reposicao".pedidossku p  where codpedido= ' + "'" + codPedido + "'"
                                                                                " group by produto, endereco "
                                                                                "order by endereco asc", conn)

    # Validando as descricoes + cor + tamanho dos produtos para nao ser null

    descricaoSku = pd.read_sql(
                    'select engenharia as referencia, codreduzido as reduzido, descricao, cor ,tamanho from "Reposicao"."Tabela_Sku" '
                    ' where codreduzido in '
                    '(select  produto as reduzido '
                    'from "Reposicao".pedidossku p  where codpedido = ' + "'" + codPedido + "') ", conn)


    DetalhaSku = pd.merge(DetalhaSku, descricaoSku, on='reduzido', how='left')

    # Agrupar os valores da col2 por col1 e concatenar em uma nova coluna
    DetalhaSku['endereco'] = DetalhaSku.groupby(['reduzido'])['endereco'].transform(lambda x: ', '.join(x))
    # Remover as linhas duplicadas
    DetalhaSku = DetalhaSku.drop_duplicates()
    data = {
        '1 - codpedido': f'{skus["codigopedido"][0]} ',
        '2 - Tiponota': f'{skus["desc_tiponota"][0]} ',
        '3 - Cliente': f'{skus["cliente"][0]} ',
        '4- Repres.': f'{skus["repres"][0]} ',
        # '4.1- Grupo.': f'{skus["grupo"][0]} ',
        '5- Detalhamento dos Sku:': DetalhaSku.to_dict(orient='records')
    }

    return [data]

def AtualizadoEnderecoPedido(codpedido):
    conn = ConexaoPostgreMPL.conexao()
    Pedido = pd.read_sql('Select * From "Reposicao".pedidossku p '
                         'where p.codpedido = '+"'"+codpedido+"'"+" and p.necessidade > 0",conn)
    testeAtualizacao(Pedido)
    return print(f'pedido {codpedido} atualizado')


def testeAtualizacao(dataframe):
    dataframe = dataframe
    tamanho = dataframe['codpedido'].size
    conn = ConexaoPostgreMPL.conexao()
    if dataframe.empty:
        print('sem incrmento' )
        return pd.DataFrame(
                {'Mensagem': [f'{tamanho} atualizacoes para realizar! ']})
    else:
        for i in range(tamanho):

            query = '''
                UPDATE "Reposicao".pedidossku p 
                SET "endereco" = %s
                WHERE p.codpedido = %s AND p.produto = %s
            '''

            # Execute a consulta usando a conexão e o cursor apropriados
            cursor = conn.cursor()
            cursor.execute(query, (dataframe['endereco'][i], dataframe['codpedido'][i], dataframe['produto'][i]))
            conn.commit()