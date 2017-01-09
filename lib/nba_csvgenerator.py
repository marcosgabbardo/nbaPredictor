import pymysql.cursors
import csv


# CSV file generator to upload in amazon machine learning with some statistics to use
# in multiclass, binary or regression analisys

def csvGenerator(league, now, cvs_file):

    connection = pymysql.connect(host='192.168.99.100',
                             user='root',
                             password='stalinmaki',
                             db='sportbet',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    print "Generating Statistic CSV file..."
    c_game_stat = connection.cursor()

    sql = "SELECT game.id,home.name homename,away.name awayname, "
    sql = sql + " (home_stat.orb_avg1 - away_stat.orb_avg1) a_orb_avg1, "
    sql = sql + " (home_stat.ortg_avg1 - away_stat.ortg_avg1) a_ortg_avg1, "
    sql = sql + " (home_stat.orb_avg3 - away_stat.orb_avg3) a_orb_avg3, "
    sql = sql + " (home_stat.ortg_avg3 - away_stat.ortg_avg3) a_ortg_avg3, "
    sql = sql + " (home_stat.orb_avg5 - away_stat.orb_avg5) a_orb_avg5, "
    sql = sql + " (home_stat.ortg_avg5 - away_stat.ortg_avg5) a_ortg_avg5, "
    sql = sql + " case when home_point > away_point then home.name "
    sql = sql + " when home_point < away_point then away.name end decisor "
    sql = sql + " FROM nba_game game, nba_team home, nba_team away, nba_team_history home_stat, nba_team_history away_stat "
    sql = sql + " WHERE home.name = game.home_name AND away.name = game.away_name AND home_stat.team_name = home.name "
    sql = sql + " AND away_stat.team_name = away_name AND game.date = home_stat.date AND game.date = away_stat.date "
    sql = sql + " AND home.type = away.type and home.type = %s AND game.date < %s ORDER BY game.date "

    c_game_stat.execute(sql, (league, now))


    rows = c_game_stat.fetchall()

    fp_url = 'data/'+ cvs_file
    fp = open(fp_url, 'w')
    myFile = csv.writer(fp)

    myFile.writerow(['ID','HOME','AWAY','ORB1','RTG1',
                         'ORB3','RTG3',"ORB5",'RTG5','DECISOR'])

    for x in rows:

        v_id = x["id"]
        v_homename = x["homename"]
        v_orb1 = x["a_orb_avg1"]
        v_orb3 = x["a_orb_avg3"]
        v_orb5 = x["a_orb_avg5"]
        v_rtg1 = x["a_ortg_avg1"]
        v_rtg3 = x["a_ortg_avg3"]
        v_rtg5 = x["a_ortg_avg5"]

        v_awayname = x["awayname"]
        v_decisor = x["decisor"]


        myFile.writerow([v_id,v_homename,v_awayname,v_orb1,v_rtg1,
                         v_orb3, v_rtg3,v_orb5,v_rtg5,v_decisor])

    fp.close()
    c_game_stat.close()
    connection.close()

def predictCsvGenerator(league, now, cvs_file):

    connection = pymysql.connect(host='192.168.99.100',
                             user='root',
                             password='stalinmaki',
                             db='sportbet',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    print "Generating Statistic CSV file..."
    c_game_stat = connection.cursor()

    sql = "SELECT game.id,home.name homename,away.name awayname, "
    sql = sql + " (home_stat.orb_avg1 - away_stat.orb_avg1) a_orb_avg1, "
    sql = sql + " (home_stat.ortg_avg1 - away_stat.ortg_avg1) a_ortg_avg1, "
    sql = sql + " (home_stat.orb_avg3 - away_stat.orb_avg3) a_orb_avg3, "
    sql = sql + " (home_stat.ortg_avg3 - away_stat.ortg_avg3) a_ortg_avg3, "
    sql = sql + " (home_stat.orb_avg5 - away_stat.orb_avg5) a_orb_avg5, "
    sql = sql + " (home_stat.ortg_avg5 - away_stat.ortg_avg5) a_ortg_avg5, "
    sql = sql + " case when home_point > away_point then home.name "
    sql = sql + " when home_point < away_point then away.name end decisor "
    sql = sql + " FROM nba_game game, nba_team home, nba_team away, nba_team_history home_stat, nba_team_history away_stat "
    sql = sql + " WHERE home.name = game.home_name AND away.name = game.away_name AND home_stat.team_name = home.name "
    sql = sql + " AND away_stat.team_name = away_name AND game.date = home_stat.date AND game.date = away_stat.date "
    sql = sql + " AND home.type = away.type and home.type = %s AND game.date = %s ORDER BY game.date "

    c_game_stat.execute(sql, (league, now))


    rows = c_game_stat.fetchall()

    fp_url = 'data/'+ cvs_file
    fp = open(fp_url, 'w')
    myFile = csv.writer(fp)

    myFile.writerow(['ID','HOME','AWAY','ORB1','RTG1',
                         'ORB3','RTG3',"ORB5",'RTG5','DECISOR'])

    for x in rows:

        v_id = x["id"]
        v_homename = x["homename"]
        v_orb1 = x["a_orb_avg1"]
        v_orb3 = x["a_orb_avg3"]
        v_orb5 = x["a_orb_avg5"]
        v_rtg1 = x["a_ortg_avg1"]
        v_rtg3 = x["a_ortg_avg3"]
        v_rtg5 = x["a_ortg_avg5"]

        v_awayname = x["awayname"]
        v_decisor = x["decisor"]


        myFile.writerow([v_id,v_homename,v_awayname,v_orb1,v_rtg1,
                         v_orb3, v_rtg3,v_orb5,v_rtg5,v_decisor])

    fp.close()
    c_game_stat.close()
    connection.close()