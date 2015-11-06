#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
import MySQLdb
import csv


if __name__ == '__main__':
    # CONEXION A LA DB
    db = MySQLdb.connect(host='192.168.1.107', port=3306, user='prueba',
                         passwd='prueba', db='laboratorio3',
                         unix_socket='/opt/bitnami/mysql/tmp/mysql.sock')
    x = db.cursor()

    # PATH AL ARCHIVO
    the_file = open('C:\ml-latest-small\\ratings.csv', 'rb')

    with the_file as f:
        reader = csv.reader(f, delimiter=',')
        try:
            i = 1
            for row in reader:
                print i
                # VER SI EXISTE EL USUARIO, SINO AGREGARLO
                x.execute("""SELECT id FROM usuarios WHERE id = %s""" % int(row[0]))
                res_u = x.fetchone()
                if not res_u:
                    x.execute('INSERT INTO usuarios VALUES (%s)' % int(row[0]))

                # VER SI LA PELICULA EXISTE, SINO IGNORAR RATING
                x.execute("""SELECT id FROM peliculas WHERE id = %s""" % int(row[1]))
                res_m = x.fetchone()
                if res_m:
                    x.execute('INSERT INTO ratings (usuario_id,pelicula_id,rating,fecha_hora) \
                              VALUES (%s,%s,%s,FROM_UNIXTIME(%s))',
                              (int(row[0]), int(row[1]), float(row[2]), int(row[3])))
                i += 1
            db.commit()
            print "OK"
        except Exception as err:
            db.rollback()
            traceback.print_exc()

        db.close()
