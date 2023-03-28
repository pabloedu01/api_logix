from .db import conexao
from functions.valida_cpf import ValidaCpfCnpj
from flask import request

def listar_beneficiarios (id_owner, nome, limit, page, owner, cpf_cnpj, email):
    conn = conexao()[0]
    cursor = conexao()[1]
    cursor.execute('SELECT count(*) FROM tunap_beneficiarios')
    if nome != None:
        nome = str.upper(nome)
        consulta_nome = f" AND upper(nome) LIKE '%{nome}%'"
    else:
        consulta_nome = ''
    if id_owner != None:
        if str(id_owner).isnumeric():
            id_owner = int(id_owner)
            consulta_owner = f" AND owner = {id_owner}"
        else:
            return ({'message':'o id_owner deve ser um número inteiro'},400)
    else:
        consulta_owner = ''
    if cpf_cnpj != None:
        cpf_cnpj = str.upper(cpf_cnpj)
        consulta_cpf_cnpj = f" AND upper(cpf_cnpj) LIKE '%{cpf_cnpj}%'"
    else:
        consulta_cpf_cnpj = ''

    if email != None:
        email = str.upper(email)
        consulta_email = f" AND upper(email) LIKE '%{email}%'"
    else:
        consulta_email = ''

    total = cursor.fetchone()[0]

    try:
        limit = int(limit)
    except:
        return (({'message': 'O parâmetro limit deve ser um número inteiro!'}), 400)
    try:
        page = int(page)
    except:
        return ({'message': 'O parâmetro page deve ser um número inteiro!'}, 400)
    total_page = (total / limit)
    if total_page == 0:
        total_page = 1
    
    skip_page = (page - 1) * limit
    consulta = (f'SELECT SKIP {skip_page} first {limit} tb.id, trim(tb.nome), trim(tb.cpf_cnpj), trim(tb.email), trim(tb.telefone), tb.owner, trim(wa.usuario) \
                FROM tunap_beneficiarios tb \
                left join wb_acesso_internet wa on tb.owner = wa.codigo \
                where 1=1 {consulta_nome} {consulta_cpf_cnpj}{consulta_email}{consulta_owner} ORDER BY id')
    cursor.execute(consulta)
    rows = cursor.fetchall()
    lista_beneficiarios = []
    beneficiarios = {}
    for row in rows:
        beneficiario = {
            'id': row[0],
            'nome': row[1],
            'cpf_cnpj': row[2],
            'email': row[3],
            'telefone': row[4],
            'id_owner': row[5],
            'owner': row[6]
        }
        lista_beneficiarios.append(beneficiario)
    cursor.close()
    conn.close()
    beneficiarios['Beneficiarios'] = lista_beneficiarios
    beneficiarios['qtd_resultados'] = int(total)
    beneficiarios['pagina_atual'] = int(page)
    return (beneficiarios, 200)


def inserir_beneficiario (data):
    
    nome = data.get('nome')
    cpf_cnpj = data.get('cpf_cnpj', None)
    email = data.get('email')
    telefone = data.get('telefone')
    owner = data.get('id_owner', 'null')
    if cpf_cnpj != None:
        valida_cpf = ValidaCpfCnpj(cpf_cnpj)
        if valida_cpf.valida():
            pass
        else:
            return ({'message': 'CPF/CNPJ inválido!'}, 400)
    else:
        return ({'message': 'CPF/CNPJ não informado!'}, 400)
    try:
        conn = conexao()[0]
        cursor = conexao()[1]
        insert = (f"INSERT INTO tunap_beneficiarios (nome, cpf_cnpj, email, telefone, owner) VALUES ('{nome}', '{cpf_cnpj}', '{email}', '{telefone}', {owner})")
        cursor.execute(insert)
        

        consulta = f"select tb.id, trim(tb.nome), trim(tb.cpf_cnpj), trim(tb.email), trim(tb.telefone), tb.owner, trim(wa.usuario) FROM tunap_beneficiarios tb \
                left join wb_acesso_internet wa on tb.owner = wa.codigo \
                where tb.cpf_cnpj = {cpf_cnpj}"
        cursor.execute(consulta)
        consulta = cursor.fetchone()
        if consulta == None:
            return ({'message': 'Beneficiário não encontrado!'}, 404)
        beneficiario = {}
        beneficiario['id'] = consulta[0]
        beneficiario['nome'] = str(data.get('nome',consulta[1]))
        beneficiario['cpf_cnpj'] = str(data.get('cpf_cnpj',consulta[2]))
        beneficiario['email'] = str(data.get('email',consulta[3]))
        beneficiario['telefone'] = str(data.get('telefone',consulta[4]))
        beneficiario['id_owner'] = data.get('id_owner',consulta[5])
        beneficiario['owner'] = consulta[6]
        retorno = {}
        retorno['Beneficiario'] = beneficiario
        retorno['message'] = 'Beneficiário adicionado com sucesso!'
        cursor.close()
        conn.close()

        return (retorno, 201)
    except Exception as e:
        if 'Unique constraint' in str(e):
            conn.close()
            retorno = {'message': 'CPF/CNPJ já cadastrado!'}
            return (retorno, 400)
        else:
            conn.close()
            retorno = {'message': 'Erro ao adicionar beneficiário: ' + str(e)}
            return (retorno, 400)

