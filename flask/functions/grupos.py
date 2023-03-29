from .db import conexao

def criar_grupo(data):
    conn = conexao()[0]
    cursor = conexao()[1]
    nome = data.get('nome')
    try:
        cursor.execute(f"insert into tunap_grupos (nome) values ('{nome}')")
        conn.commit()
        cursor.execute(f"select id, nome from tunap_grupos where nome = '{nome}'")
        grupo = {}
        grupo['id'] = cursor.fetchone()[0]
        grupo['nome'] = nome
        conn.close()
        retorno = {}
        retorno['grupo'] = grupo
        retorno['message'] = 'Grupo criado com sucesso!'
        return (retorno, 201)
    except Exception as e:
        conn.close()
        if 'Unique' in str(e):
            return ({'message': 'Já existe um grupo com esse nome!'}, 400)
        else:
            return ({'message': 'Erro ao criar grupo!'}, 500)