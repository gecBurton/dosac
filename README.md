Yet Another wrapper around GPT, written for fun and to explore if it is possible to have:

* The simplest possible Text only Interface - as far as possible all features are accessed via chat:
  * wikipedia search
  * document selection, deletion, and search
  * help
* The simplest possible Postgres-based architecture:
  * [Queues](https://github.com/django-q2/django-q2) are Postgres 
  * The [Vector-Store](https://github.com/pkavumba/django-vectordb) is Postgres
* The simplest possible langchain/langgraph set up where:
  * all features are tools accessed via the prebuilt [ReAct agent](*https://langchain-ai.github.io/langgraph/how-tos/create-react-agent/)
  * appropriate citations are sourced after the text has been streamed to the user for speed

Inspired in equal measure by:
* https://github.com/i-dot-ai/redbox/
* In The Thick of It

![image](https://github.com/user-attachments/assets/a95a56f9-3476-4e4d-a0a3-7ed7e3f502cc)

### How to run via docker:

1. create a .env file, see .env.example
2. `docker compose up -d`
3. `docker compose run python manage createsuperuser`
4. Then login via the admin http://localhost:8080/admin/ (or grep the logs looking for the magic link)
