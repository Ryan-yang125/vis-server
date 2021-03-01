'''
Author: Yang Rui
Date: 2021-01-11 01:43:31
LastEditTime: 2021-01-15 11:28:34
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /python-server/server.py
'''
import pymongo
from flask import Flask, request
from clustering import *
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

client = pymongo.MongoClient(host='localhost', port=27017)


@app.route('/', methods=['GET'])
@cross_origin()
def get_clustered():
    matchId = request.args.get('wyId')
    phases_num = request.args.get('clusters')
    print(phases_num)
    phases = find_phases(client, matchId)
    clustered_phases = clustering_phases(phases, int(phases_num))
    ranked_clusters = rank_clusters_shots(clustered_phases)
    return ranked_clusters


if __name__ == '__main__':
    app.run(port=5050, debug=True)
