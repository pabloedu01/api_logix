from .db import conexao
from flask import request

def listar_solicitacao_pagamento ():
    conn = conexao()[0]
    cursor = conexao()[1]
    limit = request.args.get('limit', 20)
    page = request.args.get('page', 1)
    owner = request.args.get('owner', None)
    cursor.execute('SELECT count(*) FROM tunap_beneficiarios')
    nome = request.args.get('nome', None)
    cpf_cnpj = request.args.get('cpf_cnpj', None)
    email = request.args.get('email', None)
    id_owner = request.args.get('id_owner', None)
    total = f"select count(*) from tunap_solicitacao_pagamento_detalhe where 1=1;"
    cursor.execute(total)
    total = cursor.fetchone()[0]
    if total == 0:
        retorno = {}
        retorno['message'] = 'Nenhuma solicitação encontrada!'
        retorno['solicitacoes'] = []
        return (retorno, 404)
    detalhes = []
    consulta = (f"select tsp.id \
                , tsp.id_grupo \
                , tg.nome \
                , trim(r.raz_social) \
                , tsp.owner \
                , tsp.valor_total \
                , atus.id,atus.nome \
                , tsp.created_at \
                , tsp.updated_at \
                from tunap_solicitacao_pagamento tsp \
                left join tunap_grupos tg on tsp.id_grupo = tg.id \
                left join representante r on r.cod_repres = tsp.owner \
                left join pablo.tunap_status_pagamento atus on atus.id = tsp.status \
                where 1=1")
    cursor.execute(consulta)
    consulta = cursor.fetchall()
    solicitacoes = []
    for row in consulta:
        solicitacao = {}
        solicitacao['id'] = row[0]
        solicitacao['id_grupo'] = row[1]
        solicitacao['nome_grupo'] = row[2]
        solicitacao['owner'] = row[3]
        solicitacao['id_owner'] = row[4]
        solicitacao['valor_total'] = row[5]
        solicitacao['id_status'] = row[6]
        solicitacao['status'] = row[7]
        solicitacao['created_at'] = row[8]
        solicitacao['updated_at'] = row[9]
        solicitacoes.append(solicitacao)
        select = f"select tspd.id,tlgp.id_grupo, tg.nome, tspd.id_empresa, c.nom_cliente, c.num_cgc_cpf, tspd.valor, tspd.forma_pagamento, tspd.status, tsp.nome, tspd.created_at, tspd.updated_at \
                from tunap_solicitacao_pagamento_detalhe tspd \
                left join clientes c on c.cod_cliente = tspd.id_empresa \
                left join tunap_formas_pagamento tfp on tfp.id = tspd.forma_pagamento \
                left join tunap_status_pagamento tsp on tsp.id = tspd.status \
                left join tunap_link_grupos_empresas tlgp on tlgp.id_empresa = c.cod_cliente \
                left join tunap_grupos tg on tg.id = tlgp.id_grupo \
                where tspd.id_solicitacao_pagamento = {row[0]}"
        cursor.execute(select)
        consulta = cursor.fetchall()
        
        for row in consulta:
            detalhe = {}
            detalhe['id'] = row[0]
            detalhe['id_grupo'] = row[1]
            detalhe['nome_grupo'] = row[2]
            detalhe['id_empresa'] = row[3]
            detalhe['nome_empresa'] = row[4]
            detalhe['cpf_cnpj'] = row[5]
            detalhe['valor'] = row[6]
            detalhe['forma_pagamento'] = row[7]
            detalhe['id_status'] = row[8]
            detalhe['status'] = row[9]
            detalhe['created_at'] = row[10]
            detalhe['updated_at'] = row[11]
            detalhes.append(detalhe)
        solicitacao['detalhes'] = detalhes
    
    conn.close()
    retorno = {}
    retorno['solicitacoes'] = solicitacoes
    retorno['message'] = 'Solicitações listadas com sucesso!'
    return (retorno, 200)