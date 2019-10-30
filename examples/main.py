# -*- coding: utf-8 -*-
from gevent.pool import Pool
from gevent.pywsgi import WSGIServer

from examples.server import app

pool = Pool(10) # do not accept more than 10000 connections

http_server = WSGIServer(('', 5001), app, spawn=pool)
http_server.serve_forever()
