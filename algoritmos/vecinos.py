#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import scipy.stats


def average_rating(list):
    average = float(0)
    length_list = len(list)
    for i in range(0, length_list):
        average = average + list[i][1]
    average /= length_list
    return average


def get_standard_deviation(list, average):
    deviation = 0
    length_list = len(list)
    for i in range(0, length_list):
        deviation = deviation + ((average - list[i][1]) * (average - list[i][1]))
    if length_list != 1:
        deviation = (deviation / (length_list - 1))
    return math.sqrt(deviation)


# Asumo que las tuplas de (peli_id,rating) de cada usuario aparecen en orden de peli_id.
# def get_similar_users(list_of_users, user):
# array_of_users_and_correlation_value = []
# average_user = average_rating(user[1])
#     length_user = len(user[1])
#     user_deviation = get_standard_deviation(user[1], average_user)
#
#     for i in range(0, len(list_of_users)):
#         average_new_user = average_rating(list_of_users[i][1])
#         new_user_id = list_of_users[i][0]
#         new_user_deviation = get_standard_deviation(list_of_users[i][1], average_new_user) # Puede ser mejorado.
#         n = 0
#         correlation_value = 0
#
#         for j in range(0, length_user):
#             peli_id_user = user[1][j][0]
#             if n >= len(list_of_users[i][1]):
#                 break
#             peli_id_new_user = list_of_users[i][1][n][0]
#
#             if (peli_id_user > peli_id_new_user) and (n+1<len(list_of_users[i][1])):
#                 n += 1
#             elif (peli_id_user == peli_id_new_user):
#                 rating_user = user[1][j][1]
#                 rating_new_user = list_of_users[i][1][n][1]
#                 substraction_user = rating_user - average_user
#                 substraction_new_user = rating_new_user - average_new_user
#                 correlation_value = correlation_value + (substraction_user * substraction_new_user)
#                 n+=1
#         if (user_deviation * new_user_deviation) != 0:
#             correlation_value = correlation_value / (user_deviation * new_user_deviation)
#         array_of_users_and_correlation_value.append((new_user_id, correlation_value))
#     return array_of_users_and_correlation_value;


def get_similar_users(list_of_users, user):
    user_movie_ids = []
    correlations = []

    for i in range(0, len(user[1])):
        user_movie_ids.append(user[1][i][0])

    dict = {}
    for i in range(0, len(user[1])):
        dict[user[1][i][0]] = user[1][i][1]

    for i in range(0, len(list_of_users)):
        user_ratings = []
        tmp_user = list_of_users[i]
        tmp_user_ratings = []
        for j in tmp_user[1]:
            if j[0] in user_movie_ids:
                tmp_user_ratings.append(j[1])
                user_ratings.append(dict[j[0]])

        if tmp_user_ratings == []:
            correlations.append((list_of_users[i][0], 0))
        else:
            correlation = scipy.stats.pearsonr(user_ratings, tmp_user_ratings)
            correlations.append((list_of_users[i][0], correlation[0]))
    return correlations


def create_user_movie_matrix(list_of_users):
    users = []
    for i in list_of_users:
        users.append(i[0])

    movies = []
    for i in list_of_users:
        for j in i[1]:
            if j[0] not in movies:
                movies.append(j[0])

    matrix = [[0 for j in range(0, len(users))] for i in range(0, len(movies))]
    for j in range(0, len(users)):
        movies_of_user_j = [k[0] for k in list_of_users[j][1]]
        h = 0
        user_j_average_rate = average_rating(list_of_users[j][1])

        for i in range(0, len(movies)):
            if movies[i] in movies_of_user_j:
                matrix[i][j] = list_of_users[j][1][h][1] - user_j_average_rate
                h += 1

    return matrix, users, movies


def user_user_recommender(user, list_of_users):
    user_average_rate = average_rating(user[1])
    user_movie_ids = []
    for p in user[1]:
        user_movie_ids.append(p[0])

    similar_users = get_similar_users(list_of_users, user)
    users_id = []
    for i in similar_users:
        users_id.append(i[0])
    similar_users = sorted(similar_users, key=lambda a: a[1], reverse=True)
    new_list_of_users = []
    n = len(similar_users)

    for p in range(0, n):

        if list_of_users[p][0] in users_id:
            new_list_of_users.append(list_of_users[p])

    (user_movie_matrix, users_id, movies_id) = create_user_movie_matrix(new_list_of_users)
    correlation_sum = 0
    for k in similar_users:
        correlation_sum += k[1]

    recommender_vector = []

    for i in range(0, len(movies_id)):
        x = 0
        for j in range(0, len(users_id)):
            x += similar_users[j][1] * user_movie_matrix[i][j]
        if correlation_sum != 0:
            recommender_vector.append((movies_id[i], user_average_rate + x / correlation_sum))
        else:
            recommender_vector.append((movies_id[i], user_average_rate + x))
    recommender_vector = sorted(recommender_vector, key=lambda a: a[1], reverse=True)
    new_recommender_vector = []

    for p in recommender_vector:
        if p[0] not in user_movie_ids:
            new_recommender_vector.append(p)
    return new_recommender_vector