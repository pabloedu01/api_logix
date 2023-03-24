from flask import Flask, jsonify, request, make_response
import IfxPy
import IfxPyDbi as dbapi2
from dotenv import load_dotenv
import os
from functions.valida_cpf import ValidaCpfCnpj
load_dotenv()

app = Flask(__name__)
def conexao ():
    connection_info = "SERVER={};DATABASE=logix;HOST={};SERVICE={};UID={};PWD={};".format(
        os.environ.get('DB_CONNECTION_NAME')
        ,os.environ.get('DB_HOST')
        ,os.environ.get('DB_PORT')
        ,os.environ.get('DB_USERNAME')
        ,os.environ.get('DB_PASSWORD'))
    conn = dbapi2.connect(connection_info, "", "")
    cur = conn.cursor()
    cur.execute('set isolation to dirty read;')
    return(conn, cur)
@app.route('/')
def index():
    return 'Web App with Python Flask!'

# Rota para obter a lista de beneficiários
@app.route('/beneficiarios', methods=['GET'])
def get_beneficiarios():
    limit = request.args.get('limit', 20)
    page = request.args.get('page', 1)
    owner = request.args.get('owner', None)
    conn = conexao()[0]
    cursor = conexao()[1]
    cursor.execute('SELECT count(*) FROM tunap_beneficiarios')
    nome = request.args.get('nome', None)
    cpf_cnpj = request.args.get('cpf_cnpj', None)
    email = request.args.get('email', None)
    id_owner = request.args.get('id_owner', None)

    if nome != None:
        nome = str.upper(nome)
        consulta_nome = f" AND upper(nome) LIKE '%{nome}%'"
    else:
        consulta_nome = ''

    if id_owner != None:
        if int(id_owner):
            consulta_owner = f" AND owner = {id_owner}"
        else:
            return(make_response(jsonify({'message': 'O parâmetro owner deve ser um número inteiro!'}), 400))
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
        return make_response(jsonify({'message': 'O parâmetro limit deve ser um número inteiro!'}), 400)
    try:
        page = int(page)
    except:
        return make_response(jsonify({'message': 'O parâmetro page deve ser um número inteiro!'}), 400)
    total_page = (total / limit)
    if total_page == 0:
        total_page = 1
    
    skip_page = (page - 1) * limit
    consulta = (f'SELECT SKIP {skip_page} first {limit} tb.id, trim(tb.nome), trim(tb.cpf_cnpj), trim(tb.email), trim(tb.telefone), tb.owner, trim(wa.usuario) \
                FROM tunap_beneficiarios tb \
                left join wb_acesso_internet wa on tb.owner = wa.codigo \
                where 1=1 {consulta_nome} {consulta_cpf_cnpj}{consulta_email}{consulta_owner} ORDER BY id')
    print(consulta)
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
    # beneficiarios['qtd_paginas'] = int(total_page)
    beneficiarios['pagina_atual'] = int(page)
    return jsonify(beneficiarios)

# Rota para adicionar um novo beneficiário
@app.route('/beneficiarios', methods=['POST'])
def add_beneficiario():
    data = request.get_json()
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
            return make_response(jsonify({'message': 'CPF/CNPJ inválido!'}), 400)
    else:
        return make_response(jsonify({'message': 'CPF/CNPJ não informado!'}), 400)
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
            return make_response(jsonify({'message': 'Beneficiário não encontrado!'}), 404)
        print(consulta)
        beneficiario = {}
        beneficiario['id'] = consulta[0]
        beneficiario['nome'] = str(data.get('nome',consulta[1]))
        beneficiario['cpf_cnpj'] = str(data.get('cpf_cnpj',consulta[2]))
        beneficiario['email'] = str(data.get('email',consulta[3]))
        beneficiario['telefone'] = str(data.get('telefone',consulta[4]))
        beneficiario['id_owner'] = data.get('id_owner',consulta[5])
        beneficiario['owner'] = consulta[6]
        print(beneficiario)
        retorno = {}
        retorno['Beneficiario'] = beneficiario
        retorno['message'] = 'Beneficiário adicionado com sucesso!'
        cursor.close()
        conn.close()

        return make_response(jsonify(retorno), 201)
    except Exception as e:
        if 'Unique constraint' in str(e):
            conn.close()
            retorno = {'message': 'CPF/CNPJ já cadastrado!'}
            return make_response(jsonify(retorno), 400)
        else:
            conn.close()
            retorno = {'message': 'Erro ao adicionar beneficiário: ' + str(e)}
            return make_response(jsonify(retorno), 400)
