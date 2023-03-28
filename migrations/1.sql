drop table tunap_beneficiarios;
drop table tunap_grupos;
drop table tunap_link_grupos_empresas;
drop table tunap_solicitacao_pagamento;
drop table tunap_formas_pagamento;
drop table tunap_status_pagamento;
CREATE TABLE tunap_beneficiarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255),
    cpf_cnpj VARCHAR(255) UNIQUE,
    email VARCHAR(255),
    telefone VARCHAR(20),
    owner INTEGER,
    id_empresa INTEGER
);
CREATE TABLE tunap_grupos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) UNIQUE
);
CREATE TABLE tunap_link_grupos_empresas (
    id SERIAL PRIMARY KEY,
    id_empresa VARCHAR(255) UNIQUE,
    id_grupo INTEGER
);
CREATE TABLE tunap_solicitacao_pagamento (
    id SERIAL PRIMARY KEY,
    id_empresa VARCHAR(255),
    valor  FLOAT,
    forma_pagamento int
);

CREATE TABLE tunap_formas_pagamento (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255), 
    id_empresa VARCHAR(255),
    valor_total FLOAT,
    status int
);

CREATE TABLE tunap_status_pagamento (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255)
);