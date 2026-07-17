from dotenv import load_dotenv

load_dotenv()

from app.db.mongo import db

if __name__ == "__main__":
    colecao = db["teste"]
    resultado = colecao.insert_one({"mensagem": "Conexao com o banco estabelecida"})
    print("resultado inserido no id:", resultado.inserted_id)

    documento = colecao.find_one({"_id": resultado.inserted_id})
    print("Retorno: ", documento)