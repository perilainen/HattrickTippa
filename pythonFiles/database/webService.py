# -*- coding: utf-8 -*-

from flask import request
from flask import Flask
import json
import sqlite3
from flask import Response, jsonify
import databasesetting
app = Flask(__name__)
from datetime import date
import datetime
import time
import re



from flask import make_response, request, current_app, jsonify
from datetime import timedelta
from functools import update_wrapper

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()



def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

@app.route('/matches', methods=['GET'])
@crossdomain(origin='*')
def getMatches():
    conn = sqlite3.connect(databasesetting.db_path)
    sql_command = "SELECT * from matches"
    response = conn.execute(sql_command)
    test = {'matches': [i for i in response.fetchall()]}

    resp = Response(json.dumps(test), status=200,mimetype='application/json')
    return resp


users = {
    "john": "hello",
    "susan": "bye"
}

@auth.get_password
def get_pw(username):


    print username
    conn = sqlite3.connect(databasesetting.db_path)
    sql_command ="SELECT user from users WHERE user=?"
    params = ([username])
    resp = conn.execute(sql_command,params)
    if len(resp.fetchall())>0:
        print "hej på dig"
        sql_command = "SELECT password from users WHERE user=?"
        params = ([username])
        resp = conn.execute(sql_command,params)
        data  = resp.fetchall()
        print data
        return data[0][0]


    #if username in users:

    #    return users.get(username)
    return None

@app.route('/login',methods = ['POST', 'OPTION'])
@crossdomain(origin='127.0.0.1')
@auth.login_required
def index():
    return "Hello, %s!" % auth.username()



@app.route('/table', methods = ['GET'])
@crossdomain(origin='*',headers='authorization')
#@auth.login_required
def getTable():
    matches = getMatches()
    matchesjson =  json.loads(matches.data)['matches']
    users  = json.loads(getUsers().data)['users']
    userdict = {}
    for i in range(len(users)):
        userdict[users[i][0]] =0
    for match in matchesjson:
        result =(json.loads((getResult(match[0]).data))['result'])[0][0]
        if (result !=None):
            for i in range(len(users)):
                bet = getBet(users[i][0],match[0])

                betData =  json.loads(bet.data)['bet']
                if not (betData[0][0]==None):
                    print betData[0][0]
                    userdict[users[i][0]] +=getPoints(betData[0][0],result)
                    print result
    table = []
    for i in userdict:
        j={}
        print i
        print userdict[i]
        table.append({'user':i,'points':userdict[i]})
    resp = jsonify(table=table)
    return resp

def getPlayedMatches(date):
    sql_command = '''SELECT * FROM matches WHERE matchDate < ?'''
    params = ([date])
    conn = sqlite3.connect(databasesetting.db_path)
    resp = conn.execute(sql_command,params)
    return resp.fetchall()


@app.route('/officialBets',methods = ['GET'])
@crossdomain(origin='*')
def getOfficialBets():
    testdate =  datetime.datetime.now()#"2017-01-01 01:00:00"
    matches =  getPlayedMatches(testdate)
    users  = json.loads(getUsers().data)['users']
    bets = []

    for match in matches:
        print match
        jsonitem = {"MatchId": match[0]}
        jsonitem['HomeTeam'] = match[1]
        jsonitem['AwayTeam'] = match[2]
        jsonitem['date'] = match[3]
        jsonitem['result'] = match[4]
        jsonitem['omgång'] = match[5]


        bets.append(jsonitem)
        list = []
        for i in range(len(users)):
            user =  users[i][0]
            bet =  json.loads(getBet(user,match[0]).data)['bet'][0][0]
            listbet = {"user":user}
            listbet["bet"] = bet
            print(match[0])
            print bet
            print match
            listbet["point"] = getPoints(bet,(match[4]))
            list.append(listbet)
        jsonitem['users'] = list

    resp = Response(json.dumps(bets), status=200,mimetype='application/json')
    return resp

def validateresult(stringResult):
    pattern = re.compile('^[0-9]+\-[0-9]+$')
    print "test"
    return re.match('^[0-9]+\-[0-9]+$',stringResult)


def getPoints(bet,result):
    print "Bet: "+str((bet))
    print "Result: "+str(type(result))
    if validateresult(str(bet)) and validateresult(str(result)):

        if bet == result:
            return 3
        signplace = str(bet).find("-")
        homegoalBet = str(bet)[0:signplace]
        awaygoalBet = str(bet)[signplace+1:]
        print "homegoal: "+ homegoalBet
        betDiff =  int(homegoalBet)-int(awaygoalBet)

        signplaceresult = str(result).find("-")
        homegoalResult = str(result)[0:signplaceresult]
        awaygoalResult = str(result)[signplaceresult+1:]

        resultDiff = int(homegoalResult)-int(awaygoalResult)

        if((resultDiff==0==betDiff) or ((resultDiff>0) and (betDiff>0)) or ((resultDiff<0) and (betDiff<0))):
            return 1

    return 0

