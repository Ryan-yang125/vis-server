import pymongo
from bson.json_util import loads, dumps
import json
import numpy as np
from sklearn.cluster import AgglomerativeClustering


def find_phases(client, match_id):
    db = client.soccer
    phase_info = db.phases

    phases = phase_info.find(
        {'matchId': int(match_id)}, {'_id': 0})
    # filter
    filtered_phases = []
    for phase in phases:
        if phase['phaseLength'] >= 3:
            filtered_phases.append(phase)

    return filtered_phases


def get_sequence_info(phase):

    event_sequence = phase['eventSequence']
    positions = []
    for event in event_sequence:
        current_positions = event['positions']
        if len(positions) == 0:
            positions.append(current_positions[0])
            if len(current_positions) > 1:
                positions.append(current_positions[1])
        else:
            if len(current_positions) > 1:
                positions.append(current_positions[1])

    return positions


def event_distance(position_1, position_2):
    distance = np.sqrt((position_1['x'] - position_2['x']) **
                       2 + (position_1['y'] - position_2['y']) ** 2)

    return distance


def phase_distance(phase_1, phase_2):
    # [] of all event postion[]
    positions_1 = get_sequence_info(phase_1)
    positions_2 = get_sequence_info(phase_2)

    len_1 = len(positions_1)
    len_2 = len(positions_2)

    # DTW algorithm
    D = np.zeros((len_1, len_2))
    for i in range(len_1):
        for j in range(len_2):
            temp_min = 0

            if i == 0:
                if j == 0:
                    temp_min = 0
                else:
                    temp_min = D[i, j - 1]
            else:
                if j == 0:
                    temp_min = D[i - 1, j]
                else:
                    temp_min = min(D[i - 1, j - 1], D[i, j - 1], D[i - 1, j])

            D[i, j] = event_distance(positions_1[i], positions_2[j]) + temp_min

    return D[len_1 - 1, len_2 - 1]


def clustering_phases(phases, cluster_number):

    # new distance mat
    phases_count = len(phases)
    distance_matrix = np.zeros((phases_count, phases_count))

    # computer distance between phases by DTW
    for i in range(phases_count):
        for j in range(phases_count):
            if j < i:
                current_distance = phase_distance(phases[i], phases[j])
                distance_matrix[i, j] = current_distance
                distance_matrix[j, i] = current_distance

    clustering = AgglomerativeClustering(
        n_clusters=cluster_number, affinity='precomputed', linkage='complete')
    clustering_result = clustering.fit(distance_matrix)
    labels = clustering_result.labels_

    clustered_phases = []
    for _ in range(cluster_number):
        clustered_phases.append([])
    for i in range(phases_count):
        clustered_phases[labels[i]].append(phases[i])
    return clustered_phases


def get_shots_of_cluseter(cluster):
    cluster_shot_cnt = 0
    for phase in cluster:
        event_sequence = phase['eventSequence']
        event_shot_cnt = 0
        for event in event_sequence:
            if event['eventName'] == 'Shot':
                event_shot_cnt += 1
        cluster_shot_cnt += event_shot_cnt
    return cluster_shot_cnt


def rank_clusters_shots(clusteres):
    clustered_result = []
    for cluster in clusteres:
        clustered_result.append(
            {"phases": cluster, "shots": get_shots_of_cluseter(cluster), "length": len(cluster)})
    clustered_result.sort(reverse=True, key=lambda item: item['shots'])
    return dumps(clustered_result)
