var express = require('express')
var mysql = require('mysql')
var bodyParser = require('body-parser').urlencoded({extended: true});
var moment = require('moment')
var dbInfo = require('./dbInfo.json');
var pool = mysql.createPool({
    connectionLimit : 100,
    host : dbInfo.host,
    user : dbInfo.user,
    port : dbInfo.port,
    password : dbInfo.password,
    database : dbInfo.database
})


// 모듈 별로 파일 나누기
// mysql 정보 공개 말기


var app = express();
app.set('port', process.env.PORT || 3000)
app.use(bodyParser);



/** 감정 삽입 : POST /insertemotion   (위도, 경도, 감정 번호)
*/
app.post('/insertemotion', function(req, res, next) {
    pool.getConnection(function(err, connection) {
        userid = req.body.userid
        lat = parseFloat(req.body.lat)
        lon = parseFloat(req.body.lon)
        emotion = req.body.emotion
        var query = 'INSERT INTO emotion (userid, lat, lon, emotion) VALUES (' + userid + ','+ lat + ',' + lon + ',' + emotion + ')';
        connection.query(query, function(err, result) {
            if(err) res.send(err);
            connection.release();
            res.send(result);
        })
    })
})


/** 최근에 표현된 전세계의 모든 감정 불러오기 : GET /loaddata
*/
// app.get('/loadData', function(req, res, next) {
//     console.log("loadData");
//     pool.getConnection(function(err, connection) {
//         connection.query('SELECT lat, lon, emotion FROM emotion', function(err, rows) {
//             connection.release();
//             res.json(rows);
//         })
//     })
// })


/** 현재 보고 있는 지역에서 최근 2시간 이내에 표현된 감정 불러오기 : GET /loaddata?startlat={시작 위도}&endlat={끝 위도}&startlon={시작 경도}&endlon={끝 경도}
*/
app.get('/loaddata', function(req, res, next) {
    var query = 'SELECT lat, lon, emotion FROM emotion\n';
    // 현재 보고 있는 지역이 날짜 변경선에 걸쳐 있는 경우
    if(req.query.startLon>=0 && req.query.endLon<=0) {
        query += 'WHERE lon NOT BETWEEN ' + req.query.endLon + ' AND ' + req.query.startLon;
    } else {
        query += 'WHERE lon BETWEEN ' + req.query.startLon + ' AND ' + req.query.endLon;
    }
    query += '\nAND\nlat BETWEEN ' + req.query.startLat + ' AND ' + req.query.endLat +
             "\nAND\ntime BETWEEN '" + hoursAgo(2) + "' AND '" + hoursAgo(0) + "'";

    pool.getConnection(function(err, connection) {
        connection.query(query, function(err, rows) {
            connection.release();
            res.json(rows);
        })
    })
})


/* 특정 시간 대에 표현된 감정 불러오기 : GET /loaddata/{시간}
*/
app.get('/loaddata/:time', function(req, res, next) {
    pool.getConnection(function(err, connection) {
        var query = "SELECT time, lat, lon, emotion FROM emotion " +
                    "WHERE time BETWEEN '" + hoursAgo(+req.params.time+2) + "' AND '" + hoursAgo(req.params.time) + "'"
        connection.query(query, function(err, rows) {
            connection.release();
            res.json(rows);
        })
    })
})


function hoursAgo(hours) {
    var time = moment().subtract(hours,'hours').format('YYYY-MM-DD HH:mm:ss')
    console.log(hours);
    console.log(time);
    return time
}


app.listen(app.get('port'), function(){
    console.log('잇힝 시작이당!');
})
