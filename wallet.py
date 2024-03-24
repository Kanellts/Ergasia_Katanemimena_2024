from Crypto.PublicKey import RSA


class Wallet:

    def __init__(self, utxos={}):
        #set
        rsa_key = RSA.generate(1024)
        self.private_key = rsa_key.exportKey('PEM').decode()
        self.public_key = rsa_key.publickey().exportKey('PEM').decode()
        self.utxos = utxos  # key : public key, value: {id, to_who, amount}
        self.utxos_snapshot = {}  # we will use it to validate any received block

    def balance(self):
        temp = self.public_key
        balance_sum = 0
        for i in self.utxos[temp]:
            balance_sum = balance_sum + i['amount']
        return balance_sum
