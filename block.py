import datetime
import json
from collections import OrderedDict
import transaction

from Crypto.Hash import SHA256


class Block:
    # constructor function of the block
    def __init__(self, index=-1, previousHash=None):
        self.index = index  # block index
        self.previousHash = previousHash  # hash of the previous block
        self.timestamp = datetime.datetime.now().timestamp()  # block's creations timestamp
        self.validator = 0  # this should be the public key of the validator / Proof of stake
        self.listOfTransactions = []  # the blocks transactions
        self.hash = None  # the block's hash

    # for when mining the block
    def block_validator(self, validator):
        self.validator = validator

    # returns a list of all the transactions this block has
    def listToSerialisable(self):
        final = []
        for trans in self.listOfTransactions:
            final.append(trans.__dict__)
        return final

    # hashes the block info
    def myHash(self):
        hash_data = OrderedDict(
            [('index', self.index), ('prev', self.previousHash), ('tmsp', self.timestamp),
             ('validator', self.validator),
             ('transactions', self.listToSerialisable())])
        tmp = json.dumps(hash_data)
        return SHA256.new(tmp.encode()).hexdigest()

    # prints the block info
    def print_block(self):
        print('\n__Block no:' + str(self.index) + '__')
        print('prev hash: \t' + str(self.previousHash))
        print('timestamp: \t' + str(self.timestamp))
        print('validator: \t\t' + str(self.validator))
        print('transactions: \t')
        for t in self.listOfTransactions:
            print('\t\tsender id: ' + str(t.senderID) + ' \t\treceiver id: ' + str(
                t.receiverID) + ' \t\tamount: ' + str(t.amount) + ' \t\tmessage: ' + str(t.message))
            print('\t\thash: ' + str(t.id))
        print('hash: \t\t' + str(self.hash))

    '''
		def add_transaction(transaction transaction, blockchain blockchain):
	'''
# TODO: add a transaction to the block function
# TODO: returns list of all the transactions that have happened to a blockchain function
