# Projeto: cadastro de empresa/usuario - login - perfil - vagas

## O que este projeto faz
Funcionalidades:
- Cadastro de usuário e empresa
- Login
- Perfil com upload de currículo (PDF)
- Cadastro e listagem de vagas
- Candidatura em vagas
- Edição de vagas pela empresa

## 1) Criar o banco no MySQL Workbench
Abra o arquivo `schema.sql` no MySQL Workbench e execute tudo.

Isso vai criar:
- banco `projeto_senac_db`
- tabela `empresas`
- tabela `usuarios`
- tabela `vagas`
- tabela `candidaturas`

## 2) Configurar a senha do MySQL
No arquivo `app.py`, altere:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "SUA_SENHA_AQUI",
    "database": "projeto_senac_db"
}
```

## 3) Instalar dependências
No terminal, dentro da pasta do projeto:
```bash
pip install -r requirements.txt
```

## 4) Rodar o projeto
```bash
python app.py
```

## 5) Abrir no navegador
```bash
http://127.0.0.1:5000
```

## Rotas
- `/login`
- `/cadastro-empresa`
- `/cadastro-usuario`
- `/editar-vaga`
- `/nova-vaga`
- `/vagas`
- `/perfil`
- `/feed`
- `/logout`

## Observação
As imagens do logo não foram incluídas. Se você já tiver o arquivo `canva-logo.png`, coloque em:
`static/images/canva-logo.png`