def getBet(user,matchID):
    conn = sqlite3.connect(databasesetting.db_path)
    sql_command = '''SELECT result from results WHERE user=? AND matchID=?'''
    params = ([user,matchID])
    print params
    response = conn.execute(sql_command,params)

    return jsonify(bet=response.fetchall())


@app.route('/result/<string:matchID>', methods=['GET'])
def getResult(matchID):
    conn = sqlite3.connect(databasesetting.db_path)
    sql_command = '''SELECT result from matches WHERE matchID=?'''
    #print matchID
    params =([matchID])

    response = conn.execute(sql_command,params)
    resp = jsonify(result= response.fetchall())
    conn.close
    return resp

@app.route('/result/<string:matchID>/<string:result>',methods=['PUT'])
def putResult(matchID,result):
    conn = sqlite3.connect(databasesetting.db_path)
    sql_command = '''UPDATE matches SET result =? WHERE matchID=?'''
    params = ([result, matchID])
    print params
    response  = conn.execute(sql_command,params)
    conn.commit()
    conn.close()
    return Response(status=200)

@app.route('/getBets/<string:user>/<string:password>', methods=['GET'])
def getBets(user,password):
    if (not verifyPassword(user,password)):
        return Response("not allowed",status=401)
    conn = sqlite3.connect(databasesetting.db_path)
    sql_command = '''SELECT matchID, result from results WHERE user=?'''
    params = ([user])
    response = conn.execute(sql_command,params)

    results  = response.fetchall()
    print results
    resp = Response(json.dumps(results),status=200,mimetype='application/json')
    return resp


def getUsers():
    conn = sqlite3.connect(databasesetting.db_path)
    sql_command = '''SELECT user from users'''

    response = conn.execute(sql_command)

    return jsonify(users=response.fetchall())

@app.route('/createUser/<string:user>/<string:password>',methods=['POST'])
def createUser(user,password):
    conn = sqlite3.connect(databasesetting.db_path)
    sql_command = '''SELECT * FROM users WHERE user=?'''
    params = ([user])

    response = conn.execute(sql_command,params)

    if len(response.fetchall())>0:
        conn.close()
        resp = Response("user already exists",status=409)
        return resp
    conn.close()
    saveUser(user,password)
    resp = Response("user created", status=200)
    return resp
@app.route('/user/<string:user>', methods =['DELETE'])
def deleteUser(user):
    conn = sqlite3.connect(databasesetting.db_path)
    sql_command = '''DELETE FROM users WHERE user = ?'''
    params = ([user])
    conn.execute(sql_command,params)
    conn.commit()
    conn.close()

def saveUser(user,password):
    conn = sqlite3.connect(databasesetting.db_path)
    sql_command = '''INSERT INTO users (user,password) VALUES(?,?)'''
    params = ([user, password])
    curs = conn.cursor()

    curs.execute(sql_command,params)

    sql_command = '''SELECT matchID from matches'''

    resp = conn.execute(sql_command)
    allMatches = resp.fetchall()

    for match in allMatches:
        currmatch = match[0]
        sql_command = '''INSERT INTO results (user,matchID,result) VALUES (?,?,NULL)'''
        params = ([user,currmatch])
        curs.execute(sql_command,params)
    conn.commit()
    conn.close()


def verifyPassword(user,password):
    conn =sqlite3.connect(databasesetting.db_path)
    sql_command = '''SELECT password FROM users WHERE user=? AND password=?'''
    params = ([user, password])
    resp = conn.execute(sql_command,params)

    #print resp.fetchone()
    if resp.fetchall()==[]:
        conn.close()
        return False
    conn.close()
    return True

@app.route('/placeBet/<string:user>/<string:password>/<string:matchID>/<string:result>',methods=['PUT'])
def placeBet(user,password,matchID,result):
    if (not verifyPassword(user,password)):
        return Response("not allowed",status=401)
    sql_command = '''UPDATE results SET result =? WHERE matchID=? AND user=?'''

    conn = sqlite3.connect(databasesetting.db_path)
    params = ([result,matchID,user])
    resp = conn.execute(sql_command,params)
    print resp.fetchall()
    conn.commit()
    conn.close()
    return Response("bet placed",status=200)





if __name__=='__main__':
    app.run(debug=True)