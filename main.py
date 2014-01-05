from __future__ import with_statement
import urllib
import logging
import os

import webapp2
import jinja2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import files
from Crypto.PublicKey import RSA
from Crypto import Random


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def list_current_blobs(total=5):
    """
    Gets a list of blobs in system
    """
    gqlQuery = blobstore.BlobInfo.gql("ORDER BY creation DESC")
    blobs = gqlQuery.fetch(total)
    return blobs


class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/form.html')
        self.response.write(template.render())

class UploadHandler(webapp2.RequestHandler):
    def crypt(self, key_str, plaintext):
        key = RSA.importKey(key_str)
        public_key = key.publickey()
        #logging.info("PUBLIC_KEY : " + public_key.exportKey())
        enc_data = public_key.encrypt(plaintext, 32)
        
        # encode the byte data into ASCII data so that it could be printed out in the browser
        return enc_data[0].encode('base64')

    def post(self):
        rows=self.request.POST.get('file').value.split("\n")
        pub_key = self.request.POST.get('pub_key')

        if not pub_key:
            webapp2.abort(400, "Missing Public Key Param")

        #clean it
        pub_key = pub_key.strip()

        file_name = files.blobstore.create(mime_type='text/plain')
        with files.open(file_name, 'a') as f:
            for row in rows:
                items = row.split(",")
                if len(items) > 1:
                    items[1] = self.crypt(pub_key, items[1])
                f.write("%s\n" % (",".join(items)))
        files.finalize(file_name)
        
        blob_key = files.blobstore.get_blob_key(file_name)
        
        blobs = list_current_blobs()
        template = JINJA_ENVIRONMENT.get_template('templates/blobs.html')
        self.response.write(template.render({
            "blobs":blobs,
            "flash":str(blob_key)
        }))

    
class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)


class ListBlobsHandler(webapp2.RequestHandler):
    def get(self):
        blobs = list_current_blobs()
        template = JINJA_ENVIRONMENT.get_template('templates/blobs.html')
        self.response.write(template.render({
            "blobs":blobs,
        }))


app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/upload', UploadHandler),
                               ('/serve/([^/]+)?', ServeHandler),
                               ('/blobs', ListBlobsHandler)],
                              debug=True)


def handle_404(request, response, exception):
    logging.exception(exception)
    response.write('Missing Page')
    response.set_status(404)

def handle_500(request, response, exception):
    logging.exception(exception)
    response.write('A server error occurred!')
    response.set_status(500)

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500
