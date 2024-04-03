from Crypto.PublicKey import RSA


class Wallet:

    # constructor function
    def __init__(self, wallets={}):
        rsa_key = RSA.generate(1024)
        self.private_key = rsa_key.exportKey('PEM').decode()
        self.public_key = rsa_key.publickey().exportKey('PEM').decode()
        self.wallets = wallets  # key : public key, value: {stake, usable_amount}

    # return this wallet's balance
    def balance(self):
        temp = self.public_key
        balance_sum = 0
        for i in self.wallets[temp]:
            balance_sum = balance_sum + i['usable_amount']
        return balance_sum
