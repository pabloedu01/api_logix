CREATE TABLE tunap_beneficiarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255),
    cpf_cnpj VARCHAR(255) UNIQUE,
    email VARCHAR(255),
    telefone VARCHAR(20),
    owner INTEGER
);