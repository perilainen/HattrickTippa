# -*- coding: utf-8 -*-

from flask import request
from flask import Flask
import json
import sqlite3

import databasesetting
app = Flask(__name__)


@app.route('/matches', methods=['GET'])
def getMatches():
    conn = sqlite3.connect(databasesetting.db_path)
    sql_command = "SELECT * from matches"
    response = conn.execute(sql_command)
    test = {'matches': [i for i in response.fetchall()]}
    return json.dumps(test)


@app.route('/result/<string:matchID>', methods=['GET'])
def getResult(matchID):
    conn = sqlite3.connect(databasesetting.db_path)
    sql_command = '''SELECT result from matches WHERE matchID=?'''
    print matchID
    params =([matchID])

    response = conn.execute(sql_command,params)

    return json.dumps(response.fetchall())

@app.route('/result/<string:matchID>/<string:result>',methods=['PUT'])
def putResult(matchID,result):
    conn = sqlite3.connect(databasesetting.db_path)
    sql_command = '''UPDATE matches SET result =? WHERE matchID=?'''
    params = ([result, matchID])
    print params
    response  = conn.execute(sql_command,params)
    conn.commit()
    conn.close()


if __name__=='__main__':
    app.run(debug=True)