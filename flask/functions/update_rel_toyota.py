from .db import conexao
# from flask import request

def update_relatorio_toyota (j):
    conn = conexao()[0]
    cursor = conexao()[1]
    try:
        total_linhas = 0
        for i in j:
            try:

                select = " \
                select count(*) from wb_pedidos_toyota \
                where \
                empresa='02' \
                and codigo_toyota = '{}' \
                and pedido_toyota = {}\
                and codigo_dealer = {} \
                and pedido_dealer = '{}' \
                and cliente_tunap = '{}' \
                and item_toyota = '{}' \
                and item_tunap = '{}' \
                and qtd_solic = {} \
                and val_unit = {} \
                ".format(i['cod_toyota']
                         , i['pedido_toyota']
                         ,i['codigo_dealer']
                         ,i['pedido_dealer']
                         ,i['cliente_tunap']
                         ,i['item_toyota']
                         ,i['item_tunap']
                         ,i['qtd_solic']
                         ,i['val_unit']
                         ,i['arquivo']
                         )
                cursor.execute(select)
                # cursor.fetchall()
                consulta = cursor.fetchall()[0][0]
                if consulta == 0:
                    insert = " \
                    insert into wb_pedidos_toyota \
                    (empresa, codigo_toyota, pedido_toyota, codigo_dealer, pedido_dealer, cliente_tunap, item_toyota, item_tunap, qtd_solic, val_unit, arquivo_toyota, data_pedido, hora_pedido, dat_gravavao_reg) \
                    values \
                    ('02', '{}', {}, {}, '{}', '{}', '{}', '{}', {}, {}, '{}', to_date('{}','%d/%m/%Y'), '{}', {}); \
                    ".format(i['cod_toyota']
                             , i['pedido_toyota']
                             ,i['codigo_dealer']
                             ,i['pedido_dealer']
                             ,i['cliente_tunap']
                             ,i['item_toyota']
                             ,i['item_tunap']
                             ,i['qtd_solic']
                             ,i['val_unit']
                             ,i['arquivo']
                             ,i['data_pedido']
                             ,i['hora']
                             ,'current'
                             )
                    cursor.execute(insert)
                    conn.commit()
                    # print(insert)
                    # print('Inserido')
                else:
                    print(select)
                    print('Já existe')
                # print(consulta)
            except Exception as e:
                print(e)
            total_linhas += 1
            # conn.close()
        return ({'message': 'Relatório Toyota atualizado com sucesso', 'total_beneficiarios': total_linhas}, 200)
    except Exception as e:
        # conn.close()
        print(e)
        return ({'message': 'Erro ao atualizar relatório Toyota'}, 500)