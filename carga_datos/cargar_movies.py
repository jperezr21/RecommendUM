#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb
import csv


if __name__ == '__main__':
    # CONEXION A LA DB
    db = MySQLdb.connect(host='192.168.1.107', port=3306, user='prueba',
                         passwd='prueba', db='laboratorio3',
                         unix_socket='/opt/bitnami/mysql/tmp/mysql.sock')
    x = db.cursor()

    # PATH AL ARCHIVO
    the_file = open('C:\ml-1m\movies.dat', 'rb')

    with the_file as f:
        # REEMPLAZAR :: POR ; EN EL ARCHIVO movies.dat!!!!!!!!!!
        reader = csv.reader(f, delimiter=';')
        try:
            for row in reader:
                nombre = row[1][:-7]
                anio = row[1][-5:-1]
                x.execute("""INSERT INTO peliculas (id,nombre,anio) VALUES (%s,%s,%s)""",
                          (int(row[0]), nombre, anio))
                generos = row[2].split('|')
                for genero in generos:
                    if genero == 'Action':
                        genero_id = 1
                    elif genero == 'Adventure':
                        genero_id = 2
                    elif genero == 'Animation':
                        genero_id = 3
                    elif genero == 'Children\'s':
                        genero_id = 4
                    elif genero == 'Comedy':
                        genero_id = 5
                    elif genero == 'Crime':
                        genero_id = 6
                    elif genero == 'Documentary':
                        genero_id = 7
                    elif genero == 'Drama':
                        genero_id = 8
                    elif genero == 'Fantasy':
                        genero_id = 9
                    elif genero == 'Film-Noir':
                        genero_id = 10
                    elif genero == 'Horror':
                        genero_id = 11
                    elif genero == 'Musical':
                        genero_id = 12
                    elif genero == 'Mystery':
                        genero_id = 13
                    elif genero == 'Romance':
                        genero_id = 14
                    elif genero == 'Sci-Fi':
                        genero_id = 15
                    elif genero == 'Thriller':
                        genero_id = 16
                    elif genero == 'War':
                        genero_id = 17
                    elif genero == 'Western':
                        genero_id = 18
                    else:
                        print(genero)
                        raise Exception('No existe el género')
                    x.execute("""INSERT INTO peliculas_generos (pelicula_id,genero_id) VALUES (%s,%s)""",
                              (int(row[0]), genero_id))
            db.commit()
            print "OK"
        except MySQLdb.Error as err:
            db.rollback()
            print err

        db.close()