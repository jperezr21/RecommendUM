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
    the_file = open('C:\ml-1m\\ratings.dat', 'rb')

    with the_file as f:
        reader = csv.reader((line.replace('::', ':') for line in f), delimiter=':')
        try:
            for row in reader:
                x.execute("""INSERT INTO ratings (usuario_id,pelicula_id,rating,fecha_hora)
                          VALUES (%s,%s,%s,FROM_UNIXTIME(%s))""",
                          (int(row[0]), int(row[1]), int(row[2]), int(row[3])))
            db.commit()
            print "OK"
        except MySQLdb.Error as err:
            db.rollback()
            print err

        db.close()
