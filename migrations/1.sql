drop table tunap_beneficiarios;
drop table tunap_grupos;
drop table tunap_link_grupos_empresas;
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
    id_empresa INTEGER unique,
    id_grupo INTEGER
);