from pymongo import MongoClient

from app.core.config import settings

# connect=False: adia a conexão real até o primeiro uso. Sem isso, o client
# conecta no import — que no worker Celery acontece no processo pai, antes do
# fork — e os forks herdam a conexão compartilhada (warning "MongoClient opened
# before fork", risco de deadlock documentado pelo pymongo).
client = MongoClient(settings.mongo_uri, connect=False)
db = client[settings.mongo_db]