import copy
import json
import time

import numpy as np
import requests
from flask import Flask, request
from flask_cors import CORS

import block
import blockchain
import node
import transaction

app = Flask(__name__)
CORS(app)
blockchain = blockchain.Blockchain()

PORT = '5000'  # specify your port here in string format
TOTAL_NODES = 0
NODE_COUNTER = 0

btsrp_url = 'http://192.168.0.1:' + PORT  # communication details for bootstrap node
myNode = node.node()
btstrp_IP = '192.168.0.1'


# bootstrap node initializes the app, create genesis block and add boostrap to dict to be broadcasted
@app.route('/init/<total_nodes>', methods=['GET'])
def init_connection(total_nodes):
    global TOTAL_NODES
    global PORT
    TOTAL_NODES = int(total_nodes)
    print('App starting for ' + str(TOTAL_NODES) + ' nodes')
    genesis_trans = myNode.create_genesis_transaction(TOTAL_NODES)
    myNode.valid_chain.create_blockchain(genesis_trans)  # also creates genesis block
    myNode.id = 0
    myNode.register_node_to_ring(myNode.id, btstrp_IP, PORT, myNode.wallet.public_key)
    return "Init OK\n", 200


# node requests to boostrap connect to the ring
@app.route('/connect/<myIP>/<port>', methods=['GET'])
def connect_node_request(myIP, port):
    # print('Node wants to connect')
    myInfo = 'http://' + myIP + port
    message = {'ip': myIP, 'port': port, 'public_key': myNode.wallet.public_key}
    message['flag'] = 0  # flag=0 if connection request
    m = json.dumps(message)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.post(btsrp_url + "/receive", data=m, headers=headers)

    data = response.json()  # dictionary containing id + chain
    error = 'error' in data.keys()
    if (not error):
        potentialID = int(data.get('id'))
        current_chain = data.get('chain')
        current_wallets = data.get('wallets')
        wallet_snapshot = data.get('wallet_snapshot')
        myNode.id = potentialID
        myNode.wallet.wallets = current_wallets
        myNode.wallet.wallet_snapshot = wallet_snapshot
        myNode.add_block_list_to_chain(myNode.valid_chain.block_list, current_chain)
        message = {}
        message['public_key'] = myNode.wallet.public_key
        message['flag'] = 1  # if request success and transaction is due

        response = requests.post(btsrp_url + "/receive", data=json.dumps(message), headers=headers)
        return "Connection for IP: " + myIP + " established,\nOK\n", 200
    else:
        return "Connection for IP: " + myIP + " to ring refused, too many nodes\n", 403


@app.route('/connect/ring', methods=['POST'])
def get_ring():
    data = request.get_json()
    newRing = {}
    for nodeID in data:
        tmp = int(nodeID)
        newRing[tmp] = copy.deepcopy(data[nodeID])
    # print(newRing)
    myNode.ring = newRing
    return "OK", 200


# bootstrap handles node requests to join the ring
@app.route('/receive', methods=['POST'])
def receive_node_request():
    global NODE_COUNTER
    global TOTAL_NODES
    receivedMsg = request.get_json()
    if receivedMsg.get('flag') == 0:
        senderInfo = 'http://' + receivedMsg.get('ip') + ':' + receivedMsg.get('port')
        print(senderInfo)
        newID = -1

        if NODE_COUNTER < TOTAL_NODES - 1:
            NODE_COUNTER += 1
            newID = NODE_COUNTER
            myNode.register_node_to_ring(newID, str(receivedMsg.get('ip')), receivedMsg.get('port'),
                                         str(receivedMsg.get('public_key')))
            new_data = {}
            new_data['id'] = str(newID)
            new_data['wallets'] = myNode.wallet.wallets
            new_data['wallet_snapshot'] = myNode.wallet.wallet_snapshot
            blocks = []
            for block in myNode.valid_chain.block_list:
                tmp = copy.deepcopy(block.__dict__)
                tmp['listOfTransactions'] = block.listToSerialisable()
                blocks.append(tmp)
            new_data['chain'] = blocks
            message = json.dumps(new_data)

            # finished with connections, broadcast final ring
            if (NODE_COUNTER == TOTAL_NODES - 1):
                myNode.broadcast_ring()
            return message, 200  # OK
        else:
            # print("_Network is full, rejected node_")
            # broadcast  final ring data
            message = {}
            message['error'] = 1
            return json.dumps(message), 403  # FORBIDDEN

    if (receivedMsg.get('flag') == 1):
        receiverID = myNode.public_key_to_ring_id(receivedMsg.get('public_key'))
        myNode.create_transaction(myNode.wallet.public_key, myNode.id, receivedMsg.get('public_key'), receiverID,
                                  "money", 1000, '')
        return "Transfered 1000 BCCs to Node\n", 200  # OK


def print_n_return(msg, code):
    print(msg)
    return msg, code


