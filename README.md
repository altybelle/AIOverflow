# NetOverflow - Uma abordagem para coletar e analisar questões disponíveis no StackOverflow

### Introdução

O StackExchange é uma rede colaborativa de websites de perguntas e respostas, com cada um deles cobrindo uma temática específica.
Estes websites, por sua vez, seguem uma interface comum, tratando tanto perguntas e respostas como postagens, sendo estas feitas por usuários. Postagens e usuários compõe um sistema de reputação, que permite a automoderação dos websites.

Coletar dados dos websites que utilizam desta interface é uma tarefa fácil, visto que a rede disponibiliza uma API pública com diversas funcionalidades, que permitem desde a coleção de postagens até usuários e tags. Dadas essas ferramentas, queremos analisar que tipo de dados podemos extrair das questões existentes no website StackOverflow, o website mais utilizado da rede, e responder à seguinte pergunta: Como se comportam os usuários dado o advento das LLM's e sua disponibilização ao público?

### Metodologia

Para iniciar o processo, utilizamo-nos da ferramenta "Trends" do Google, para dimensionar o interesse do público utilizador do motor de busca em tópicos como "Inteligência Artificial", "Modelos de linguagem de grande escala", "ChatGPT" e "Microsoft Copilot". Baseado na análise dos dados, é perceptível que o interesse nesses temas começou a crescer abruptamente no fim de 2022,
próximo da data de lançamento oficial do ChatGPT. Percebe-se, utilizando a mesma ferramenta, que o interesse pelo tópico "Stack Overflow" teve uma queda abrupta a partir do mesmo período. De tal forma, buscamos fazer uma análise de ambos os fenômenos e tentar determinar se há uma relação causal para estes, com base numa análise do banco de dados do próprio StackOverflow, a fim de verificar se esta tendência afeta a produção de conteúdo destinada ao website.

Sabe-se que 