#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import urllib2
import MySQLdb
import cherrypy
import jinja2
import os

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def connect(thread_index):
    # Create a connection and store it in the current thread
    cherrypy.thread_data.db = MySQLdb.connect(host='10.252.254.122', port=3306, user='prueba',
                                              passwd='prueba', db='laboratorio3',
                                              unix_socket='/opt/bitnami/mysql/tmp/mysql.sock')

# Tell CherryPy to call "connect" for each thread, when it starts up
cherrypy.engine.subscribe('start_thread', connect)


class Recommender(object):
    @cherrypy.expose
    def index(self):
        c = cherrypy.thread_data.db.cursor()
        c.execute('select * from info_usuarios')
        res = c.fetchall()
        c.close()
        usuarios = []
        for i in res:
            usuarios.append({'id': i[0],
                             'nombre': unicode(i[1], 'latin-1')})
        template = JINJA_ENVIRONMENT.get_template('views/index.html')
        return template.render(users=usuarios)

    @cherrypy.expose
    def calificar(self, user_id=None):
        if user_id:
            cherrypy.session['usuario_id'] = user_id
            resultado = json.load(urllib2.urlopen(
                "https://api.themoviedb.org/3/search/movie?api_key=150d5e95df95be2e0c68094bc9d6241f&query=toy+story"))
            descripcion = resultado[u'results'][0][u'overview']
            link_imagen = 'https://image.tmdb.org/t/p/w320' + resultado[u'results'][0][u'backdrop_path']
            peliculas = [{'movie_id': 1,
                          'nombre': u'Toy Story',
                          'generos': [u'Animación', u'Comedia'],
                          'desc': descripcion,
                          'link_img': link_imagen}] * 10
            template = JINJA_ENVIRONMENT.get_template('views/calificar.html')
            return template.render(pelis=peliculas)
        else:
            raise cherrypy.HTTPRedirect("/")


class Api(object):
    @cherrypy.expose
    def post_rating(self, movie_id, rating):
        # TODO agregar rating a la DB
        print(movie_id, rating)


if __name__ == '__main__':
    recommender_conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/assets': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './assets'
        }
    }
    api_conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        }
    }

    cherrypy.tree.mount(Recommender(), '/', recommender_conf)
    cherrypy.tree.mount(Api(), '/api', api_conf)

    cherrypy.engine.start()
    cherrypy.engine.block()