from flask import Flask, jsonify, request, make_response
import IfxPy
import IfxPyDbi as dbapi2
from dotenv import load_dotenv
import os
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
    conn = conexao()[0]
    cursor = conexao()[1]
    cursor.execute('SELECT count(*) FROM tunap_beneficiarios')
    total = cursor.fetchone()[0]
    try:
        limit = int(limit)
    except:
        return make_response(jsonify({'message': 'O parâmetro limit deve ser um número inteiro!'}), 400)
    try:
        page = int(page)
    except:
        return make_response(jsonify({'message': 'O parâmetro page deve ser um número inteiro!'}), 400)
    total_page = total / limit
    
    skip_page = (page - 1) * limit
    if total_page < page:
        return make_response(jsonify({'message': 'A página solicitada não existe!'}), 404)
    print(skip_page)
    cursor.execute(f'SELECT SKIP {skip_page} first {limit} id, nome, cpf_cnpj, email, telefone, owner FROM tunap_beneficiarios ORDER BY id')
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
            'owner': row[5]
        }
        lista_beneficiarios.append(beneficiario)
    cursor.close()
    conn.close()
    beneficiarios['Beneficiarios'] = lista_beneficiarios
    beneficiarios['qtd_resultados'] = int(total)
    beneficiarios['qtd_paginas'] = int(total_page)
    beneficiarios['pagina_atual'] = int(page)
    return jsonify(beneficiarios)

# Rota para adicionar um novo beneficiário
@app.route('/beneficiarios', methods=['POST'])
def add_beneficiario():
    data = request.get_json()
    nome = data.get('nome')
    cpf_cnpj = data.get('cpf_cnpj')
    email = data.get('email')
    telefone = data.get('telefone')
    owner = data.get('owner')
    try:
        conn = conexao()[0]
        cursor = conexao()[1]
        cursor.execute("INSERT INTO tunap_beneficiarios (nome, cpf_cnpj, email, telefone, owner) VALUES (?, ?, ?, ?, ?)", (nome, cpf_cnpj, email, telefone, owner))
        cursor.close()
        conn.close()
        retorno = {'message': 'Beneficiário adicionado com sucesso!'}
        return make_response(jsonify({'message': 'Beneficiário adicionado com sucesso!'}), 201)
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
    try:
        cursor.execute("SELECT count(*) FROM tunap_beneficiarios WHERE id = ?", (id,))
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.close()
            conn.close()
            return make_response(jsonify({'message': 'Beneficiário não encontrado!'}), 404)
        else:
            cursor.execute("delete from tunap_beneficiarios where id = ?", (id,))
            cursor.close()
            conn.close()
            return make_response(jsonify({'message': 'Beneficiário excluído com sucesso!'}), 204)
    except Exception as e:
        retorno = {'message': 'Erro ao adicionar beneficiário: ' + str(e)}
        return make_response(jsonify(retorno), 400)
    
# Rota para atualizar um beneficiário existente
@app.route('/beneficiarios/<int:id>', methods=['PUT'])
def update_beneficiario(id):
    conn = conexao()[0]
    cursor = conexao()[1]
    try:
        cursor.execute("SELECT * FROM tunap_beneficiarios WHERE id = ?", (id,))
        beneficiario = cursor.fetchall()
        print(beneficiario)
        return make_response(jsonify(beneficiario),200)
    except Exception as e:
        cursor.close()
        conn.close()
        return make_response(jsonify({'message': 'Erro ao atualizar beneficiário: ' + str(e)}), 400)




# Definir um manipulador de erro personalizado para erros 404
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': 'Página não encontrada'}), 404

app.run(host='0.0.0.0', port=5000)