from flask import Flask, jsonify
from flask_cprs import CORS

import blockchain

### JUST A BASIC EXAMPLE OD A REST API WITH FLASK


app = Flask(__name__)
CORS(app)
blockchain = Blockchain()


#..............................................................................................


#get all transactions in blockchain

@app.route('/transactions/get', methods=['GET'])
def get_transaction():
	transactions = blockchain.transactions

	response = {'transactions':transactions}
	return jsonify(response,200) # ή jsonify(response) 200 όπως είχε γράψει στο βίντεο


#run it once for every node

if __name__ == '__main__':
	from argparse import ArgumentParser

	parser = ArgumentParser()
	parser.add_argument('-p','--port', default=5000, type-int, help='port to listen on') 
	args = parser.parser_args()
	port = args.port

	app.run(host='127.0.0.1',port=port)