import base64
import json
from collections import OrderedDict

from Crypto.Hash import SHA384
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import enum


class type_of_transaction(enum.Enum):
    message = 'message'
    money = 'money'


class Transaction:

    # constructor function
    def __init__(self, sender, senderID, receiver, receiverID, type_of_transaction, amount=0, message='',
                 id=None, signature=None):
        self.sender = sender  # public key str of the sender
        self.receiver = receiver  # public key str of the receiver
        self.senderID = senderID  # ring IDs int of the sender
        self.receiverID = receiverID  # ring IDs int of the receiver
        self.type_of_transaction = type_of_transaction  # enum of either money or message
        self.amount = amount  # int of the amount if it's a money transaction
        self.message = message  # str of the message if it's a message transaction
        self.id = id  # transaction hash (str)
        self.signature = signature  # transaction signature

    # 2 transactions are equal when they have the same hash (compare 2 strings)
    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return NotImplemented
        return self.id == other.id

    # return transaction to dictionary
    def to_dict(self):
        return OrderedDict([('sender', self.sender), ('receiver', self.receiver),
                            ('amount', self.amount),
                            ('type_of_transaction', self.type_of_transaction),
                            ('message', self.message), ('id', self.id),
                            ('signature', self.signature)])

    # hashing transaction
    def hash(self):
        trans = OrderedDict([('sender', self.sender), ('receiver', self.receiver), ('amount', self.amount),
                             ('message', self.message)])
        temp = json.dumps(trans)
        return SHA384.new(temp.encode())

    # signing transaction
    def sign_transaction(self, sender_private_key):
        hash_obj = self.hash()
        private_key = RSA.importKey(sender_private_key)
        signer = PKCS1_v1_5.new(private_key)
        self.id = hash_obj.hexdigest()
        self.signature = base64.b64encode(signer.sign(hash_obj)).decode()
        return self.signature

    # verifies with a public key from whom the data came that it was indeed signed by their private key
    def verify_signature(self):
        rsa_key = RSA.importKey(self.sender.encode())  # sender public key
        verifier = PKCS1_v1_5.new(rsa_key)
        hash_obj = self.hash()
        return verifier.verify(hash_obj, base64.b64decode(self.signature))  # signature needed to be decoded
