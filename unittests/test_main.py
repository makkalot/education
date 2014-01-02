'''
Created on Dec 1, 2013

@author: Chris
'''
import unittest
import logging
from time import sleep
from google.appengine.api import users
from django.utils import simplejson as json
from google.appengine.api import urlfetch
from google.appengine.api import memcache
from google.appengine.ext import testbed
from google.appengine.ext import db
import webapp2
import uploader

class Test_Quest(unittest.TestCase):

    def setUp(self):
        
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_mail_stub()
        self.testbed.init_blobstore_stub()
        self.testbed.init_taskqueue_stub(root_path="../.") #2.7
        
        self.request = webapp2.Request.blank('')
        self.request.META = {}
        self.request.META['REMOTE_ADDR'] = '1.2.3.4'

    def tearDown(self):
        self.testbed.deactivate()

    def test_index(self):
        self.assertEqual(1,1)
        # Build a request object passing the URI path to be tested.
        # You can also pass headers, query arguments etc.
        request = webapp2.Request.blank('/')
        # Get a response for that request.
        response = request.get_response(uploader.app)

        # Let's check if the response is correct.
        self.assertEqual(response.status_int, 200)
        self.assertEqual(True, "Upload File:" in response.body)
    
    def test_pycrypto(self):
        from Crypto.PublicKey import RSA
        from Crypto import Random
        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)

        self.assertEqual(True, key.can_encrypt())
        self.assertEqual(True, key.can_sign())
        self.assertEqual(True, key.has_private())

        public_key = key.publickey()
        
        for username in ['chris', 'bob', 'mary-joe add']:
            enc_data = public_key.encrypt(username, 32)
            decrypted = key.decrypt(enc_data)
            self.assertEqual(username, decrypted)
          
