#!/usr/bin/env python
# -*- coding: utf-8 -*-
from server import app
from gevent.pywsgi import WSGIServer
# app.config['STATIC_FOLDER'] = './client/assets'

http_server = WSGIServer(('', 5003), app)
http_server.serve_forever()
