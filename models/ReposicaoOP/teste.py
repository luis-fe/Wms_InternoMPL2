import ConexaoPostgreMPL
import pandas as pd
import numpy

def FilaPorOP(natureza, codempresa):
    conn = ConexaoPostgreMPL.conexao()

    df_OP1 = pd.read_sql \
        (' select "numeroop", "totalop" as qtdpeÃ§s_total, "usuario" as codusuario_atribuido, count("numeroop") as qtdpeÃ§s_arepor  from "Reposicao"."filareposicaoportag" frt '
                         ' where "codnaturezaatual" = %s  '
                         ' group by "numeroop", "usuario", "totalop"  ' ,conn ,params=(natureza,))

    df_OP_Iniciada =pd.read_sql(
        ' select "numeroop", count("numeroop") as qtdpeÃ§s_reposto  from "Reposicao"."tagsreposicao" frt '
        ' where "numeroop" is not null '
        ' group by "numeroop" ', conn)
    df_OP1 = pd.merge(df_OP1, df_OP_Iniciada, on='numeroop', how='left')



    usuarios = pd.read_sql(
        'select codigo as codusuario_atribuido , nome as nomeusuario_atribuido  from "Reposicao".cadusuarios c ', conn)
    usuarios['codusuario_atribuido'] = usuarios['codusuario_atribuido'].astype(str)
    df_OP1 = pd.merge(df_OP1, usuarios, on='codusuario_atribuido', how='left')
    df_OP1['qtdpeÃ§s_reposto'] = df_OP1['qtdpeÃ§s_reposto'].replace('', numpy.nan).fillna('0')
    df_OP1['qtdpeÃ§s_total'] = df_OP1['qtdpeÃ§s_total'].replace('', numpy.nan).fillna('0')
    df_OP1['qtdpeÃ§s_arepor'] = df_OP1['qtdpeÃ§s_arepor'].replace('', numpy.nan).fillna('0')
    df_OP1['qtdpeÃ§s_total'] = df_OP1['qtdpeÃ§s_total'].astype(int)
    df_OP1 = df_OP1[df_OP1['qtdpeÃ§s_total'] > 0]
    df_OP1['qtdpeÃ§s_reposto'] = df_OP1['qtdpeÃ§s_reposto'].astype(int)
    df_OP1['% Reposto'] = 1 - numpy.divide(df_OP1['qtdpeÃ§s_arepor'], df_OP1['qtdpeÃ§s_total'])
    df_OP1['% Reposto'] = df_OP1['% Reposto'] * 100
    df_OP1['% Reposto'] = df_OP1['% Reposto'].round(2)

    # Clasificando o Dataframe para analise
    df_OP1 = df_OP1.sort_values(by='qtdpeÃ§s_total', ascending=False,
                                ignore_index=True)  # escolher como deseja classificar
    df_OP1["Situacao"] = df_OP1.apply(lambda row: 'Iniciada' if row['qtdpeÃ§s_reposto'] > 0 else 'Nao Iniciada', axis=1)
    df_OP1['codusuario_atribuido'] = df_OP1['codusuario_atribuido'].replace('', numpy.nan).fillna('-')
    df_OP1['nomeusuario_atribuido'] = df_OP1['nomeusuario_atribuido'].replace('', numpy.nan).fillna('-')
    conn.close()
    # Limitar o nÃºmero de linhas usando head()
    df_OP1 = df_OP1.head(50)  # Retorna as 3 primeiras linhas
    return df_OP1

def ConsultaSeExisteAtribuicao(numeroop):
    conn = ConexaoPostgreMPL.conexao()
    cursor = conn.cursor()
    cursor.execute('select "numeroop", "usuario"  from "Reposicao"."filareposicaoportag" frt  '
                   'WHERE "numeroop" = %s AND "usuario" IS NULL', (numeroop,))
    # Obter o nÃºmero de linhas afetadas
    NumeroLInhas = cursor.rowcount

    cursor.close()
    conn.close()
    return NumeroLInhas

