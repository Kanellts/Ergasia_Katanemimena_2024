import block
import wallet

class node:
	def __init__():
		self.NBC = 100
		##set

		#self.chain
		#self.current_id_count
		#self.NBCs
		#self.wallet

		#self.ring[] #here we store information for every node, as its id, its address (id:port) its public key and its balance


	def create_new_block():

	def create_wallet():
		#create a wallet for this node, with a public key and a private key

		#here we will place the RSA implementation

	def register_node_to_ring():
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bootstrap node informs all other nodes and gives request node an id and 100 NBCs

	def create_transaction(sender, receiver, signature):
		#remember to broadcast it

	def broadcast_transaction():


	def validate_transaction():
		#use of siganture and NBCs balance

	def add_transaction_to_block():
		#if enough transactions mine


	def mine_block():

	def broadcast_block():


	def valid_proof(... difficulty=MINING_DIFFICULTY):



	#concencus functions

	def valid_chain(self, chain):
		#check for the longer chain accross all nodes