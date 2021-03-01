'''
Author: Yang Rui
Date: 2021-01-11 01:49:24
LastEditTime: 2021-01-12 21:38:51
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
            {"name": t_name, "wyId": t_id})

with open('team-data.json', 'w') as file:
    json.dump(hireac_data, file)