def AtribuiRepositorOP(codigo, numeroop):
    conn = ConexaoPostgreMPL.conexao()
    cursor = conn.cursor()
    cursor.execute('update "Reposicao"."filareposicaoportag" '
                   'set "usuario"  = %s where "numeroop" = %s'
                   , (codigo, numeroop))
    # Obter o nÃºmero de linhas afetadas
    numero_linhas_afetadas = cursor.rowcount
    conn.commit()
    cursor.close()


def detalhaOP(numeroop, empresa, natureza):
    conn = ConexaoPostgreMPL.conexao()
    df_op = pd.read_sql(
        'select "numeroop" , "codbarrastag", "epc", "usuario" as codusuario_atribuido, "Situacao", "codreduzido", codnaturezaatual as natureza '
        'from "Reposicao"."filareposicaoportag" frt where "numeroop" = ' + "'" + numeroop + "' and "
                                                                                            " codnaturezaatual = '" + natureza + "' ",
        conn)

    df_op['codusuario_atribuido'] = df_op['codusuario_atribuido'].replace('', numpy.nan).fillna('-')
    df_op2 = pd.read_sql(
        'select "numeroop" , "codbarrastag" AS codbarrastag, "epc" as epc, "usuario" as codusuario_atribuido,' + "'reposto'" + 'as situacao, "codreduzido", natureza '
                                                                                                                               'from "Reposicao"."tagsreposicao" frt where "numeroop" = ' + "'" + numeroop + "' and natureza = '" + natureza + "'",
        conn)
    df_op2.rename(columns={'codreduzido': 'codreduzido', "situacao": 'Situacao'}, inplace=True)

    df_op = pd.concat([df_op, df_op2])
    usuarios = pd.read_sql(
        'select codigo as codusuario_atribuido , nome as nomeusuario_atribuido  from "Reposicao".cadusuarios c ', conn)
    usuarios['codusuario_atribuido'] = usuarios['codusuario_atribuido'].astype(str)
    df_op = pd.merge(df_op, usuarios, on='codusuario_atribuido', how='left')
    df_op['codusuario_atribuido'] = df_op['codusuario_atribuido'].replace('', numpy.nan).fillna('-')
    df_op['nomeusuario_atribuido'] = df_op['nomeusuario_atribuido'].replace('', numpy.nan).fillna('-')
    conn.close()

    if df_op.empty:
        return pd.DataFrame({'Status': [False], 'Mensagem': ['OP nao Encontrada']})
    else:
        return df_op

def detalhaOPxSKU(numeroop, empresa, natureza):
    conn = ConexaoPostgreMPL.conexao()
    df_op = pd.read_sql('select "numeroop", "codreduzido", "engenharia", "cor", "tamanho", "descricao", "codnaturezaatual" as natureza '
                   'from "Reposicao"."filareposicaoportag" frt where "numeroop" = ' +"'"+  numeroop +"' and codnaturezaatual = '"+natureza+"' "
                   'group by "numeroop", "codreduzido","descricao" , "cor","tamanho","engenharia", codnaturezaatual', conn)
    df_op2 = pd.read_sql('select "numeroop", "codreduzido", "engenharia", "cor", "tamanho", "descricao", natureza '
                   'from "Reposicao"."tagsreposicao" frt where "numeroop" = ' +"'"+  numeroop +"' and natureza = '"+natureza+"' "
                   ' group by "numeroop", "codreduzido","descricao" , "cor","tamanho","engenharia" , natureza', conn)
    df_op2.rename(columns={'codreduzido': 'codreduzido', "engenharia": 'engenharia', "cor": "cor", "descricao": "descricao"}, inplace=True)

    df_op = pd.concat([df_op, df_op2])
    df_op.drop_duplicates(subset={'numeroop', 'codreduzido'}, inplace=True)


    conn.close()
    if df_op.empty:
        return pd.DataFrame({'Status': [False],'Mensagem':['OP nao Encontrada']})
    else:
        return  df_op

