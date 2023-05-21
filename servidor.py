from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from threading import Thread
from flask_cors import CORS

import time

app = Flask(__name__)
cors = CORS(app)

class Produto:
    def __init__(self, codigo, nome, descricao, preco_inicial, duracao, cliente):
        self.codigo = codigo
        self.nome = nome
        self.descricao = descricao
        self.tempo_final = datetime.now() + timedelta(seconds=duracao) 
        self.lance = preco_inicial
        self.comprador = ""

    def set_lance(self, valor, usuario):
        if valor > self.lance or (valor >= self.lance and self.comprador==""):
            self.lance = valor
            self.comprador = usuario

            #TODO enviar notificação

            return True
        return False
    
    def finalizar_produto(self):
        #TODO enviar notificação

        print(f"Produto {self.nome} expirou. O comprador foi {self.comprador} com o valor de R$ {self.lance}")
        
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

        return "SUCCESS"
    
    def remove_produto(self, codigo):
        for produto in self.produtos:
            if produto.codigo == codigo:
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
        print('rodando')
        for produto in leilao.produtos:
            if not produto.disponivel():
                print('produto indisponivel')
                produto.finalizar_produto()
                leilao.remove_produto(produto.codigo)
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

    return jsonify({"message": "Usuário cadastrado com sucesso! :)"}), 200

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

if __name__ == '__main__':
    # Thread(target=main).start()

    app.run(host='localhost', port=5000, debug=True)