@app.route('/receive_trans', methods=['POST'])
def receive_trans():
    data = request.get_json()
    trans = transaction.Transaction(**data)

    # check if transaction is already received & remove it from unreceived
    for unrec in myNode.unreceived_trans:
        if (trans.id == unrec.id):
            myNode.unreceived_trans = [t for t in myNode.unreceived_trans if t.id == unrec.id]
            return  # ignore received transaction

    code = myNode.validate_transaction(myNode.wallet.wallets, trans)

    if (code == 'validated'):
        isBlockMined = myNode.add_transaction_to_validated(trans)

        myNode.validate_pending()

        if (isBlockMined):
            return print_n_return('Valid transaction added!\n', 200)
        else:
            return print_n_return('Valid transaction added!\n', 200)

    elif (code == 'pending'):
        myNode.add_transaction_to_pending(trans)
        return print_n_return('Transaction added to list of pending for approval\n', 200)

    else:
        return print_n_return('Error: Illegal Transaction\n', 403)


@app.route('/receive_block', methods=['POST'])
def receive_block():
    data = request.get_json()
    b = block.Block(index=int(data.get('index')), previousHash=data.get('previousHash'))
    b.timestamp = data.get('timestamp')
    b.validator = data.get('validator')
    for t in data.get('listOfTransactions'):
        tmp = transaction.Transaction(**t)
        b.listOfTransactions.append(tmp)
    b.hash = data.get('hash')
    myNode.receive_block(b)
    return "Block received OK\n", 200


# sends list of blocks as dict
@app.route('/get_blockchain', methods=['GET'])
def get_blockchain():
    message = {}
    blocks = []
    for block in myNode.valid_chain.block_list:
        tmp = copy.deepcopy(block.__dict__)
        tmp['listOfTransactions'] = block.listToSerialisable()
        blocks.append(tmp)
    message['blockchain'] = blocks
    return json.dumps(message), 200


@app.route('/chain_length', methods=['GET'])
def get_chain_length():
    message = {}
    message['length'] = len(myNode.valid_chain.block_list)
    return json.dumps(message), 200


# create new transaction
@app.route('/transaction/new', methods=['POST'])
def transaction_new():
    # print("FLAG1!!!!!!!!!!!!!!!!!!")
    data = request.get_json()
    # print("FLAG1.3!!!!!!!!!!!!!!!!!")
    id = int(data.get('id'))
    transaction_message = str(data.get('message'))
    amount = int(data.get('amount'))
    # print("FLAG1.5!!!!!!!!!!!!!!!!!!")
    if transaction_message == '':
        type_of_transaction = 'money'
    else:
        type_of_transaction = 'message'
    # ip = myNode.ring[id].get('ip')
    # port = myNode.ring[id].get('port')
    recipient_address = myNode.ring[id].get('public_key')
    senderID = myNode.id
    receiverID = myNode.public_key_to_ring_id(recipient_address)
    ret = myNode.create_transaction(myNode.wallet.public_key, senderID, recipient_address, receiverID,
                                    type_of_transaction, amount, transaction_message)
    message = {'response': ret}
    response = json.dumps(message)
    return response, 200


# get all transactions in the blockchain
@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    transactions = blockchain.transactions
    response = {'transactions': transactions}
    return json.dumps(response) + "\n", 200


@app.route('/show_balance', methods=['GET'])
def show_balance():
    balance = myNode.wallet.balance()
    response = {'Balance': balance}
    return json.dumps(response) + "\n", 200


@app.route('/show_stake', methods=['GET'])
def show_stake():
    stake = myNode.wallet.return_stake_amount()
    response = {'Stake': stake}
    return json.dumps(response) + "\n", 200

@app.route('/update_stake', methods=['POST'])
def update_stake():
    data = request.get_json()
    stake = int(data.get('amount'))
    test = myNode.wallet.stake(stake)
    if test == 0:
        return "Stake updated!" "\n", 200
    else:
        return "Stake not updated! Check how many money the node has!"

@app.route('/blockchain/view', methods=['GET'])
def view_blockchain():
    myNode.valid_chain.print_chain()
    return "OK", 200


@app.route('/transactions/view', methods=['GET'])
def view_transactions():
    last_transactions = myNode.valid_chain.block_list[-1].listOfTransactions
    validator = myNode.valid_chain.block_list[-1].return_validator()
    response = {}
    for t, i in zip(last_transactions, np.arange(len(last_transactions))):
        print(t)
        sender_pk = t.sender
        receiver_pk = t.receiver
        for id, info in myNode.ring.items():
            if info['public_key'] == sender_pk:
                sender_id = id
            if info['public_key'] == receiver_pk:
                receiver_id = id
        tmp = {}
        tmp['sender_id'] = sender_id
        tmp['receiver_id'] = receiver_id
        tmp['type_of_transaction'] = t.type_of_transaction
        tmp['message'] = t.message
        tmp['amount'] = t.amount
        tmp['validator'] = validator
        response[str(i)] = tmp
    return json.dumps(response) + "\n", 200


@app.route('/time/transaction', methods=['GET'])
def trans_time():
    start, end = myNode.trans_timer()
    response = {}
    response['start'] = f'{start[3]}:{start[4]}:{start[5]}'
    response['end'] = f'{end[3]}:{end[4]}:{end[5]}'
    time_diff_seconds = time.mktime(end) - time.mktime(start)
    time_diff_miliseconds = time_diff_seconds * 1000
    response['# transactions'] = myNode.numBlocks()
    response[' milliseconds elapsed'] = time_diff_miliseconds
    return json.dumps(response), 200


@app.route('/time/block', methods=['GET'])
def block_time():
    average = myNode.block_timer()
    response = {}
    response['average block time'] = average
    return json.dumps(response), 200


# run it once for every node
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(host='0.0.0.0', port=port)