# Rota para excluir um beneficiário existente
@app.route('/beneficiarios/<int:id>', methods=['DELETE'])
def delete_beneficiario(id):
    conn = conexao()[0]
    cursor = conexao()[1]
    
    
# Rota para atualizar um beneficiário existente
@app.route('/beneficiarios/<int:id>', methods=['PUT'])
def update_beneficiario(id):
    conn = conexao()[0]
    cursor = conexao()[1]
    data = request.get_json()
    consulta = f"select tb.id, trim(tb.nome), trim(tb.cpf_cnpj), trim(tb.email), trim(tb.telefone), tb.owner, trim(wa.usuario) FROM tunap_beneficiarios tb \
                left join wb_acesso_internet wa on tb.owner = wa.codigo \
                where tb.id = {id}"
    
    cursor.execute(consulta)
    consulta = cursor.fetchone()
    if consulta == None:
        return make_response(jsonify({'message': 'Beneficiário não encontrado!'}), 404)
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
            return make_response(jsonify({'message': 'CPF/CNPJ inválido!'}), 400)
    update = f"UPDATE tunap_beneficiarios SET nome = '{beneficiario['nome']}', cpf_cnpj = '{beneficiario['cpf_cnpj']}', email = '{beneficiario['email']}', telefone = '{beneficiario['telefone']}', owner = {beneficiario['id_owner']} WHERE id = {id}"
    
    cursor.execute(update)


    consulta = f"select tb.id, trim(tb.nome), trim(tb.cpf_cnpj), trim(tb.email), trim(tb.telefone), tb.owner, trim(wa.usuario) FROM tunap_beneficiarios tb \
                left join wb_acesso_internet wa on tb.owner = wa.codigo \
                where tb.id = {id}"
    
    cursor.execute(consulta)
    consulta = cursor.fetchone()
    if consulta == None:
        return make_response(jsonify({'message': 'Beneficiário não encontrado!'}), 404)
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
    
    return make_response(jsonify(retorno), 200)

# Rota para criar um grupo
@app.route('/grupos', methods=['POST'])
def create_grupo():
    conn = conexao()[0]
    cursor = conexao()[1]
    data = request.get_json()
    nome = data.get('nome')
    cursor.execute(f"insert into tunap_grupos (nome) values ('{nome}')")
    conn.commit()
    conn.close()
    retorno = {}
    retorno['message'] = 'Grupo criado com sucesso!'
    return make_response(jsonify(retorno), 201)

# Rota para listar todos os grupos
@app.route('/grupos', methods=['GET'])
def get_grupos():
    conn = conexao()[0]
    cursor = conexao()[1]
    
    cursor.execute("select id, nome from tunap_grupos")
    consulta = cursor.fetchall()
    grupos = []
    for row in consulta:
        grupo = {}
        grupo['id'] = row[0]
        grupo['nome'] = row[1]
        grupos.append(grupo)
    if consulta == None:
        return make_response(jsonify({'message': 'Nenhum grupo encontrado!'}), 404)
    retorno = {}
    retorno['grupos'] = grupos
    retorno['message'] = 'Grupos listados com sucesso!'
    cursor.close()
    conn.close()
    return make_response(jsonify(retorno), 200)

# Definir um manipulador de erro personalizado para erros 404
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': 'Página não encontrada'}), 404

app.run(host='0.0.0.0', port=5000)