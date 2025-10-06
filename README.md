Boletim de Caixa GCONT é um app Streamlit para digitalizar o controle diário de caixa dos clientes da GCONT. Após o login autenticado, cada usuário acessa apenas os lançamentos da própria empresa, podendo registrar entradas e saídas, editar ou excluir registros já feitos, acompanhar o saldo acumulado em tempo real e exportar o movimento em TXT no layout exigido pela Domínio. Administradores têm uma área exclusiva para cadastrar novos clientes, definir históricos padronizados e criar contas contábeis, mantendo toda a base sincronizada com o banco PostgreSQL que sustenta a aplicação.

## Execução com Docker

1. Faça o build da imagem: `docker build -t boletim-caixa .`
2. Rode o contêiner informando as variáveis do banco e expondo a porta:  
   `docker run --env DB_HOST=<host> --env DB_NAME=<nome> --env DB_USER=<usuario> --env DB_PASSWORD=<senha> --env DB_PORT=5432 -p 8501:8501 boletim-caixa`

O app escuta na porta `8501` por padrão. Em provedores como o EasyPanel/Hostinger, defina a variável `PORT` e ela será respeitada automaticamente.

### Variáveis de ambiente suportadas

- `DB_HOST`: endereço do PostgreSQL (ex.: `postgres` ou `192.168.0.10`)
- `DB_NAME`: nome do banco (`boletimcaixa` por padrão)
- `DB_USER`: usuário do banco (`postgres` por padrão)
- `DB_PASSWORD`: senha do banco (`0176` por padrão)
- `DB_PORT`: porta do PostgreSQL (default `5432`)
- `DB_SSLMODE`: modo SSL opcional (ex.: `require`, `verify-full`)

Caso você já utilize `secrets.toml` no Streamlit (`.streamlit/secrets.toml`), o bloco `[db]` continua valendo e sobrescreve as variáveis acima.

### Deploy no EasyPanel (Hostinger)

- Adicione um novo serviço Docker e aponte para este repositório ou imagem.
- Configure as variáveis de ambiente listadas acima e, se o painel exigir, informe `PORT=8501`.
- Garanta que o banco PostgreSQL esteja acessível a partir do contêiner (libere firewall/VPC conforme necessário).
- Aponte o domínio/subdomínio para a aplicação pelo painel, mapeando a porta exposta pelo contêiner.
