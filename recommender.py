#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import urllib2
import MySQLdb
import cherrypy
import jinja2
import os
from algoritmos.vecinos import get_similar_users

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


def get_info_peli(tmdb_id, movie_id):
    try:
        resultado = json.load(urllib2.urlopen(
            "https://api.themoviedb.org/3/movie/" + str(tmdb_id) +
            "?api_key=150d5e95df95be2e0c68094bc9d6241f&language=es"))
        if resultado[u'overview'] is not None and resultado[u'overview'] != u'':
            descripcion = resultado[u'overview'].encode('latin-1', errors='ignore')
        else:
            new_desc = json.load(urllib2.urlopen(
                "https://api.themoviedb.org/3/movie/" + str(tmdb_id) +
                "?api_key=150d5e95df95be2e0c68094bc9d6241f"))
            if new_desc[u'overview'] is not None:
                descripcion = new_desc[u'overview'].encode('latin-1', errors='ignore')
            else:
                descripcion = ''
        if resultado[u'title'] is not None and resultado[u'title'] != u'':
            titulo = resultado[u'title'].encode('latin-1', errors='ignore')
        else:
            new_title = json.load(urllib2.urlopen(
                "https://api.themoviedb.org/3/movie/" + str(tmdb_id) +
                "?api_key=150d5e95df95be2e0c68094bc9d6241f"))
            if new_title[u'title'] is not None:
                titulo = new_title[u'title'].encode('latin-1', errors='ignore')
            else:
                titulo = ''
        path_imagen = resultado[u'backdrop_path']
        if resultado[u'release_date'] is not None and resultado[u'release_date'] != u'':
            anio = int(resultado[u'release_date'][0:4])
        else:
            anio = None
        return titulo, descripcion, anio, path_imagen, movie_id
    except:
        return None, None, None, None, movie_id


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
            db = cherrypy.thread_data.db
            cursor = db.cursor()
            cursor.execute('SELECT ratings.pelicula_id, peliculas.imdb_id, peliculas.tmdb_id, peliculas.nombre, '
                           'peliculas.descripcion, peliculas.anio, peliculas.backdrop_path, '
                           '((COUNT(*) - 12)/25) / POW(((NOW() - AVG(ratings.fecha_hora))/54423110737), 1.8) '
                           'FROM ratings JOIN peliculas ON ratings.pelicula_id = peliculas.id '
                           'GROUP BY 1 ORDER BY 8 DESC LIMIT 99')
            res = cursor.fetchall()
            peliculas = []
            for i in res:
                pelicula = {'movie_id': int(i[0])}

                # VOY A BUSCAR SI EL USUARIO YA CALIFICO ESTA PELICULA
                cursor.execute('SELECT ratings.rating FROM ratings WHERE ratings.pelicula_id = %s AND '
                               'ratings.usuario_id = %s', (int(i[0]), cherrypy.session['usuario_id']))
                res = cursor.fetchone()
                if res:
                    pelicula['rating'] = res[0]

                """
                # SI NO TENGO DATOS DE TMBD
                if i[3] is None and i[4] is None and i[5] is None and i[6] is None:
                    try:
                        info_peli = get_info_peli(int(i[2]), int(i[0]))
                        print info_peli
                        cursor.execute('UPDATE peliculas SET nombre = %s, descripcion = %s, anio = %s, '
                                       'backdrop_path = %s WHERE id = %s', info_peli)
                        db.commit()
                    except MySQLdb.Error as err:
                        print(err)
                        db.rollback()
                        raise cherrypy.HTTPError(500)
                """

                # TRAIGO LOS GENEROS
                cursor.execute('SELECT descripcion FROM generos JOIN peliculas_generos '
                               'ON generos.id = peliculas_generos.genero_id '
                               'WHERE peliculas_generos.pelicula_id = %s' % i[0])
                res = cursor.fetchall()
                generos = []
                for gen in res:
                    generos.append(unicode(gen[0], 'latin-1'))
                pelicula['generos'] = generos
                cursor.execute('SELECT nombre, descripcion, backdrop_path FROM peliculas '
                               'WHERE id = %s' % int(i[0]))
                res = cursor.fetchone()
                if res[0]:
                    pelicula['nombre'] = unicode(res[0], 'latin-1')
                if res[1]:
                    pelicula['desc'] = unicode(res[1], 'latin-1')
                if res[2]:
                    pelicula['link_img'] = u'https://image.tmdb.org/t/p/w320' + unicode(res[2], 'latin-1')
                peliculas.append(pelicula)
            cursor.close()
            template = JINJA_ENVIRONMENT.get_template('views/calificar.html')
            return template.render(pelis=peliculas)
        else:
            raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def recomendar(self):
        if 'usuario_id' in cherrypy.session:
            usuario = cherrypy.session['usuario_id']
            db = cherrypy.thread_data.db
            cursor = db.cursor()
            cursor.execute('SELECT pelicula_id, rating FROM ratings WHERE usuario_id = %s' % usuario)
            res = cursor.fetchall()
            user = (usuario, list(res))
            cursor.execute('SELECT DISTINCT usuario_id FROM ratings WHERE pelicula_id IN '
                           '(SELECT DISTINCT pelicula_id FROM ratings WHERE usuario_id = %s)' % usuario)
            res = cursor.fetchall()
            usuarios = [(u1[0], []) for u1 in res]
            for u2 in usuarios:
                cursor.execute('SELECT pelicula_id, rating FROM ratings WHERE usuario_id = %s AND pelicula_id IN '
                               '(SELECT DISTINCT pelicula_id FROM ratings WHERE usuario_id = %s)', (u2[0], usuario))
                res = cursor.fetchall()
                for i in res:
                    u2[1].append(i)
            vecinos = get_similar_users(usuarios, user)
            return str(sorted(vecinos, key=lambda x: x[1], reverse=True)[:10])
        else:
            raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def register(self, nombre=None):
        method = cherrypy.request.method.upper()
        if method == 'GET':
            template = JINJA_ENVIRONMENT.get_template('views/register.html')
            return template.render()
        elif method == 'POST':
            db = cherrypy.thread_data.db
            cursor = db.cursor()
            try:
                cursor.execute('INSERT INTO usuarios VALUES (NULL)')
                cursor.execute('SELECT id FROM usuarios ORDER BY id DESC')
                usuario_id = cursor.fetchone()[0]
                cursor.execute('INSERT INTO info_usuarios (usuario_id, nombre) VALUES (%s, %s)',
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
                cursor.execute('SELECT * FROM ratings WHERE usuario_id = %s AND pelicula_id = %s',
                               (user_id, movie_id))
                r = cursor.fetchone()
                if not r:
                    cursor.execute('INSERT INTO ratings (usuario_id, pelicula_id, rating) VALUES (%s, %s, %s)',
                                   (user_id, movie_id, rating))
                    db.commit()
                else:
                    cursor.execute('UPDATE ratings SET rating = %s, fecha_hora = NOW() '
                                   'WHERE usuario_id = %s AND pelicula_id = %s',
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

    cherrypy.config.update({'server.socket_host': '0.0.0.0'})

    cherrypy.engine.start()
    cherrypy.engine.block()