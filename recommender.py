#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import urllib
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
        cursor = cherrypy.thread_data.db.cursor()
        cursor.execute('SELECT * FROM info_usuarios ORDER BY nombre')
        res = cursor.fetchall()
        cursor.close()
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
        if 'usuario_id' in cherrypy.session:
            cursor = cherrypy.thread_data.db.cursor()
            cursor.execute('SELECT ratings.pelicula_id, peliculas.nombre, COUNT(*) FROM ratings '
                           'JOIN peliculas ON ratings.pelicula_id = peliculas.id '
                           'GROUP BY 1 ORDER BY 3 DESC LIMIT 20')
            res = cursor.fetchall()
            peliculas = []
            for i in res:
                pelicula = {'movie_id': int(i[0]), 'nombre': unicode(i[1], 'latin-1')}
                cursor.execute('SELECT descripcion FROM generos JOIN peliculas_generos '
                               'ON generos.id = peliculas_generos.genero_id '
                               'WHERE peliculas_generos.pelicula_id = %s' % i[0])
                res = cursor.fetchall()
                generos = []
                for gen in res:
                    generos.append(unicode(gen[0], 'latin-1'))
                pelicula['generos'] = generos
                nombre_url = urllib.quote_plus(i[1])
                resultado = json.load(urllib2.urlopen(
                    "https://api.themoviedb.org/3/search/movie?api_key=150d5e95df95be2e0c68094bc9d6241f&query="
                    + nombre_url))
                descripcion = resultado[u'results'][0][u'overview']
                link_imagen = 'https://image.tmdb.org/t/p/w320' + resultado[u'results'][0][u'backdrop_path']
                pelicula['desc'] = descripcion
                pelicula['link_img'] = link_imagen
                peliculas.append(pelicula)
            template = JINJA_ENVIRONMENT.get_template('views/calificar.html')
            return template.render(pelis=peliculas)
        else:
            raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def register(self, nombre=None, sexo=None, edad=None, ocupacion=None):
        method = cherrypy.request.method.upper()
        if method == 'GET':
            template = JINJA_ENVIRONMENT.get_template('views/register.html')
            return template.render()
        elif method == 'POST':
            db = cherrypy.thread_data.db
            cursor = db.cursor()
            try:
                cursor.execute("""INSERT INTO usuarios (sexo, edad, ocupacion) VALUES (%s, %s, %s)""",
                               (sexo, edad, ocupacion))
                cursor.execute("""SELECT id FROM usuarios ORDER BY id DESC""")
                usuario_id = cursor.fetchone()[0]
                cursor.execute("""INSERT INTO info_usuarios (usuario_id, nombre) VALUES (%s, %s)""",
                               (usuario_id, nombre))
                db.commit()
            except MySQLdb.Error as err:
                print(err)
                db.rollback()
                raise cherrypy.HTTPError(500)
            cursor.close()
            raise cherrypy.HTTPRedirect("/")
        else:
            raise cherrypy.HTTPError(405)


class Api(object):
    @cherrypy.expose
    def post_rating(self, movie_id, rating):
        if 'usuario_id' in cherrypy.session:
            db = cherrypy.thread_data.db
            cursor = db.cursor()
            user_id = cherrypy.session['usuario_id']
            try:
                cursor.execute("""SELECT * FROM ratings WHERE usuario_id = %s AND pelicula_id = %s""",
                               (user_id, movie_id))
                r = cursor.fetchone()
                if not r:
                    cursor.execute("""INSERT INTO ratings (usuario_id, pelicula_id, rating) VALUES (%s, %s, %s)""",
                                   (user_id, movie_id, rating))
                    db.commit()
                else:
                    cursor.execute("""UPDATE ratings SET rating = %s, fecha_hora = NOW()
                                   WHERE usuario_id = %s AND pelicula_id = %s""",
                                   (rating, user_id, movie_id))
                    db.commit()
            except MySQLdb.Error as err:
                print(err)
                db.rollback()
                raise cherrypy.HTTPError(500)
            cursor.close()
        else:
            raise cherrypy.HTTPError(403)


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