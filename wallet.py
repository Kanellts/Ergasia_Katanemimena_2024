from Crypto.PublicKey import RSA


class Wallet:

    # constructor function
    def __init__(self, wallets={}):
        rsa_key = RSA.generate(1024)
        self.private_key = rsa_key.exportKey('PEM').decode()
        self.public_key = rsa_key.publickey().exportKey('PEM').decode()
        self.wallets = wallets  # key : public key, value: {stake, usable_amount}
        self.wallet_snapshot = {}  # here we store how the wallets were when the last block was added to the blockchain

    # return this wallet's balance
    def balance(self):
        temp = self.public_key
        balance_sum = 0
        for i in self.wallets[temp]:
            balance_sum = balance_sum + i['usable_amount']
        return balance_sum

    # changes the stake of a node
    def stake(self, stake):
        temp = self.wallets[self.public_key]
        if temp['usable_amount]'] < stake:
            return -1
        else:
            temp_sum = temp['usable_amount'] + temp['stake']
            temp['stake'] = stake
            temp['usable_amount'] = temp_sum - stake

    def return_stake_amount(self):
        temp = self.wallets[self.public_key]
        return temp['stake']

    def return_publickey(self):
        return self.public_key
