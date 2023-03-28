from flask import Flask, jsonify, request, make_response
from dotenv import load_dotenv
# from functions.conexao import conexao
import os

from functions.solicitacoes_pagamento import listar_solicitacao_pagamento
from functions.beneficiarios import listar_beneficiarios, inserir_beneficiario, deletar_beneficiario, atualizar_beneficiario
from functions.grupos import criar_grupo
load_dotenv()

app = Flask(__name__)
@app.route('/')
def index():
    return 'Web App with Python Flask!'

# Rota para obter a lista de beneficiários
@app.route('/beneficiarios', methods=['GET'])
def get_beneficiarios():
    limit = request.args.get('limit', 20)
    page = request.args.get('page', 1)
    owner = request.args.get('owner', None)
    nome = request.args.get('nome', None)
    cpf_cnpj = request.args.get('cpf_cnpj', None)
    email = request.args.get('email', None)
    id_owner = request.args.get('id_owner', None)

    beneficiarios = listar_beneficiarios(id_owner, nome, limit, page, owner, cpf_cnpj, email)
    return make_response(jsonify(beneficiarios[0]), beneficiarios[1])

# Rota para adicionar um novo beneficiário
@app.route('/beneficiarios', methods=['POST'])
def add_beneficiario():
    data = request.get_json()
    resposta = inserir_beneficiario(data)
    return make_response(jsonify(resposta[0]), resposta[1])
    

# Rota para excluir um beneficiário existente
@app.route('/beneficiarios/<int:id>', methods=['DELETE'])
def delete_beneficiario(id):
    resposta = deletar_beneficiario(id)
    return make_response(jsonify(resposta[0]), resposta[1])
    
    
# Rota para atualizar um beneficiário existente
@app.route('/beneficiarios/<int:id>', methods=['PUT'])
def update_beneficiario(id):
    resposta = atualizar_beneficiario(id, request.get_json())
    return make_response(jsonify(resposta[0]), resposta[1])

# Rota para criar um grupo
@app.route('/grupos', methods=['POST'])
def create_grupo():
    resposta = criar_grupo(request.get_json())
    return make_response(jsonify(resposta[0]), resposta[1])

# # Rota para listar todos os grupos
# @app.route('/grupos', methods=['GET'])
# def get_grupos():
#     conn = conexao()[0]
#     cursor = conexao()[1]
    
#     cursor.execute("select id, nome from tunap_grupos")
#     consulta = cursor.fetchall()
#     grupos = []
#     for row in consulta:
#         grupo = {}
#         grupo['id'] = row[0]
#         grupo['nome'] = row[1]
#         grupos.append(grupo)
#     if consulta == None:
#         return make_response(jsonify({'message': 'Nenhum grupo encontrado!'}), 404)
#     retorno = {}
#     retorno['grupos'] = grupos
#     retorno['message'] = 'Grupos listados com sucesso!'
#     cursor.close()
#     conn.close()
#     return make_response(jsonify(retorno), 200)

# # Rota para atualizar um grupo existente
# @app.route('/grupos/<int:id>', methods=['PUT'])
# def update_grupo(id):
#     conn = conexao()[0]
#     cursor = conexao()[1]
#     data = request.get_json()
#     nome = data.get('nome')
#     cursor.execute(f"select count(*) from tunap_grupos where id = {id}")
#     consulta = cursor.fetchone()[0]
#     if consulta == 0:
#         return make_response(jsonify({'message': 'Grupo não encontrado!'}), 404)
#     cursor.execute(f"update tunap_grupos set nome = '{nome}' where id = {id}")
#     conn.commit()
#     conn.close()
#     retorno = {}
#     retorno['message'] = 'Grupo atualizado com sucesso!'
#     return make_response(jsonify(retorno), 200)

# # Rota para alterar grupo da empresa
# @app.route('/empresas', methods=['PUT'])
# def update_empresa():
#     conn = conexao()[0]
#     cursor = conexao()[1]
#     data = request.get_json()
#     id_grupo = data.get('id_grupo')
#     cod_empresa = str(data.get('cod_empresa'))
#     consulta = f"select cod_cliente, id_empresa, id_grupo from clientes \
#                 left join tunap_link_grupos_empresas on id_empresa = cod_cliente \
#                 where cod_cliente={cod_empresa}"
#     cursor.execute(consulta)
#     consulta = cursor.fetchone()
#     cliente = {}
#     cliente['cod_cliente'] = consulta[0]
#     cliente['id_empresa'] = consulta[1]
#     cliente['id_grupo'] = consulta[2]
#     retorno = {}
#     cursor.execute(f"select count(*) from tunap_grupos where id = {id_grupo}")
#     consulta = cursor.fetchone()
#     if consulta[0] == 0:
#         return make_response(jsonify({'message': 'Grupo não encontrado!'}), 404)
#     if cliente['id_grupo'] == None:
#         insert = f"insert into tunap_link_grupos_empresas (id_empresa, id_grupo) values ('{cod_empresa}', {id_grupo})"
#         print(insert)
#         cursor.execute(insert)
#         retorno['message'] = 'Grupo da empresa atualizado com sucesso!'
#         return make_response(jsonify(retorno), 200)
#     else:
#         update = f"update tunap_link_grupos_empresas set id_grupo = {id_grupo} where id_empresa = {cod_empresa}"
#         cursor.execute(update)
#         retorno['message'] = 'Atualizado com sucesso!'
#         return make_response(jsonify(retorno), 200)

# Rota para listar as solicitações de pagamento
@app.route('/solicitacao_bonificacao', methods=['GET'])
def get_solicitacao_bonificacao():
    json = listar_solicitacao_pagamento()
    return make_response(jsonify(json[0]), json[1])

# Definir um manipulador de erro personalizado para erros 404
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': 'Página não encontrada'}), 404

app.run(host='0.0.0.0', port=5000)