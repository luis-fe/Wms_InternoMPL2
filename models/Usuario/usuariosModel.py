import datetime

import pandas as pd

import ConexaoPostgreMPL


def obterHoraAtual():
    agora = datetime.datetime.now()
    hora_str = agora.strftime('%d/%m/%Y %H:%M')
    return hora_str

def PesquisarUsuarios():
    conn = ConexaoPostgreMPL.conexao()
    cursor = conn.cursor()
    cursor.execute('select codigo, nome, funcao, situacao, login, "AcessaWMS", "AcessaGarantia", "AcessaPCP" from "Reposicao"."cadusuarios" c order by nome asc')
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    colunas = [desc[0] for desc in cursor.description]
    dataframe = pd.DataFrame(usuarios, columns=colunas)
    dataframe.fillna('NAO',inplace=True)


    return dataframe

def PesquisarSenha():
    conn = ConexaoPostgreMPL.conexao()
    cursor = conn.cursor()
    cursor.execute('select codigo, nome, senha from "Reposicao"."cadusuarios" c')
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return usuarios

def PesquisarUsuariosCodigo(codigo):
    conn = ConexaoPostgreMPL.conexao()
    cursor = conn.cursor()
    codigo = int(codigo)
    cursor.execute('select codigo, nome, funcao, situacao, empresa from "Reposicao"."cadusuarios" c'
                   ' where codigo = %s',(codigo,))
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    if not usuarios:
        return 0, 0, 0,0
    else:
        return usuarios[0][1],usuarios[0][2],usuarios[0][3],usuarios[0][4]

def AtualizarInformacoes(novo_nome, nova_funcao, nova_situacao,  codigo):
    conn = ConexaoPostgreMPL.conexao()
    cursor = conn.cursor()
    cursor.execute('UPDATE "Reposicao"."cadusuarios" SET nome=%s, funcao=%s, situacao= %s WHERE codigo=%s',(novo_nome,nova_funcao,nova_situacao, codigo))
    conn.commit()
    cursor.close()
    conn.close()
    return novo_nome

def InserirUsuario(codigo, funcao, nome, senha, situacao, empresa):
    conn = ConexaoPostgreMPL.conexao()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO "Reposicao"."cadusuarios" (codigo, funcao, nome, senha, situacao, empresa) '
                   'VALUES (%s, %s, %s, %s, %s, %s)',(codigo, funcao, nome, senha, situacao, empresa))

    conn.commit()
    cursor.close()
    conn.close()
    return True

def ConsultaUsuarioSenha(codigo, senha):
    conn = ConexaoPostgreMPL.conexao()
    cursor = conn.cursor()
    # Consulta no banco de dados para verificar se o usuário e senha correspondem
    query = 'SELECT COUNT(*) FROM "Reposicao"."cadusuarios" WHERE codigo = %s AND senha = %s '

    cursor.execute(query, (codigo, senha))
    result = cursor.fetchone()[0]
    cursor.close()


    return result

def RegistroLog(codigo):
    conn = ConexaoPostgreMPL.conexao()
    # registrando data e hora do log
    hora = obterHoraAtual()
    cursor = conn.cursor()
    log = 'insert into "Reposicao"."horariodolog" ( "codigo", "datalog" ) ' \
          'values(%s, %s)'

    cursor.execute(log, (codigo, hora))
    conn.commit()
    cursor.close()
    conn.close()
    return True