from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Siganture import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template

class Transaction:

	def __init__(self, sender_address, sender_private_key, recipient_address, value):

		##set



		#seld.sender_address: To public key του wallet απο το οποίο προέρχονται τα χρήματα
		#self.receiver_address: Το public key του wallet το οποίο θα καταήξουν τα χρήματα
		#self.amount: το ποσό που θα μεταφερθεί
		#self.transaction_id: το hash του transaction
		"""
		Αυτά δε χρειάζονται είναι από άσκηση προηγούμενης χρονιάς
		# self.transaction_inputs: λιστα από Transaction Input
		# self.transaction_outputs: λιστα από Transaction Output
		"""
		# selfSiganture

	def to_dict(self):


	def sign_transaction(self):
		"""
		Sign transaction with private key
		"""

