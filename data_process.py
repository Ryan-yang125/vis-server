'''
Author: your name
Date: 2021-01-11 01:49:24
LastEditTime: 2021-01-11 02:18:05
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /python-server/data_process.py
'''
import pymongo
import os

client = pymongo.MongoClient(host='localhost', port=27017)
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
