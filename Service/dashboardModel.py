import ConexaoPostgreMPL
import pandas as pd
def relatorioTotalFila(empresa, natureza):
    conn = ConexaoPostgreMPL.conexao()
    query = pd.read_sql('SELECT numeroop, COUNT(codbarrastag) AS Saldo '
        'FROM "Reposicao".filareposicaoportag t where codnaturezaatual = %s ' 
        ' GROUP BY "numeroop" ',conn,params=(natureza,))

    query2 = pd.read_sql('select *, 1 as contagem from "Reposicao".pedidossku p'
                        " where endereco = 'Não Reposto' and necessidade > 0 and qtdepecasconf = 0",conn)

    query3 = pd.read_sql('select *, 1 as contagem from "Reposicao".pedidossku p'
                        " where endereco <> 'Não Reposto' and necessidade > 0 and qtdepecasconf = 0",conn)

    Inventario = pd.read_sql('select codreduzido  from "Reposicao".tagsreposicao_inventario ti' ,conn)
    Reposto = pd.read_sql('select codreduzido  from "Reposicao".tagsreposicao ti where natureza = %s ' ,conn, params=(natureza,))

    query['saldo'] = query['saldo'].sum()
    query2['contagem'] = query2['contagem'].sum()
    query3['contagem'] = query3['contagem'].sum()
    Inventario['codreduzido'] = Inventario['codreduzido'].count()
    Reposto['codreduzido'] = Reposto['codreduzido'].count()
    total =  query3['contagem'][0] +  query2['contagem'][0]

    Percentual = query3['contagem'][0] / total
    Percentual = round(Percentual, 2) * 100
    totalPecas = query["saldo"][0] + Reposto["codreduzido"][0]+Inventario["codreduzido"][0]
    # Aplicando a formatação para exibir como "100.000"
    query['saldo'] = query['saldo'].apply(lambda x: "{:,.0f}".format(x))
    saldo_str= str(query["saldo"][0])
    saldo_str = saldo_str.replace(',', '.')
    totalPecas = "{:,.0f}".format(totalPecas)
    totalPecas = str(totalPecas)
    totalPecas = totalPecas.replace(',', '.')
    total = "{:,.0f}".format(total)
    total = str(total)
    total2 = total.replace(',', '.')


    conn.close()
    data = {
        '1.0':f' Informacoes Gerais do Estoque natureza: {natureza}',
        '1.1-Total de Peças Nat. 5':   f'{totalPecas} pçs',
        '1.2-Saldo na Fila':   f'{saldo_str} pçs',
        '1.3-Peçs Repostas':   f'{Reposto["codreduzido"][0]} pçs',
        '1.4-Peçs em Inventario':   f'{Inventario["codreduzido"][0]} pçs',
        '2.0':' Informacoes dos pedidos',
        '2.1- Total de Skus nos Pedidos em aberto ': f'{total2} pçs',
        '2.2-Qtd de Enderecos Nao Reposto em Pedido': f'{query2["contagem"][0]}',
        '2.3-Qtd de Enderecos OK Reposto nos Pedido': f'{query3["contagem"][0]}',
        '2.4- Percentual Reposto':f'{Percentual}%'
    }
    return [data]