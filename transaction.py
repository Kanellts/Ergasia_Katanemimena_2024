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
    def __init__(self, sender, senderID, receiver, receiverID, type_of_transaction, amount=0, message = '',
                id=None, nonce, signature=None):
        #TODO: should we calculate the amount if the type is a message type here?
        self.sender = sender  # public key str
        self.receiver = receiver  # public key str
        self.senderID = senderID  # ring IDs int
        self.receiverID = receiverID
        self.type_of_transaction = type_of_transaction  # TODO: what type of variable is this
        self.amount = amount  # int
        self.message = message  # str
        self.id = id  # transaction hash (str)
        self.signature = signature
        self.nonce = nonce # TODO: pws afto diathreitai 'ana apostolea'???

    # 2 transactions are equal when they have the same hash (compare 2 strings)
    # TODO: is this even implemented????
    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return NotImplemented
        return self.id == other.id

    # return transaction to dictionary
    def to_dict(self):
        return OrderedDict([('sender', self.sender), ('receiver', self.receiver),
                            ('message_type', self.message_type), ('message', self.message),
                            ('amount', self.amount),
                            ('type_of_transaction', self.type_of_transaction),
                            ('message', self.message), ('id', self.id),
                            ('signature', self.signature),
                            ('nonce', self.nonce)])
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
