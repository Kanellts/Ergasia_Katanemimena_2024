import blockchain
import datetime
from collections import OrderedDict
from Crypto.Hash import SHA256
import json

class Block:
	def __init__(self, index=-1, previousHash=None):
		self.index = index
		self.previousHash = previousHash
		self.timestamp = datetime.datetime.now().timestamp()
		self.nonce = 0 #this should be the public key of the validator / Proof of stake
		self.listOfTransactions = []
		self.hash = None

	def add_transaction(transaction transaction, blockchain blockchain):

		#TODO: add a transaction to the block

	def listToSerialisable(self):
		final = []
		for trans in self.listOfTransactions:
			final.append(trans.__dict__)
		return final
		#TODO: is that the correct function? ( λειπει
		# μια συνάρτηση get που καλείται από το rest.py
		# και θα μας δείχνει όλο το ιστορικό των transactions που έχουν γίνει)

	def myHash(self):
		hash_data = OrderedDict(
			[('index', self.index), ('prev', self.previousHash), ('tmsp', self.timestamp), ('nonce', self.nonce),
			 ('transactions', self.listToSerialisable())])
		tmp = json.dumps(hash_data)
		return SHA256.new(tmp.encode()).hexdigest()

	def print_block(self):
		print('\n__Block no:' + str(self.index) + '__')
		print('prev hash: \t' + str(self.previousHash))
		print('timestamp: \t' + str(self.timestamp))
		print('nonce: \t\t' + str(self.nonce))
		print('transactions: \t')
		for t in self.listOfTransactions:
			print('\t\tsender id: ' + str(t.senderID) + ' \t\treceiver id: ' + str(
				t.receiverID) + ' \t\tamount: ' + str(t.amount))
			print('\t\thash: ' + str(t.id))
		print('hash: \t\t' + str(self.hash))



