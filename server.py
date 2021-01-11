'''
Author: Yang Rui
Date: 2021-01-11 01:43:31
LastEditTime: 2021-01-12 00:31:56
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
    print(matchId)
    phases = find_phases(client, matchId)
    print(phases)
    clustered_phases = clustering_phases(phases, 10)
    ranked_clusters = rank_clusters(clustered_phases)
    return ranked_clusters


if __name__ == '__main__':
    app.run(port=5500, debug=True)
