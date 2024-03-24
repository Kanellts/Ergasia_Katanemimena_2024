import block


#TODO: is this really proof of stake and not proof of work??
class Blockchain:

    def __init__(self):
        ##set
        self.block_list = []

    # create bootstrap_node and
    # genesis block(previous_hash = 1, nonce = 0)
    def create_blockchain(self, genesis_trans):
        genesis = block.Block(index=0, previousHash=1)
        genesis.listOfTransactions.append(genesis_trans)
        genesis.hash = genesis.myHash()
        self.add_block(genesis)  # only genesis block is added instantly to blockchain
        return

    def print_chain(self):
        print("\n___PRINT CHAIN___")
        for b in self.block_list:
            b.print_block()

    # add to chain
    def add_block(self, new_block):
        # print("add_block")
        self.block_list.append(new_block)
        self.print_chain()
        print('length: \t' + str(len(self.block_list)))