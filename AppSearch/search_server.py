#!/usr/local/Python-2.7.3/python

# See LICENSE file
""" 
A tornado web service for handling Search requests from application.
"""
import tornado.httpserver
import tornado.ioloop
import tornado.web

import search_impl

from google.appengine.api.search import search_service_pb

from google.appengine.ext.remote_api import remote_api_pb

# Default port this service runs on.
SERVER_PORT = 53496

class MainHandler(tornado.web.RequestHandler):
  """
  Defines what to do when the webserver receives different 
  types of HTTP requests.
  """
  def unknown_request(self, app_id, http_request_data, pb_type):
    """ Function which handles unknown protocol buffers.
   
    Args:
      app_id: Name of the application.
      http_request_data: The encoded protocol buffer from the AppServer.
    Raise:
      NotImplementedError: This unknown type is not implemented.
    """
    raise NotImplementedError("Unknown request of operation %s" % pb_type)

  @tornado.web.asynchronous
  def post(self):
    """ Function which handles POST requests. Data of the request is 
        the request from the AppServer in an encoded protocol buffer 
        format.
    """
    global search    
    request = self.request
    http_request_data = request.body
    pb_type = request.headers['protocolbuffertype']
    app_data = request.headers['appdata']
    app_data  = app_data.split(':')
    app_id = app_data[0]
 
    if pb_type == "Request":
      self.remote_request(app_id, http_request_data)
    else:
      self.unknown_request(app_id, http_request_data, pb_type)

    self.finish()

  @tornado.web.asynchronous
  def get(self):
    """ Handles get request for the web server. Returns that it is currently
        up in json.
    """
    self.write('{"status":"up"}')
    self.finish()

  def remote_request(self, app_id, http_request_data):
    """ Receives a remote request to which it should give the correct 
        response. The http_request_data holds an encoded protocol buffer
        of a certain type. Each type has a particular response type. 
    
    Args:
      app_id: The application ID that is sending this request.
      http_request_data: Encoded protocol buffer.
    """
    global search    
    apirequest = remote_api_pb.Request()
    apirequest.ParseFromString(http_request_data)
    apiresponse = remote_api_pb.Response()
    response = None
    errcode = 0
    errdetail = ""
    apperror_pb = None
    method = ""
    http_request_data = ""

    if not apirequest.has_method():
      errcode = search_service_pb.SearchServiceError.INVALID_REQUEST
      errdetail = "Method was not set in request"
      apirequest.set_method("NOT_FOUND")
    else:
      method = apirequest.method()

    if not apirequest.has_request():
      errcode = search_service_pb.SearchServiceError.INVALID_REQUEST
      errdetail = "Request missing in call"
      apirequest.set_method("NOT_FOUND")
      apirequest.clear_request()
    else:
      http_request_data = apirequest.request()

    if method == "IndexDocument":
      response, errcode, errdetail = search.index_document(app_id,
                                                 http_request_data)
    elif method == "DeleteDocument":
      response, errcode, errdetail = search.delete_document(app_id,
                                                 http_request_data)
    elif method == "ListIndexes":
      response, errcode, errdetail = search.list_indexes(app_id,
                                                 http_request_data)
    elif method == "ListDocuments":
      response, errcode, errdetail = search.list_documents( app_id,
                                                 http_request_data)
    elif method == "Search":
      response, errcode, errdetail = search.search(app_id,
                                                 http_request_data)
   
    if response:
      apiresponse.set_response(response)

    # If there was an error add it to the response.
    if errcode != 0:
      apperror_pb = apiresponse.mutable_application_error()
      apperror_pb.set_code(errcode)
      apperror_pb.set_detail(errdetail)

    self.write(apiresponse.Encode())

def main():
  """ Main function which initializes and starts the tornado server. """
  global search
  search = search_impl.Search()
  search_application = tornado.web.Application([
    # Takes protocol buffers from the AppServers
    (r"/*", MainHandler)
  ])

  server = tornado.httpserver.HTTPServer(search_application)
  server.listen(SERVER_PORT)

  while 1:
    try:
      print "Starting Search server on port %d" % SERVER_PORT
      tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
      print "Server interrupted by user, terminating..."
      exit(1)

if __name__ == '__main__':
  main()
