#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cherrypy
import MySQLdb
import jinja2
import os

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def connect(thread_index):
    # Create a connection and store it in the current thread 
    cherrypy.thread_data.db = MySQLdb.connect(host='192.168.1.107', port=3306, user='prueba',
                                              passwd='prueba', db='laboratorio3',
                                              unix_socket='/opt/bitnami/mysql/tmp/mysql.sock')

# Tell CherryPy to call "connect" for each thread, when it starts up 
cherrypy.engine.subscribe('start_thread', connect)


class Root:
    def index(self):
        # Sample page that displays the number of records in "table"
        # Open a cursor, using the DB connection for the current thread
        c = cherrypy.thread_data.db.cursor()
        c.execute('select count(*) from usuarios')
        res = c.fetchone()
        c.close()
        output = jinja2.Template(
            u'<html><body>Hay {{ filas }} películas en la tabla `peliculas`</body></html>').render(filas=res[0])
        return output

    index.exposed = True


cherrypy.quickstart(Root())