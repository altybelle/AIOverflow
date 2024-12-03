# NetOverflow - Uma abordagem para coletar e analisar questões disponíveis no StackOverflow

### Introdução

O StackExchange é uma rede colaborativa de websites de perguntas e respostas, com cada um deles cobrindo uma temática específica.
Estes websites, por sua vez, seguem uma interface comum, tratando tanto perguntas e respostas como postagens, sendo estas feitas por usuários. Postagens e usuários compõe um sistema de reputação, que permite a automoderação dos websites.

Coletar dados dos websites que utilizam desta interface é uma tarefa fácil, visto que a rede disponibiliza uma API pública com diversas funcionalidades, que permitem desde a coleção de postagens até usuários e tags. Dadas essas ferramentas, queremos analisar que tipo de dados podemos extrair das questões existentes no website StackOverflow, o website mais utilizado da rede, e responder à seguinte pergunta: Como se comportam os usuários dado o advento das LLM's e sua disponibilização ao público?

### Metodologia

Para iniciar o processo, utilizamo-nos da ferramenta "Trends" do Google, para dimensionar o interesse do público utilizador do motor de busca em tópicos como "Inteligência Artificial", "Modelos de linguagem de grande escala", "ChatGPT" e "Microsoft Copilot" num intervalo de tempo de 2019 até o momento. Baseado na análise dos dados, é perceptível que o interesse nesses temas começou a crescer abruptamente no fim de 2022, próximo à data de lançamento oficial do ChatGPT. Percebe-se, utilizando a mesma ferramenta com o mesmo intervalo de tempo, que o interesse pelo tópico "Stack Overflow" teve uma queda abrupta a partir do mesmo período. De tal forma, buscamos fazer uma análise de ambos os fenômenos e tentar determinar se há uma relação causal para estes, com base numa análise do banco de dados do próprio StackOverflow, a fim de verificar se esta tendência afeta a produção de conteúdo destinada ao website.

Por fim, definimos por intervalo de tempo relevante o mesmo período: de 2019 a 2024.
Para analisarmos esse período levando em consideração as questões do StackOverflow, devemos consultar à API versão 2.3 disponibilizada pela StackExchange, utilizando-se da rota /questions.

A rota /questions recebe por parâmetros:
| Parâmetro | Descrição |
|---|---|
| page | Página atual |
| pagesize | Quantidade de questões a serem disponibilizadas por página (máx: 100) |
| fromdate | Data inicial (timestamp) |
| todate | Data final (timestamp) |
| order | asc, desc |
| min | Data mínima |
| max | Data máxima |
| sort | activity, creation, votes, hot, week, month |
| tagged | Tags disponíveis |

Utilizamos um algoritmo em Python para fazer as requisições de forma linear, utilizando os parâmetros fixos pagesize, fromdate, todate, order, além dos parâmetro site e key, que diz respeito à aplicação que se deseja inspecionar.

Rota: https://api.stackexchange.com/2.3/questions?order=desc&sort=creation&site=stackoverflow&pagesize=100

Como o algoritmo foi projetado para ser executado por ano (escolha arbitrária), adicionados parâmetros dinâmicos (como page, fromdate e todate), de acordo com a execução do algoritmo.

Como primeira limitação percebida, aparentemente a API disponibiliza uma cota de 300 requisições por dia para usuários não cadastrados, e só permite que a paginação chegue à página 55 nessa rota. De tal forma, nos aplicamos como desenvolvedores na plataforma, de forma a evitar essas limitações e a fim de obter mais resultados em menos tempo. Com isso, a cota de requisições aumentou para 10,000. 

Foi necessário mudar a rota informando novos parâmetros de segurança, como "access_token", gerado por uma rota de autenticação da própria API, e "key", disponibilizado para a aplicação que cadastramos na plataforma.
