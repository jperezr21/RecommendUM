#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math


def average_rating(lista):
    average = float(0)
    length_list = len(lista)
    for i in range(0, length_list):
        average = average + lista[i][1]
    average /= length_list
    return average


def get_standard_deviation(lista, average):
    deviation = 0
    length_list = len(lista)
    for i in range(0, length_list):
        deviation = deviation + ((average - lista[i][1]) * (average - lista[i][1]))
    if length_list != 1:
        deviation = (deviation / (length_list - 1))
    return math.sqrt(deviation)


# Asumo que las tuplas de (peli_id,rating) de cada usuario aparecen en orden de peli_id.
def get_similar_users(list_of_users, user):
    array_of_users_and_correlation_value = []
    average_user = average_rating(user[1])
    length_user = len(user[1])
    user_deviation = get_standard_deviation(user[1], average_user)
    for i in range(0, len(list_of_users)):
        average_new_user = average_rating(list_of_users[i][1])
        new_user_id = list_of_users[i][0]
        new_user_deviation = get_standard_deviation(list_of_users[i][1], average_new_user)  # Puede ser mejorado.
        n = 0
        correlation_value = 0
        for j in range(0, length_user):
            peli_id_user = user[1][j][0]
            peli_id_new_user = list_of_users[i][1][n][0]
            if (peli_id_user > peli_id_new_user) and (n + 1 < len(list_of_users[i][1])):
                n += 1
            elif peli_id_user == peli_id_new_user:
                rating_user = user[1][j][1]
                rating_new_user = list_of_users[i][1][n][1]
                substraction_user = rating_user - average_user
                substraction_new_user = rating_new_user - average_new_user
                correlation_value += substraction_user * substraction_new_user
        if (user_deviation * new_user_deviation) != 0:
            correlation_value /= user_deviation * new_user_deviation
        array_of_users_and_correlation_value.append((new_user_id, correlation_value))
    return array_of_users_and_correlation_value