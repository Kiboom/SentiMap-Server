#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask import Flask, render_template, request, Response, session, url_for, json, jsonify, make_response
from flaskext.mysql import MySQL
from datetime import datetime, timedelta
from decimal import *

app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root';
app.config['MYSQL_DATABASE_PASSWORD'] = 'db1004'
app.config['MYSQL_DATABASE_DB'] = 'patchwork'
app.config['DEBUG'] = True
#app.secret_key = "08db348a20f4745717a979947e9af630"
app.secret_key = "lqiu4hrw348liuhgeahpq9845iutw9p4e8r7gquigarfusw"

mysql.init_app(app);

@app.route('/')
def checkLogin():
    if 'login' in session and session.get('login') == True:
        return make_response(json.jsonify(email=session.get('email')), 200)
    else:
        return make_response(json.jsonify(message="Not logged in"), 403)


@app.route('/login', methods=["GET"])
def login():
    conn = mysql.connect()
    email = request.args.get('email')

    if email != None:
        session['login'] = True
        session['email'] = email

    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM user WHERE email = %s"%(email))
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute("INSERT INTO user (email) VALUES (%s)"%(email))
        conn.commit()
        return make_response(json.jsonify(message="Logged in", email=email), 200)
    else:
        return make_response(json.jsonify(message="No data from your request"), 403)


@app.route("/logout", methods=["GET"])
def logout():
    session['login'] = None
    session['email'] = None
    return make_response(json.jsonify(message="Logged out"), 200)

@app.route('/main')
def main():
    return 'main page'


@app.route('/insertEmotion', methods=["POST"])
def insertData():
    getcontext().prec = 38
    userid = Decimal(request.form['userid'])
    lat = float(request.form['lat'])
    lon = float(request.form['lon'])
    emotion = request.form['emotion']

    dic = {"userid" : userid, "lat" : lat, "lon" : lon, "emotion" : emotion}
    result = [dic]

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO emotion (userid, lat, lon, emotion) values (%s, %s, %s, %s)"%(userid, lat, lon, emotion))
    conn.commit()

    return "jsonify(results = result)"

@app.route('/loadData', methods=["GET", "POST"])
def loadData():
    cursor = mysql.connect().cursor();
    cursor.execute("select id, userid, lat, lon, emotion from emotion where time between '" + hoursAgo(-2) + "' AND '" + hoursAgo(0)+"'")
    data = cursor.fetchall()
    result = []

    for row in data:
        dic = {
        "id" : row[0],
        "userid" : row[1],
        "lat" : float(row[2]),
        "lon" : float(row[3]),
        "emotion" : row[4]
        }
        result.append(dic)

    print(result)
    return jsonify(results=result)



def hoursAgo(ago):
    return datetime.strftime(datetime.now() + timedelta(hours=ago), '%Y-%m-%d %H:%M:%S');


@app.route('/loadData/<path:requestTime>', methods=["GET"])
def loadDataByTime(requestTime):
    cursor = mysql.connect().cursor();

    if requestTime=='Now':
        print(hoursAgo(-2)+"~"+hoursAgo(0))
        print("select id, userid, time, lat, lon, emotion from emotion where time between '" + hoursAgo(-2) + "' AND '" + hoursAgo(0)+"'")
        cursor.execute("select id, userid, time, lat, lon, emotion from emotion where time between '" + hoursAgo(-2) + "' AND '" + hoursAgo(0)+"'")
    elif requestTime=='12Hours':
        print(hoursAgo(-14)+"~"+hoursAgo(-12))
        print("select id, userid, time, lat, lon, emotion from emotion where time between '" + hoursAgo(-14) + "' AND '" + hoursAgo(-12)+"'")
        cursor.execute("select id, userid, time, lat, lon, emotion from emotion where time between '" + hoursAgo(-14) + "' AND '" + hoursAgo(-12)+"'")
    elif requestTime=='1Day':
        print(hoursAgo(-26)+"~"+hoursAgo(-24))
        print("select id, userid, time, lat, lon, emotion from emotion where time between '" + hoursAgo(-26) + "' AND '" + hoursAgo(-24)+"'")
        cursor.execute("select id, userid, time, lat, lon, emotion from emotion where time between '"+ hoursAgo(-26) + "' AND '" + hoursAgo(-24)+"'")
    elif requestTime=='1Week':
        print(hoursAgo(-170)+"~"+hoursAgo(-168))
        print("select id, userid, time, lat, lon, emotion from emotion where time between '" + hoursAgo(-170) + "' AND '" + hoursAgo(-168)+"'")
        cursor.execute("select id, userid, time, lat, lon, emotion from emotion where time between '"+ hoursAgo(-170) + "' AND '" + hoursAgo(-168)+"'")
    elif requestTime=='1Month':
        print(hoursAgo(-734)+"~"+hoursAgo(-732))
        print("select id, userid, time, lat, lon, emotion from emotion where time between '" + hoursAgo(-734) + "' AND '" + hoursAgo(-732)+"'")
        cursor.execute("select id, userid, time, lat, lon, emotion from emotion where time between '" + hoursAgo(-734) + "' AND '" + hoursAgo(-732)+"'")
    else: pass

    data = cursor.fetchall()
    result = []

    for row in data:
        dic = {
        "id" : row[0],
        "userid" : row[1],
        "time" : row[2].strftime('%Y-%m-%d %H:%M:%S'),
        "lat" : float(row[3]),
        "lon" : float(row[4]),
        "emotion" : row[5]
        }
        result.append(dic)

    print(result)
    return jsonify(results=result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
