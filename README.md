# Full Text Searcher API


Projeto de MVP realizado para o curso de Pós graduação em Engenharia de Software da PUC-Rio - Pontifícia Universidade Católica do Rio de Janeiro.  


## Sumário

- [Objetivo](#objetivo)
- [Tecnologias](#tecnologias)
- [Arquitetura](#arquitetura)
- [Full Text Searcher](#full-text-searcher)
- [Configuração e Instalação](#configuração-e-instalação)
	- [Utilizando o Docker compose](#utilizando-o-docker-compose)
	- [Utilizando somente o Docker](#utilizando-somente-o-docker)
- [Endpoints](#endpoints)



## Objetivo

Com o objetivo de difundir o conhecimento aos direitos e deveres dos brasileiros, esse projeto vem a oferecer um pesquisador de texto completo para a Constituição Federal de 1988.  

Também oferece uma sessão de fórum para artigos e comentários, sendo assim uma troca de conhecimento entre os usuários.  

Esse projeto é um MVP e pretende evoluir para que, tanto o pesquisador de texto quanto a sessão de artigos, possam desenvolver novas funcionalidades que irão melhorar a busca de texto e ampliar a sessão do fórum, para que usuários possam trocar conhecimento respondendo a comentários existentes, inserir outros conteúdos além de texto.  

Esse é um sistema implementado em micro serviços, sendo esse componente chamado de `Full Text Searcher API`. O serviço `MVP2 Backend APP` faz a integração de todos os serviços. Para maiores informações ver os repositórios de [MVP2 Backend APP](https://github.com/lucas-rodrigues0/mvp2_backend_app) e [Forum API](https://github.com/lucas-rodrigues0/forum_api)


## Tecnologias

- [Python](https://www.python.org/)
- [Flask-openapi3](https://luolingchun.github.io/flask-openapi3/v3.x/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [SQLAlchemy-Utils](https://sqlalchemy-utils.readthedocs.io/en/latest/index.html)
- [PostgreSQL](https://www.postgresql.org/)
- [Whoosh](https://whoosh.readthedocs.io/en/latest/index.html)
- [PyPDF2](https://pypdf2.readthedocs.io/en/3.x/)
- [Docker](https://docs.docker.com/)
- [Docker compose](https://docs.docker.com/compose/)


## Arquitetura

O sistema é composto por três APIs e um serviço externo (Auth0). São chamados de:
- MVP2_BACKEND_APP
- FULL_TEXT_SEARCHER_API
- FORUM_API
- Auth0 (serviço externo de Autenticação de usuários)

Os detalhes das componentes 'MVP2 Backend APP' e 'Forum API' estão descritos em seus respectivos documentos. Sendo aqui apenas referenciados para melhor compreensão.  
O fluxograma apresentado no documento de 'MVP2 Backend APP' mostra as relações entre os componentes.

Também é utilizado um container postgres para o sistema de banco de dados. São necessários dois databases distintos. Um para o Forum API e outro para o Full Text Searcher API.  

Para o desenvolvimento é utilizado o Docker compose para orquestrar a construção e a inicialização dos containers de cada serviço. Mas caso for subir os serviços sem o Docker Compose, subir primeiro o container do postgres, pois ele será necessário para a inicialização do serviço de Full Text Searcher API. Na sessão de instalação há mais informação.  

Para a utilização do Docker Compose é importante ficar atento a estrutura de diretório a ser montada, para o docker compose fazer o build das imagens necessárias.

O arquivo `docker-compose.yml` incluído no repositório de 'MVP2 Backend APP' segue as instruções para a seguinte estrutura de diretório: 

```
.
├── database/
├── forum_api/
├── mvp2_backend_app/
├── full_text_searcher_api/
│   ├── full_text_searcher/
│   │   ├── resources/
│   │   │   └── CF.pdf
│   │   ├── __init__.py
│   │   ├── pdf_parser.py
│   │   └── searcher.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── connection.py
│   │   └── pdf_pages.py
│   ├── schemas/
│   |   ├── __init__.py
│   |   ├── error.py
│   |   └── searcher.py
│   ├── api.py
│   ├── init_api.py
│   ├── README.md
│   ├── Dockerfile
│   └── requirements.txt
└── docker-compose.yml
```

O diretório `database` é criado através do docker compose como volume do container do postgres. A estrutura dos diretórios dos serviços `mvp2 backend app` e `forum api` são apresentados em seus respectivos documentos.
O arquivo de docker-compose.yml deverá estar no diretório raiz junto com os diretórios de todos os serviços para que a orquestração possa fazer o build das respectivas imagens. 


## Full Text Searcher

O serviço é uma Api REST que realiza uma busca de texto completo em um documento PDF da Constituição Federal brasileira. O documento é indexado pela biblioteca python Whoosh.  

Ao inicializar o container é executado automaticamente um script que faz a indexação do PDF. O PDF é analisado em páginas. É também analisado o sumário da Constituição para que possa classificar os títulos e capítulos que o conteúdo de cada página pertence.
As variáveis de ambiente `CF_SUMARIO_FIRST_PAGE`, `CF_SUMARIO_LAST_PAGE` e `CF_LAST_PAGE` são utilizadas para indicar onde está o sumário para coletar as referência a essas páginas. Para o PDF atual pode utilizar os valores que estão no arquivo `.env-example`.

Ao analisar o PDF é indexado o seu conteúdo e a referência de qual página esse conteúdo se encontra. Se a página fizer referência a um Título e um Capítulo também fica referenciado no index.
Os dados são salvos no banco de dados postgres apenas para referência futura. O index é salvo em um diretório específico, e é onde a pesquisa realmente ocorre.

Para a pesquisa podem ser requisitados múltiplos termos em uma busca. Serão encontrados documentos que apresentem alguns ou todos os termos requisitados.
A pesquisa pelo conteúdo segue orientação para escolher as buscas que apresentam o maior número de correspondências. Seguindo a definição de `OR` entre os termos. Por exemplo, se uma pesquisa tiver `term=direito justiça`, a busca será com os termos `direito OR justiça`. Os resultados que possuírem os dois terão um score maior que o documento que tiver somente um dos dois.
Caso queira pesquisar por todos os termos requisitados, deverá explicitar na busca `term=direito AND justiça`.

## Configuração e Instalação

As variáveis API_PORT e DEBUG são opcionais para o desenvolvimento. No App é sugerido utilizar a porta 4000, mas caso queira trocar, alterar esse valor pela  variável é possível, mas será necessário alterar as portas no Dockerfile e docker-compose para as portas serem expostas corretamente.
A variável Debug é apenas para o desenvolvimento da aplicação Flask. Ele permite que o Flask rode em debug mode, e é realizado o auto reload quando há alteração de código.  

Para a conexão com o banco de dados é necessário inserir os valores corretos no `.env`. Os valores no arquivo `.env-example` são uma sugestão:
```
PG_DATABASE=<nome do database a ser criado>
PG_USER=<usuário postgres>
PG_PASSWORD=<senha postgres>
PG_HOST=<nome do container postgres criado>
PG_PORT=<porta exposta pelo container postgres>
```

### Utilizando o Docker compose
É necessário ter instalado o [Docker](https://docs.docker.com/engine/install/) e o [Docker Compose](https://docs.docker.com/compose/install/) para subir os serviços automaticamente.  

O arquivo `docker-compose.yml` deverá ser movido para a raiz do projeto com a estrutura de diretórios de todos os serviços montada conforme descrito na seção [Arquitetura](#arquitetura). 

É necessário criar os arquivos `.env` para cada serviço. O arquivo `.env-example` pode ser copiado e preenchido com os valores corretos.

Execute o comando para fazer o build das imagens Docker e inicializar os container na ordem necessária.
```
docker compose up -d
```

Depois que subir todos os containers, pode acessar o endereço do serviço MVP2 Backend APP em seu navegador
```
http://127.0.0.1:5000/
```

Para acessar somente esse serviço:
```
http://127.0.0.1:4000/
```

### Utilizando somente o Docker

É necessário ter instalado o [Docker](https://docs.docker.com/engine/install/).

É necessário criar os arquivos `.env` para cada serviço. O arquivo `.env-example` pode ser copiado e preenchido com os valores corretos.

> [!NOTE]  
> Caso ainda não tenha feito esses passos ao subir os outros serviços.

Para subir o ambiente sem o docker compose é importante criar uma network para que os serviços possam se conectar entre si.
Para criar uma network do tipo bridge com o nome de `app-network` execute o comando:
```
docker network create -d bridge app-network
```

Caso já tenha criado algum container, tipo o container db, e queira conectar esse container a network app-network, execute o comando:
```
docker network connect app-network db
```

Depois de criada a network, vamos subir um container com o banco postgres. O container terá o nome de 'db', estará conectado a network criada, a senha do postgres e o volume para a persistência dos dados.
execute os comandos:
```
docker pull postgres
docker run --name db --network app-network -e POSTGRES_PASSWORD=postgres -v ./database/postgres:/var/lib/postgresql/data -d postgres
```

Depois de iniciado o container do postgres podemos subir os outros containers em qualquer ordem.  
Para iniciar o serviço Full Text Searcher API, primeiro temos que fazer o build da imagem.
Estando no mesmo nível em que o Dockerfile do full_text_searcher_api se encontra, executar o comando:
```
docker build -t searcher-api .
```
depois de construída a imagem podemos executar o container com o comando:
```
docker run --name searcher-api -p 4000:4000 --network app-network -d searcher-api
```
Para subir os outros serviços veja as informações em seus respectivos documentos.
Depois de subir os outros serviços da mesma forma, podemos testar o acesso através do MVP2 Backend APP no navegador pelo endereço.
```
http://127.0.0.1:5000/
```

Para acessar somente esse serviço:
```
http://127.0.0.1:4000/
```



## Endpoints

- #### GET /searcher?query=
Pesquisa de Texto completo pelos termos indicados no parâmetro de query.

