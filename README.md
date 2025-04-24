# Projeto Sistema de Login em Conformidade com a LGPD

Este projeto é uma aplicação web desenvolvida em Python utilizando o framework Flask, que implementa um sistema de login e registro de usuários em conformidade com a Lei Geral de Proteção de Dados (LGPD) do Brasil.

## Objetivo

O objetivo principal do sistema é garantir que o tratamento dos dados pessoais dos usuários seja feito de forma segura e transparente, respeitando os direitos previstos na LGPD. Para isso, o sistema inclui funcionalidades como:

- Registro de usuários com consentimento explícito da política de privacidade.

- Envio de código de verificação por e-mail para validação do cadastro.

- Login seguro com verificação de e-mail.

- Registro e controle de consentimentos dos usuários.

- Registro de logs de acesso para auditoria.

- Funcionalidade para os usuários solicitarem acesso, retificação, exclusão ou portabilidade dos seus dados pessoais.
- Página dedicada à política de privacidade, acessível a qualquer momento.

## Estrutura do Projeto

- **app.py**: Arquivo principal que configura a aplicação Flask, define as rotas e a lógica de controle.

- **models.py**: Define as classes de modelo para usuários e solicitações de dados, incluindo métodos para manipulação no banco de dados.

- **database.py**: Contém a configuração e inicialização do banco de dados SQLite, com as tabelas necessárias para usuários, consentimentos, logs e solicitações.

- **env_email.py**: Configuração para envio de e-mails, utilizado para enviar códigos de verificação aos usuários.

- **templates/**: Diretório com os arquivos HTML que compõem as páginas da aplicação, utilizando Jinja2 para renderização dinâmica.

- **static/**: Contém arquivos estáticos como CSS, JavaScript e imagens.

## Funcionalidades Principais

- **Registro e Login**: Usuários podem se registrar e precisam aceitar a política de privacidade para concluir o cadastro. Após o registro, recebem um código de verificação por e-mail para ativar a conta. 

- **Política de Privacidade**: Disponível em uma página dedicada, com link no cabeçalho e no formulário de registro, abrindo em nova aba.

- **Solicitações de Dados**: Usuários autenticados podem fazer solicitações relacionadas aos seus dados pessoais, conforme previsto na LGPD.

- **Controle de Acesso**: Apenas usuários autenticados podem acessar áreas restritas como o dashboard e solicitações.

- **Segurança**: Senhas são armazenadas de forma segura utilizando hashing, e o sistema exige verificação por e-mail antes do login.

## Como Executar

1. Certifique-se de ter o Python instalado.
2. Instale as dependências necessárias (Flask, Werkzeug, etc.).
3. Execute o arquivo `app.py` para iniciar o servidor.
4. Acesse a aplicação via navegador no endereço `http://localhost:5000`.

## Considerações Finais

Este projeto serve como uma base para sistemas que precisam estar em conformidade com a LGPD, demonstrando boas práticas de segurança, privacidade e transparência no tratamento de dados pessoais.

---
