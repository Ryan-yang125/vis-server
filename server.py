import pymongo
from bson.json_util import loads, dumps
import json
import numpy as np
from sklearn.cluster import AgglomerativeClustering


def position_transformation(position, width, height):

    x = (position['x'] * width) / 100
    y = (position['y'] * height) / 100

    return x, y


def find_phases(client, competition_name, team_name):

    # database
    db = client.soccer

    # query
    competition_info = db.competitions
    competition = competition_info.find_one({'name': competition_name})
    competition_id = competition['wyId']

    team_info = db.teams
    team = team_info.find_one({'name': team_name})
    team_id = team['wyId']

    # find all matches of a team
    match_info = db.matches
    matches = match_info.find({'competitionId': competition_id})
    selected_matches = []
    selected_match_ids = []
    for match in matches:
        team_ids = list(match['teamsData'].keys())
        if str(team_id) in team_ids:
            selected_matches.append(match)
            selected_match_ids.append(match['wyId'])

    # find all phases of all matches in a team
    phase_info = db.phases
    # phases = phase_info.find({'teamId': team_id})

    # # TODO find phases of a selected match [0]
    selected_match_id = selected_match_ids[0]
    phases = phase_info.find({'matchId': selected_match_id, 'teamId': team_id})
    # filter
    filtered_phases = []
    for phase in phases:
        if phase['phaseLength'] >= 3:
            filtered_phases.append(phase)

    print(len(filtered_phases))
    return filtered_phases


def get_sequence_info(phase):

    event_sequence = phase['eventSequence']
    # print(len(event_sequence))
    # get all positions
    positions = []
    for event in event_sequence:
        current_positions = event['positions']
        if len(positions) == 0:
            positions.append(current_positions[0])
            positions.append(current_positions[1])
        else:
            if len(current_positions) > 1:
                positions.append(current_positions[1])

    return positions


def event_distance(position_1, position_2):

    # width = 105
    # height = 68

    # position_1_x, position_1_y = position_transformation(
    #     position_1, width, height)
    # position_2_x, position_2_y = position_transformation(
    #     position_2, width, height)

    # # only consider position
    # distance = np.sqrt((position_1_x - position_2_x) **
    #                    2 + (position_1_y - position_2_y) ** 2)
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


def rank_clusters(clusteres):
    clustered_result = []
    for cluster in clusteres:
        clustered_result.append(
            {"phases": cluster, "shots": get_shots_of_cluseter(cluster), "length": len(cluster)})
    clustered_result.sort(reverse=True, key=lambda item: item['shots'])
    return dumps(clustered_result)


client = pymongo.MongoClient(host='localhost', port=27017)
db = client.soccer

phases = find_phases(client, 'Italian first division', 'Milan')
# phases = find_phases(client, 'World Cup', 'Milan')
clustered_phases = clustering_phases(phases, 10)
ranked_clusters = rank_clusters(clustered_phases)
