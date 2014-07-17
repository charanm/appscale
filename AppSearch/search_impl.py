#!/usr/bin/env python

""" 
A service to implement the Search API methods. It uses Solr.
"""

import datetime
import hashlib
import json
import logging
import os
import sys
import time
 

sys.path.append(os.path.join(os.path.dirname(__file__), "../lib"))
import appscale_info
import constants
import file_io
import monit_app_configuration
import monit_interface

sys.path.append(os.path.join(os.path.dirname(__file__), "../AppServer"))
from google.appengine.runtime import apiproxy_errors
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_errors
from google.appengine.api import datastore_distributed
from google.appengine.api import datastore
from google.appengine.ext import db

from google.appengine.api.search import search_service_pb


class TaskName(db.Model):
  """ A datastore model for tracking task names in order to prevent
  tasks with the same name from being enqueued repeatedly.
  
  Attributes:
    timestamp: The time the task was enqueued.
  """
  STORED_KIND_NAME = "__task_name__"
  timestamp = db.DateTimeProperty(auto_now_add=True)
  queue = db.StringProperty(required=True)
  state = db.StringProperty(required=True)
  endtime = db.DateTimeProperty()
  app_id = db.StringProperty(required=True)

  @classmethod
  def kind(cls):
    """ Kind name override. """
    return cls.STORED_KIND_NAME

def setup_env():
  """ Sets required environment variables for GAE datastore library """
  os.environ['AUTH_DOMAIN'] = "appscale.com"
  os.environ['USER_EMAIL'] = ""
  os.environ['USER_NICKNAME'] = ""
  os.environ['APPLICATION_ID'] = ""

class Search():
  """ AppScale search layer for the Search API. """

  def __init__(self):
    """ Search Constructor. """

  def __parse_json_and_validate_tags(self, json_request, tags):
    """ Parses JSON and validates that it contains the 
        proper tags.

    Args: 
      json_request: A JSON string.
      tags: The tags to validate if they are in the json.
    Returns:
      A dictionary dumped from the JSON string.
    """
    try:
      json_response = json.loads(json_request)
    except ValueError:
      json_response = {"error": True, 
                       "reason": "Badly formed JSON"}
      return json_response

    for tag in tags:
      if tag  not in json_response:
        json_response = {'error': True, 
                         'reason': 'Missing ' + tag + ' tag'}
        break
    return json_response

  def index_document(self, app_id, http_data):
    """ """

  def delete_document(self, app_id, http_data):
    """ """

  def list_indexes(self, app_id, http_data):
    """ """

  def list_documents(self, app_id, http_data):
    """ """

  def search(self, app_id, http_data):
    """ """

  def fetch_queue_stats(self, app_id, http_data):
    """ Gets statistics about tasks in queues.

    Args:
      app_id: The application ID.
      http_data: The payload containing the protocol buffer request.
    Returns:
      A tuple of a encoded response, error code, and error detail.
    """
    request = taskqueue_service_pb.\
      TaskQueueFetchQueueStatsRequest(http_data)
    response = taskqueue_service_pb.\
      TaskQueueFetchQueueStatsResponse()
    for queue in request.queue_name_list():
      stats_response = response.add_queuestats()
      count = TaskName.all().filter("state =", TASK_STATES.QUEUED).\
        filter("queue =", queue).filter("app_id =", app_id).count()
      stats_response.set_num_tasks(count)
      stats_response.set_oldest_eta_usec(-1)
    return (response.Encode(), 0, "")