def deletar_beneficiario (id):
    try:
        conn = conexao()[0]
        cursor = conexao()[1]
        cursor.execute(f"select * from tunap_beneficiarios where id = {id}")
        consulta = cursor.fetchone()
        if consulta == None:
            return ({'message': 'Beneficiário não encontrado!'}, 404)
        else:
            cursor.execute(f"delete from tunap_beneficiarios where id = {id}")
            return ({'message': 'Beneficiário deletado com sucesso!'}, 200)
    except Exception as e:
        return ({'message': 'Erro ao deletar beneficiário: ' + str(e)}, 400)
    
def atualizar_beneficiario (id, data):
    conn = conexao()[0]
    cursor = conexao()[1]
    data = request.get_json()
    consulta = f"select tb.id, trim(tb.nome), trim(tb.cpf_cnpj), trim(tb.email), trim(tb.telefone), tb.owner, trim(wa.usuario) FROM tunap_beneficiarios tb \
                left join wb_acesso_internet wa on tb.owner = wa.codigo \
                where tb.id = {id}"
    
    cursor.execute(consulta)
    consulta = cursor.fetchone()
    if consulta == None:
        return ({'message': 'Beneficiário não encontrado!'}, 404)
    beneficiario = {}
    beneficiario['id'] = consulta[0]
    beneficiario['nome'] = str(data.get('nome',consulta[1]))
    beneficiario['cpf_cnpj'] = str(data.get('cpf_cnpj',consulta[2]))
    beneficiario['email'] = str(data.get('email',consulta[3]))
    beneficiario['telefone'] = str(data.get('telefone',consulta[4]))
    beneficiario['id_owner'] = data.get('id_owner',consulta[5])
    beneficiario['owner'] = consulta[6]
    if beneficiario['cpf_cnpj'] != None:
        valida_cpf = ValidaCpfCnpj(beneficiario['cpf_cnpj'])
        if valida_cpf.valida():
            pass
        else:
            return ({'message': 'CPF/CNPJ inválido!'}, 400)
    update = f"UPDATE tunap_beneficiarios SET nome = '{beneficiario['nome']}', cpf_cnpj = '{beneficiario['cpf_cnpj']}', email = '{beneficiario['email']}', telefone = '{beneficiario['telefone']}', owner = {beneficiario['id_owner']} WHERE id = {id}"
    
    cursor.execute(update)


    consulta = f"select tb.id, trim(tb.nome), trim(tb.cpf_cnpj), trim(tb.email), trim(tb.telefone), tb.owner, trim(wa.usuario) FROM tunap_beneficiarios tb \
                left join wb_acesso_internet wa on tb.owner = wa.codigo \
                where tb.id = {id}"
    
    cursor.execute(consulta)
    consulta = cursor.fetchone()
    if consulta == None:
        return ({'message': 'Beneficiário não encontrado!'}, 404)
    beneficiario = {}
    beneficiario['id'] = consulta[0]
    beneficiario['nome'] = str(data.get('nome',consulta[1]))
    beneficiario['cpf_cnpj'] = str(data.get('cpf_cnpj',consulta[2]))
    beneficiario['email'] = str(data.get('email',consulta[3]))
    beneficiario['telefone'] = str(data.get('telefone',consulta[4]))
    beneficiario['id_owner'] = data.get('id_owner',consulta[5])
    beneficiario['owner'] = consulta[6]
    cursor.close()
    conn.close()
    retorno = {}
    retorno['message'] = 'Beneficiário atualizado com sucesso!'
    retorno['beneficiario'] = beneficiario
    
    return (retorno, 200)