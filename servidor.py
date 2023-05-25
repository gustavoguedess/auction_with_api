from flask import Flask, request, jsonify
from flask_sse import sse
from datetime import datetime, timedelta
from threading import Thread
from flask_cors import CORS
import requests

import time

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')

cors = CORS(app)

class Produto:
    def __init__(self, codigo, nome, descricao, preco_inicial, duracao, criador):
        self.codigo = codigo
        self.nome = nome
        self.descricao = descricao
        self.tempo_final = datetime.now() + timedelta(seconds=duracao) 
        self.lance = preco_inicial
        self.comprador = ""
        self.interessados = [criador]

    def set_lance(self, valor, usuario):
        if valor > self.lance or (valor >= self.lance and self.comprador==""):
            self.lance = valor
            self.comprador = usuario
            if usuario not in self.interessados:
                self.interessados.append(usuario)

            for interessado in self.interessados:
                sse.publish(f"Novo lance no produto {self.nome} de R${self.lance}!", type='notificao', channel=interessado)

            return True
        return False
    
    def finalizar_produto(self):
        for interessado in self.interessados:
            if self.comprador == "":
                mensagem = f"Produto {self.nome} expirou. Nenhum comprador :("
            else:
                mensagem = f"Produto {self.nome} expirou. O comprador foi {self.comprador} com o valor de R$ {self.lance}!"
            sse.publish(mensagem, type='notificao', channel=interessado)
        
    def disponivel(self):
        return self.tempo_final > datetime.now()

class Leilao:
    def __init__(self):
        self.produtos = []
        self.clientes = []

    def add_cliente(self, usuario):
        self.clientes.append(usuario)

    def add_produto(self, codigo, nome, descricao, preco_inicial, duracao, usuario):
        if usuario not in self.clientes:
            return "USER_NOT_FOUND"
        
        for produto in self.produtos:
            if produto.codigo == codigo:
                return "PRODUCT_ALREADY_EXISTS"

        produto = Produto(codigo, nome, descricao, preco_inicial, duracao, usuario)
        self.produtos.append(produto)

        for cliente in self.clientes:
            sse.publish(f"Novo produto cadastrado: {produto.nome}! Lance inicial de R$ {produto.lance}!", type='notificao', channel=cliente)

        return "SUCCESS"
    
    def remove_produto(self, codigo):
        for produto in self.produtos:
            if produto.codigo == codigo:
                produto.finalizar_produto()
                self.produtos.remove(produto)
                return True
        return False
    
    def get_produtos(self):
        lista_produtos = []
        for produto in self.produtos:
            lista_produtos.append(
                {
                    "codigo": produto.codigo,
                    "nome": produto.nome,
                    "descricao": produto.descricao,
                    "lance": produto.lance,
                    "comprador": produto.comprador,
                    "tempo_final": produto.tempo_final.strftime("%d/%m/%Y %H:%M:%S"),
                }
            )
        
        return lista_produtos

    def dar_lance(self, usuario, codigo, valor):
        if usuario not in self.clientes:
            return "USER_NOT_FOUND"
        
        for produto in self.produtos:
            if produto.codigo == codigo:
                if produto.set_lance(valor, usuario):
                    return "SUCCESS"
                return "INVALID_VALUE"
        return "PRODUCT_NOT_FOUND"

def main():
    print("Servidor de leilão iniciado")

    while True:
        for produto in leilao.produtos:
            if not produto.disponivel():
                print(F"Produto {produto.nome} expirou. O comprador foi {produto.comprador} com o valor de R$ {produto.lance}!")
                
                url = "http://localhost:5000/produto"
                payload = {
                    "codigo": produto.codigo
                }
                requests.delete(url, json=payload)
        time.sleep(5)


leilao = Leilao()

##################### ROTAS #################################

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/usuario/<user>', methods=['POST'])
def cadastro(user):
    if user in leilao.clientes:
        return jsonify({"message": "Usuário já cadastrado"}), 400
    
    leilao.add_cliente(user)

    return jsonify({"message": f"Usuário {user} cadastrado com sucesso! :)"}), 200

# receive query
@app.route('/lance', methods=['POST'])
def lance():
    data = request.json

    try:
        usuario, codigo, valor = data['usuario'], data['codigo'], data['valor']
    except Exception as e:
        return jsonify({'error': 'Schema error'}), 400
    
    status = leilao.dar_lance(usuario, codigo, valor)

    if status == "USER_NOT_FOUND":
        return jsonify({"message": "Usuário não cadastrado"}), 400
    if status == "INVALID_VALUE":
        return jsonify({"message": "Lance não aceito. Valor menor que o atual"}), 400
    if status == "PRODUCT_NOT_FOUND":
        return jsonify({"message": "Produto não encontrado"}), 400
    if status == "SUCCESS":
        return jsonify({"message": "Lance efetuado com sucesso! :)"}), 200

@app.route('/produtos', methods=['POST'])
def cadastro_produto():
    data = request.json

    try:
        codigo, nome, descricao, preco_inicial, duracao, usuario = data['codigo'], data['nome'], data['descricao'], data['preco_inicial'], data['duracao'], data['usuario']
    except Exception as e:
        return jsonify({'error': 'Schema error'}), 400


    status = leilao.add_produto(codigo, nome, descricao, preco_inicial, duracao, usuario)

    if status == "USER_NOT_FOUND":
        return jsonify({"message": "Usuário não cadastrado"}), 400
    if status == "PRODUCT_ALREADY_EXISTS":
        return jsonify({"message": "Produto já cadastrado"}), 400
    if status == "SUCCESS":
        return jsonify({"message": "Produto cadastrado com sucesso! :)"}), 200
    
@app.route('/produtos', methods=['GET'])
def get_produtos():
    produtos = leilao.get_produtos()
    return jsonify(produtos), 200

@app.route('/produto', methods=['DELETE'])
def remove_produto():
    data = request.json

    try:
        codigo = data['codigo']
    except Exception as e:
        return jsonify({'error': 'Schema error'}), 400

    status = leilao.remove_produto(codigo)

    if status:
        return jsonify({"message": "Produto removido com sucesso! :)"}), 200
    else:
        return jsonify({"message": "Produto não encontrado"}), 400


if __name__ == '__main__':
    Thread(target=main).start()

    app.run(host='localhost', port=5000, debug=True)