'''
Author: Yang Rui
Date: 2021-01-11 01:49:24
LastEditTime: 2021-01-11 19:26:55
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /python-server/data_process.py
'''
# TODO fix european and wordl cup
import json
import os

import pymongo

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.soccer
print(db.list_collection_names())

competition_info = db.competitions
team_info = db.teams
match_info = db.matches

hireac_data = {"name": "root", "children": []}
competitions = competition_info.find()
for competition in competitions:
    c_name = competition['name']
    # print(c_name)
    c_area_id = competition['area']['id']
    c_id = competition['wyId']
    # find all team in this competitions
    # TODO area.id有int和str两种类型
    team_in_this = team_info.find({"area.id": str(c_area_id)}, {
                                  "_id": 0, 'wyId': 1, 'name': 1})
    # print(team_in_this[0]['name'])
    hireac_data['children'].append({"name": c_name, "children": []})
    c_length = len(hireac_data['children'])
    team_data = hireac_data['children'][c_length-1]
    print(team_data)
    # print(team_data)
    for team in team_in_this:
        t_id = team['wyId']
        t_name = team['name']
        print(t_name)
        team_data['children'].append(
            {"name": t_name, "children": []})
        t_length = len(team_data['children'])
        match_data = team_data['children'][t_length-1]
        matches = match_info.find({'competitionId': int(c_id)})
        for match in matches:
            team_ids = list(match['teamsData'].keys())
            print(team_ids)
            if str(t_id) in team_ids:
                match_id = match['wyId']
                t_index = team_ids.index(str(t_id))
                v_team_id = team_ids[t_index ^ 1]
                # 需要转换为int，否则查询不到
                v_team = team_info.find_one({"wyId": int(v_team_id)}, {
                    "_id": 0, 'wyId': 1, 'name': 1})
                match_data['children'].append(
                    {"name": v_team['name'], "wyId": match_id})

with open('match-data.json', 'w') as file:
    json.dump(hireac_data, file)
