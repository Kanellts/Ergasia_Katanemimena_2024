import copy
import json
import threading
import time
import random

import requests
import threadpool

import block
import blockchain
import transaction
import wallet

CAPACITY = 5  # run capacity = 1, 5, 10
init_count = -1

trans_time_start = None
trans_time_end = None
block_time = 0


class node:
    def __init__(self, NUM_OF_NODES=None):
        self.wallet = wallet.Wallet()  # node's wallet
        self.id = -1  # bootstrap node will send the node's final ID
        self.valid_chain = blockchain.Blockchain() #node's blockchain
        self.ring = {}  # store info for every node (id, address (ip:port), public key, balance)
        self.pool = threadpool.Threadpool()  # node's pool of threads (use for mining, broadcast, etc)
        self.valid_trans = []  # list of validated transactions collected to create a new block
        self.pending_trans = []  # list of pending for approval trans
        self.unreceived_trans = []  # list of transactions that are known because of a received block, they are not received individually
        self.old_valid = []  # to keep a copy of validated transactions in case miner empties them while mining
        self.validator_money = 0
        #TODO: do we need pending_trans or unreceived trans?

    # returns the url of this node
    def toURL(self, nodeID):
        url = "http://%s:%s" % (self.ring[nodeID]['ip'], self.ring[nodeID]['port'])
        return url

    # returns the start and the end of the transaction
    def trans_timer(self):
        global trans_time_end, trans_time_start
        return trans_time_start, trans_time_end

    # returns the time of block
    def block_timer(self):
        global block_time
        return block_time / len(self.valid_chain.block_list)

    # returns total number of blocks
    def numBlocks(self):
        return CAPACITY * len(self.valid_chain.block_list)

    # broadcasts
    def broadcast(self, message, url):
        m = json.dumps(message)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        for nodeID in self.ring:
            if (nodeID != self.id):  # don't broadcast to myself
                nodeInfo = self.toURL(nodeID)
                requests.post(nodeInfo + "/" + url, data=m, headers=headers)
        return

    # broadcasts the transaction
    def broadcast_transaction(self, trans):
        url = "receive_trans"
        message = copy.deepcopy(trans.__dict__)
        self.broadcast(message, url)
        return

    # broadcasts the block
    def broadcast_block(self, block):
        url = "receive_block"
        message = copy.deepcopy(block.__dict__)
        message['listOfTransactions'] = block.listToSerialisable()
        self.broadcast(message, url)
        return

    # broadcasts the ring
    def broadcast_ring(self):
        print(self.ring)
        url = "connect/ring"
        message = self.ring
        self.broadcast(message, url)

    # converts a json list of dicts to blocks and returns a list of block objects
    def add_block_list_to_chain(self, valid_chain_list, block_list):
        for d in block_list:
            newBlock = block.Block(index=d.get('index'), previousHash=d.get('previousHash'))
            newBlock.timestamp = d.get('timestamp')
            newBlock.validator = d.get('validator')
            newBlock.listOfTransactions = []
            for t in d.get('listOfTransactions'):
                newBlock.listOfTransactions.append(transaction.Transaction(**t))
            newBlock.hash = d.get('hash')
            valid_chain_list.append(newBlock)
        return

    # add this node to the ring (only the bootstrap node can add a node to the ring)
    def register_node_to_ring(self, nodeID, ip, port, public_key):
        if self.id == 0:
            self.ring[nodeID] = {'ip': ip, 'port': port, 'public_key': public_key}
            if self.id != nodeID:
                self.wallet.wallets[public_key] = {}
                print(self.wallet.wallets)
        else:
            print("failed to register")
        return

    # get node's id in the ring, given its key
    def public_key_to_ring_id(self, public_key):
        for i in self.ring:
            d = self.ring[i]
            if d['public_key'] == public_key:
                return i

    # creates the genesis transaction (the one giving the initial money to bootstrap node)
    def create_genesis_transaction(self, num_of_nodes):
        data = {}
        sender = self.wallet.public_key
        amount = 1030 * (num_of_nodes - 1) + 1000

        # create genesis transaction
        data['receiver'] = data['sender'] = sender
        data['type_of_transaction'] = 'money'
        data['id'] = 0
        data['signature'] = None
        data['amount'] = amount
        data['senderID'] = 0
        data['receiverID'] = 0
        trans = transaction.Transaction(**data)  # genesis transaction

        # add genesis money to wallet
        init_wallet = {}
        init_wallet[self.wallet.public_key] = {"stake": 10, "usable_amount": amount, "nonce": 0}
        self.wallet.wallets = init_wallet  # bootstrap wallet with 1000*n BCCs
        return trans

    # creates a transaction
    def create_transaction(self, sender_public, senderID, receiver_public, receiverID, type_of_transaction,
                           amount, message):
        global trans_time_start
        if not trans_time_start:
            trans_time_start = time.gmtime(time.time())

        if amount != 0 and message != '':
            raise Exception("Choose either money-transaction or message transaction!")
        if type_of_transaction == 'money':
            if self.wallet.balance() < amount:
                raise Exception("Not enough money!")
        elif type_of_transaction == 'message':
            message_cost = len(message)
            if self.wallet.balance() < message_cost:
                print(self.wallet.balance())
                raise Exception("Not enough money!")
        else:
            raise Exception("Invalid Transaction Type")
        trxn = copy.deepcopy(
            transaction.Transaction(sender_public, senderID, receiver_public, receiverID,
                                    type_of_transaction, amount, message))
        trxn.sign_transaction(self.wallet.private_key)  # set id & signature

        if (self.validate_transaction(self.wallet.wallets,
                                      trxn) == 'validated'):  # Node validates the trxn it created
            self.add_transaction_to_validated(trxn)
            self.broadcast_transaction(trxn)
            return "Created new transaction!"
        else:
            return "Transaction not created,error"

    # does not change lists of validated or pending transactions, only returns code
    def validate_transaction(self, wallets, t):
        # verify signature
        if not t.verify_signature():
            raise Exception('invalid signature')
        if t.sender == t.receiver:
            raise Exception('sender must be different from recepient')
        if t.amount <= 0 and t.type_of_transaction == 'money':
            raise Exception('Negative amount of money in money transaction!')
        if t.message == '' and t.type_of_transaction == 'message':
            raise Exception('Empty message in message transaction!')

        if t.receiver not in wallets:  # no transaction has been made with receiver, initialize his wallet
            wallets[t.receiver] = {}
        if wallets[t.receiver] == {}:
            wallets[t.receiver] = {"usable_amount": 0, "stake": 10, "nonce": 0}
        if t.type_of_transaction == 'money':
            self.validator_money += t.amount * 0.03
            wallets[t.sender]["usable_amount"] -= t.amount * 1.03  # charging the sender
            wallets[t.sender]["nonce"] += 1  # increasing the nonce counter by 1
            wallets[t.receiver]["usable_amount"] += t.amount  # giving money to the receiver
            # print( wallets[t.receiver]["usable_amount"])
        else:
            self.validator_money += len(t.message)
            wallets[t.sender]["usable_amount"] -= len(t.message)  # charging the sender
            wallets[t.sender]["nonce"] += 1  # increasing the nonce counter by 1
        return 'validated'

    # check if any of the pending transactions can be validated
    # if it can be validated, remove it from pending and added to validated
    def validate_pending(self):
        print("validate_pending")
        for t in self.pending_trans:
            if self.validate_transaction(self.wallet.wallets, t) == 'validated':
                self.pending_trans = [t for t in self.pending_trans if t.id not in self.pending_trans]
                self.add_transaction_to_validated(t)

    # adds transaction to pending transactions
    def add_transaction_to_pending(self, t):
        self.pending_trans.append(t)

    # TODO: what does this do
    def remove_from_old_valid(self, to_remove):
        tmp = [trans for trans in self.old_valid if trans not in to_remove]
        self.old_valid = tmp

    # add transaction to list of valid_trans
    # call mine if it is full
    # return True if mining was trigerred, else False
    def add_transaction_to_validated(self, transaction):
        global CAPACITY
        self.valid_trans.append(transaction)
        self.old_valid.append(transaction)
        if len(self.valid_trans) == CAPACITY:
            print("adding transaction to validated")
            tmp = copy.deepcopy(self.valid_trans)
            self.valid_trans = []
            future = self.pool.submit_task(self.init_mining, tmp, copy.deepcopy(self.wallet.wallets))
            return True
        else:
            return False

    def receive_block(self, block):
        global lock, trans_time_end
        # tmp_wallet = copy.deepcopy(self.wallet.wallet_snapshot)

        # if we have to redo all the transactions in a block
        # if self.block_REDO(block, tmp_wallet):
        # if block.return_validator() == self.wallet.public_key:  # if node is the validator
        # lock.acquire()
        if self.validate_block(block):
            self.valid_chain.add_block(block)

            global block_time, cnt_blocks
            trans_time_end = time.gmtime(time.time())

            self.wallet.wallet_snapshot = copy.deepcopy(self.wallet.wallets)
            self.wallet.wallets[block.return_validator()]["usable_amount"] += self.validator_money
            self.validator_money = 0
            # self.wallet.wallets = copy.deepcopy(tmp_wallet)
            # lock.release()
            #
            # # UPDATE LISTS
            # # delete from my pending what was in block
            # new_pending = [trans for trans in self.pending_trans if trans not in block.listOfTransactions]
            # self.pending_trans = new_pending
            #
            # # add to my unreceived
            # new_unreceived = [trans for trans in block.listOfTransactions if
            #                   trans not in (self.old_valid and self.pending_trans)]
            # for t in new_unreceived:
            #     self.unreceived_trans.append(t)
            #
            # # update validated trans
            # new_valid = [trans for trans in self.old_valid if trans not in block.listOfTransactions]
            # self.valid_trans = []
            #
            # self.remove_from_old_valid(block.listOfTransactions)
            #
            # for t in new_valid:
            #     self.add_transaction_to_validated(t)
            # # check if new block is useful for validation of pending transactions
            # self.validate_pending()
            # TODO: our implementation doesnt include a resolve conflict function so this whole thing might be completely redundant
            # else:
            #     lock.release()
            #     self.resolve_conflict()
        #     print("validator")
        # else:
        #     print("not validator")
        #     # self.resolve_conflict()

    # [THREAD] initialize a new_block
    def create_new_block(self, valid_trans):
        if len(self.valid_chain.block_list) == 0:
            idx = 0
            prevHash = 1
        else:
            prevBlock = self.valid_chain.block_list[-1]
            idx = prevBlock.index + 1
            prevHash = prevBlock.hash
        newBlock = block.Block(index=idx, previousHash=prevHash)
        newBlock.listOfTransactions = valid_trans
        newBlock.hash = newBlock.myHash()
        return newBlock

    # [THREAD]
    def mine_block(self, block):
        list_of_validators = self.wallet.wallets
        temp_sum = 0
        # αθροίζει το συνολικό ποσό που δώσανε όλοι οι ενδιαφερόμενοι για το validation (σύνολο χρημάτων λοταρίας)
        for key, value in list_of_validators.items():
            temp_sum = temp_sum + value["stake"]
            # print(temp_sum)

        # με το seed εξασφαλίζουμε ότι όλα τα vms θα βρούν το ίδιο αποτέλεσμα στη λοτταρία (το seed είναι οποιοδήποτε νούμερο)
        random.seed(44)
        # print("after 44")
        # ο "λαχνός" που νίκησε τη λοτταρία
        winning_lot = random.randrange(temp_sum)
        # το αμέσως προηγούμενο άνω φράγμα του προηγούμενου συμμετέχοντα στη λοτταρία
        previous_bound = 0
        lucky_winner = -1
        for key, value in list_of_validators.items():
            # αυξάνει το άνω φράγμα προσθέτοντας στο προηγούμενο το άνω φράγμα του επόμενου validator.
            # έτσι ελέγχουμε αν ο λαχνός που επιλέχθηκε είναι ένας από τους λαχνούς του τρέχοντος validator.
            previous_bound += value["stake"]
            # print("Winning lot = " + str(winning_lot))
            # print("Previous bound = " + str(previous_bound))
            if winning_lot < previous_bound:  # γίνεται ο έλεγχος
                lucky_winner = key
                # print("VALIDATOR KEY:" + lucky_winner)
                break
        if (lucky_winner == -1):
            return False  # block did not get validated
        else:
            block.block_validator(lucky_winner)
            return True  # block did get validated

    # [THREAD]
    def validate_block(self, block):
        print("into the validate block!!")
        temp1 = (block.previousHash == self.valid_chain.block_list[-1].hash)
        temp2 = (block.hash == block.myHash())
        print("1: " + str(temp1))
        print("2: " + str(temp2))
        print(block.hash)
        print(block.myHash())
        return temp1 and temp2

    # [THREAD] create block and call mine
    def init_mining(self, valid_trans, current_wallets):

        global trans_time_end, block_time

        newBlock = self.create_new_block(valid_trans)
        tmp_wallets = copy.deepcopy(self.wallet.wallet_snapshot)

        # temp = self.block_REDO(newBlock, tmp_wallets)
        # print(temp)
        # if not temp:
        #     # print("Stopping mining, block already added")
        #     return

        self.mine_block(newBlock)

        if newBlock.return_validator() == self.wallet.public_key:  # if node is the validator
            if self.validate_block(newBlock):
                self.valid_chain.add_block(newBlock)
                trans_time_end = time.gmtime(time.time())
                self.remove_from_old_valid(valid_trans)
                self.wallet.wallet_snapshot = tmp_wallets
                self.wallet.wallets[newBlock.return_validator()]["usable_amount"] += self.validator_money
                self.validator_money = 0
                block_time += time.thread_time()
                self.broadcast_block(newBlock)
                print("validator")
            else:
                print("not validator")

    # redo all the transactions in a block
    # TODO: do we even use that ?
    def block_REDO(self, block, wallets):
        for trans in block.listOfTransactions:
            if (self.validate_transaction(wallets, trans) != 'validated'):
                print("Failed Transaction: ")
                print('\t\tsender id: ' + str(trans.senderID) + ' \t\treceiver id: ' + str(
                    trans.receiverID) + ' \t\ttype_of_transaction: ' + str(trans.type_of_transaction)
                      + ' \t\tamount: ' + str(trans.amount) + ' \t\tmessage: ' + str(trans.message))
                return False
        return True

    # validate chain's hashes
    def chain_hashes_validation(self, chain):
        prev_hash = chain[0].hash

        for b in chain[1:]:
            if (b.previousHash != prev_hash or b.hash != b.myHash()):
                return False
            prev_hash = b.hash
        return True

    # validates and returns list of block objects
    def validate_chain(self, blocklist):
        # print("__________I CAN STILL HEAR YOU SAYING__________")

        chain = []
        # initialize pending and unreceived transactions
        pending = copy.deepcopy(self.pending_trans)  # we will use these lists just for validation and
        valid = copy.deepcopy(self.valid_trans)
        pending += valid
        unreceived = copy.deepcopy(self.unreceived_trans)  # then we will add them to node's lists
        tmp_wallets = {}

        btstrp_public_k = self.ring[0]['public_key']
        amount = (len(self.ring.keys()) - 1) * 1030 + 1000  # number of nodes * 100 BCCs
        tmp_wallets = {btstrp_public_k: {"stake": 10, "usable_amount": amount, "nonce": 0}}

        self.add_block_list_to_chain(chain, blocklist)

        if not self.chain_hashes_validation(chain):
            print("CHAIN HAS INVALID HASHES")
            return False

        cnt = 1  # to keep iterating over new chain
        # i is our old block, j the block from new blockchain
        for i, j in zip(self.valid_chain.block_list[1:], chain[1:]):

            old_trans = i.listOfTransactions
            new_trans = j.listOfTransactions
            A = [t for t in old_trans if t not in new_trans]
            B = [t for t in new_trans if t not in old_trans]
            # if pending transactions in new block, remove them, and add pending from i
            tmp_pending = [t for t in pending if t not in B] + [t for t in A if t not in unreceived]
            # if unreceived transactions in i, remove them, and add unreceived from j
            tmp_unreceived = [t for t in unreceived if t not in A] + [t for t in B if t not in pending]

            # REDO block and check its validity
            if not self.block_REDO(j, tmp_wallets):
                # print("Chain invalid!")
                return False, None, None

            pending = tmp_pending
            unreceived = tmp_unreceived
            cnt += 1

        # continue validating chain
        for j in chain[cnt:]:

            new_trans = j.listOfTransactions
            tmp_pending = [t for t in pending if t not in new_trans]
            tmp_unreceived = unreceived + [t for t in new_trans if t not in pending]

            if not self.block_REDO(j, tmp_wallets):
                # print("___Rest of Chain invalid!")
                return False, None, None

            print("ok")
            pending = tmp_pending
            unreceived = tmp_unreceived

        # validation successfull
        self.pending_trans = copy.deepcopy(pending)
        self.unreceived_trans = copy.deepcopy(unreceived)
        self.old_valid = []
        self.valid_trans = []

        return True, chain, tmp_wallets

