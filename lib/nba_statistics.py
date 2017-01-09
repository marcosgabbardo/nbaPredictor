import pymysql.cursors

def diff_dates(date1, date2):
    return abs(date2-date1).days

# statistic genaretor for averages, sums and other indicators from NBA
def statisticGenerator(league, season):

    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 port=3307,
                                 user='root',
                                 password='',
                                 db='sportbet',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    c_team = connection.cursor()
    c_game = connection.cursor()
    c_game_date = connection.cursor()
    c_game_inverse = connection.cursor()
    c_team_history_stat = connection.cursor()
    c_trunc_stat = connection.cursor()


    c_trunc_stat.execute("delete from nba_team_history where season = %s", (season))
    connection.commit()
    c_trunc_stat.close()

    print "Generating new statistics..."

    c_team.execute("SELECT name FROM nba_team where type in (%s)",(league))
    r = c_team.fetchall()

    for k in r:

        v_team_id = k["name"]
        print  k["name"]

        v_query = "SELECT date,home.name home_name,game.home_point home_point,away.name away_name,game.away_point away_point,overtime"
        v_query = v_query + " FROM nba_game game, nba_team home, nba_team away"
        v_query = v_query + " WHERE home.name = game.home_name AND away.name = game.away_name AND (home_name = %s OR away_name = %s)"
        v_query = v_query + " and season = %s "
       # v_query = v_query + " AND date <= (select min(date) from nba_game where season = game.season and nba_game.home_point IS NULL) "
        v_query = v_query + " ORDER BY game.date"

        c_game.execute(v_query,(v_team_id,v_team_id, season))

        s = c_game.fetchall()

        v_query = "SELECT date FROM nba_game game, nba_team home, nba_team away "
        v_query = v_query + " WHERE home.name = game.home_name AND away.name = game.away_name AND (home_name = %s OR away_name = %s) "
        v_query = v_query + " and season = %s "
        v_query = v_query + " AND date <= (select min(date) from nba_game where season = game.season and nba_game.home_point IS NULL) "
        v_query = v_query + " ORDER BY game.date"

        c_game_inverse.execute(v_query,(v_team_id,v_team_id, season))

        t = c_game_inverse.fetchall()

        for i in s:

            v_game_date = i["date"]

            sql = "INSERT INTO nba_team_history (team_name, date, season) "
            sql = sql + "VALUES (%s, %s, %s)"
            c_team_history_stat.execute(sql, (v_team_id, v_game_date, season))


        for j in t:

            v_win_last1 = 0
            v_win_last3 = 0
            v_win_last5 = 0
            v_win_last10 = 0
            v_avg_last1 = 0
            v_avg_last3 = 0
            v_avg_last5 = 0
            v_avg_last10 = 0


            v_avg_p1_b = 0
            v_avg_p2_b = 0
            v_avg_p3_b = 0
            v_avg_p4_b = 0

            v_avg5_p1_b = 0
            v_avg5_p2_b = 0
            v_avg5_p3_b = 0
            v_avg5_p4_b = 0

            v_avg10_p1_b = 0
            v_avg10_p2_b = 0
            v_avg10_p3_b = 0
            v_avg10_p4_b = 0

            v_avg_last1_b = 0
            v_avg_last3_b = 0
            v_avg_last5_b = 0
            v_avg_last10_b = 0

            v_sum_point_b = 0
            v_sum_p1_b = 0
            v_sum_p2_b = 0
            v_sum_p3_b = 0
            v_sum_p4_b = 0


            v_count_b = 0
            v_count_win_b = 0
            v_count_agn_b = 0
            v_sum_point_agn_b = 0

            v_sum_pace = 0
            v_sum_efg = 0
            v_sum_tov = 0
            v_sum_orb = 0
            v_sum_ftfga = 0
            v_sum_ortg = 0

            v_pace1 = 0
            v_efg1 = 0
            v_tov1 = 0
            v_orb1 = 0
            v_ftfga1 = 0
            v_ortg1 = 0

            v_pace3 = 0
            v_efg3 = 0
            v_tov3 = 0
            v_orb3 = 0
            v_ftfga3 = 0
            v_ortg3 = 0

            v_pace5 = 0
            v_efg5 = 0
            v_tov5 = 0
            v_orb5 = 0
            v_ftfga5 = 0
            v_ortg5 = 0

            v_pace10 = 0
            v_efg10 = 0
            v_tov10 = 0
            v_orb10 = 0
            v_ftfga10 = 0
            v_ortg10 = 0

            v_auxiliar = 0

            v_aux_date = j["date"]

            v_query = "SELECT date,home.name home_name,game.home_point home_point,away.name away_name,game.away_point, "
            v_query = v_query +" away_point,overtime, home_pace, home_efg, home_tov, home_orb, home_ftfga, home_ortg,"
            v_query = v_query + " home_p1, home_p2, home_p3, home_p4, away_p1, away_p2, away_p3, away_p4,"
            v_query = v_query + " away_pace, away_efg, away_tov, away_orb, away_ftfga, away_ortg "
            v_query = v_query + " FROM nba_game game, nba_team home, nba_team away"
            v_query = v_query + " WHERE home.name = game.home_name AND away.name = game.away_name AND (home_name = %s OR away_name = %s)"
            v_query = v_query + " AND game.date < %s "
            v_query = v_query + " and season = %s"
            v_query = v_query + " ORDER BY game.date DESC"

            c_game_date.execute(v_query,(v_team_id,v_team_id, v_aux_date, season))

            u = c_game_date.fetchall()

            v_game_overtime = "NA"
            v_day_diff = 0

            for m in u:

                v_game_date = m["date"]
                v_game_home_id = m["home_name"]
                v_game_home_point = m["home_point"]
                v_home_p1 = m["home_p1"]
                v_home_p2 = m["home_p2"]
                v_home_p3 = m["home_p3"]
                v_home_p4 = m["home_p4"]


                v_game_away_id = m["away_name"]
                v_game_away_point = m["away_point"]
                v_away_p1 = m["away_p1"]
                v_away_p2 = m["away_p2"]
                v_away_p3 = m["away_p3"]
                v_away_p4 = m["away_p4"]

                v_auxiliar = v_auxiliar + 1

                if v_team_id == v_game_home_id :
                    v_count_b = v_count_b + 1
                    v_sum_point_b = v_sum_point_b + v_game_home_point
                    v_sum_p1_b = v_sum_p1_b + v_home_p1
                    v_sum_p2_b = v_sum_p2_b + v_home_p2
                    v_sum_p3_b = v_sum_p3_b + v_home_p3
                    v_sum_p4_b = v_sum_p4_b + v_home_p4


                    v_sum_pace = v_sum_pace + m["home_pace"]
                    v_sum_efg = v_sum_efg + m["home_efg"]
                    v_sum_tov = v_sum_tov + m["home_tov"]
                    v_sum_orb = v_sum_orb + m["home_orb"]
                    v_sum_ftfga = v_sum_ftfga + m["home_ftfga"]
                    v_sum_ortg = v_sum_ortg + m["home_ortg"]

                    if v_game_home_point > v_game_away_point :
                        v_count_win_b = v_count_win_b + 1

                if v_team_id == v_game_away_id :
                    v_count_b = v_count_b + 1
                    v_sum_point_b = v_sum_point_b + v_game_away_point
                    v_sum_p1_b = v_sum_p1_b + v_away_p1
                    v_sum_p2_b = v_sum_p2_b + v_away_p2
                    v_sum_p3_b = v_sum_p3_b + v_away_p3
                    v_sum_p4_b = v_sum_p4_b + v_away_p4

                    v_sum_pace = v_sum_pace + m["away_pace"]
                    v_sum_efg = v_sum_efg + m["away_efg"]
                    v_sum_tov = v_sum_tov + m["away_tov"]
                    v_sum_orb = v_sum_orb + m["away_orb"]
                    v_sum_ftfga = v_sum_ftfga + m["away_ftfga"]
                    v_sum_ortg = v_sum_ortg + m["away_ortg"]

                    if v_game_away_point > v_game_home_point :
                        v_count_win_b = v_count_win_b + 1

                if v_team_id <> v_game_home_id and v_team_id == v_game_away_id :
                    v_count_agn_b = v_count_agn_b + 1
                    v_sum_point_agn_b = v_sum_point_agn_b + v_game_home_point

                if v_team_id == v_game_home_id and v_team_id <> v_game_away_id :
                    v_count_agn_b = v_count_agn_b + 1
                    v_sum_point_agn_b = v_sum_point_agn_b + v_game_away_point

                if v_auxiliar == 1 :

                    v_win_last1 = v_count_win_b
                    v_avg_last1 = v_sum_point_b/v_count_b

                    v_avg_last1_b = v_sum_point_agn_b/v_count_agn_b
                    v_game_overtime = m["overtime"]
                    v_day_diff = diff_dates(v_game_date, v_aux_date)

                    v_pace1 = v_sum_pace/v_count_b
                    v_efg1 = v_sum_efg/v_count_b
                    v_tov1 = v_sum_tov/v_count_b
                    v_orb1 = v_sum_orb/v_count_b
                    v_ftfga1 = v_sum_ftfga/v_count_b
                    v_ortg1 = v_sum_ortg/v_count_b

                if v_auxiliar == 3 :

                    v_win_last3 = v_count_win_b
                    v_avg_last3 = v_sum_point_b/v_count_b
                    v_avg_last3_b = v_sum_point_agn_b/v_count_agn_b

                    v_pace3 = v_sum_pace/v_count_b
                    v_efg3 = v_sum_efg/v_count_b
                    v_tov3 = v_sum_tov/v_count_b
                    v_orb3 = v_sum_orb/v_count_b
                    v_ftfga3 = v_sum_ftfga/v_count_b
                    v_ortg3 = v_sum_ortg/v_count_b

                if v_auxiliar == 5 :

                    v_win_last5 = v_count_win_b
                    v_avg_last5 = v_sum_point_b/v_count_b
                    v_avg5_p1_b = v_sum_p1_b / v_count_b
                    v_avg5_p2_b = v_sum_p2_b / v_count_b
                    v_avg5_p3_b = v_sum_p3_b / v_count_b
                    v_avg5_p4_b = v_sum_p4_b / v_count_b


                    v_avg_last5_b = v_sum_point_agn_b/v_count_agn_b

                    v_pace5 = v_sum_pace/v_count_b
                    v_efg5 = v_sum_efg/v_count_b
                    v_tov5 = v_sum_tov/v_count_b
                    v_orb5 = v_sum_orb/v_count_b
                    v_ftfga5 = v_sum_ftfga/v_count_b
                    v_ortg5 = v_sum_ortg/v_count_b

                if v_auxiliar == 10 :

                    v_win_last10 = v_count_win_b
                    v_avg_last10 = v_sum_point_b/v_count_b
                    v_avg10_p1_b = v_sum_p1_b / v_count_b
                    v_avg10_p2_b = v_sum_p2_b / v_count_b
                    v_avg10_p3_b = v_sum_p3_b / v_count_b
                    v_avg10_p4_b = v_sum_p4_b / v_count_b


                    v_avg_last10_b = v_sum_point_agn_b/v_count_agn_b

                    v_pace10 = v_sum_pace/v_count_b
                    v_efg10 = v_sum_efg/v_count_b
                    v_tov10 = v_sum_tov/v_count_b
                    v_orb10 = v_sum_orb/v_count_b
                    v_ftfga10 = v_sum_ftfga/v_count_b
                    v_ortg10 = v_sum_ortg/v_count_b

            if v_count_b > 0 :
                v_avg_point = v_sum_point_b/v_count_b
                v_avg_p1_b = v_sum_p1_b / v_count_b
                v_avg_p2_b = v_sum_p2_b / v_count_b
                v_avg_p3_b = v_sum_p3_b / v_count_b
                v_avg_p4_b = v_sum_p4_b / v_count_b

                v_pace_total = v_sum_pace/v_count_b
                v_efg_total = v_sum_efg/v_count_b
                v_tov_total = v_sum_tov/v_count_b
                v_orb_total = v_sum_orb/v_count_b
                v_ftfga_total = v_sum_ftfga/v_count_b
                v_ortg_total = v_sum_ortg/v_count_b

            else :
                v_avg_point = 0
                v_avg_p1_b = 0
                v_avg_p2_b = 0
                v_avg_p3_b = 0
                v_avg_p4_b = 0

                v_pace_total = 0
                v_efg_total = 0
                v_tov_total = 0
                v_orb_total = 0
                v_ftfga_total = 0
                v_ortg_total = 0


            if v_count_agn_b > 0 :
                v_avga_point = v_sum_point_agn_b/v_count_agn_b
            else :
                v_avga_point = 0


            sql = "UPDATE nba_team_history SET "
            sql = sql + " last1 = %s, last3 = %s, last5 = %s, last10 = %s, pointavg1 = %s, pointavg3 = %s, pointavg5 = %s, pointavg10 = %s, "
            sql = sql + " pointavg1a = %s, pointavg3a = %s, pointavg5a = %s, pointavg10a = %s, pointavg = %s, pointavga = %s, "
            sql = sql + " game = %s, win = %s, overtime = %s, day_diff = %s , pace_avg = %s , efg_avg = %s , tov_avg = %s, orb_avg = %s, "
            sql = sql + " ftfga_avg = %s, ortg_avg = %s, pace_avg1 = %s , efg_avg1 = %s , tov_avg1 = %s, orb_avg1 = %s, ftfga_avg1 = %s, ortg_avg1 = %s, "
            sql = sql + " pace_avg3 = %s , efg_avg3 = %s , tov_avg3 = %s, orb_avg3 = %s, ftfga_avg3 = %s, ortg_avg3 = %s, "
            sql = sql + " pace_avg5 = %s , efg_avg5 = %s , tov_avg5 = %s, orb_avg5 = %s, ftfga_avg5 = %s, ortg_avg5 = %s, "
            sql = sql + " pace_avg10 = %s , efg_avg10 = %s , tov_avg10 = %s, orb_avg10 = %s, ftfga_avg10 = %s, ortg_avg10 = %s, "
            sql = sql + " p1_avg = %s , p2_avg = %s, p3_avg = %s, p4_avg = %s, p1_avg5 = %s, p2_avg5 = %s, p3_avg5 = %s,"
            sql = sql + " p4_avg5 = %s, p1_avg10 = %s, p2_avg10 = %s, p3_avg10 = %s, p4_avg10 = %s "
            sql = sql + " WHERE team_name = %s and date = %s"
            c_team_history_stat.execute(sql, (v_win_last1, v_win_last3, v_win_last5, v_win_last10, v_avg_last1, v_avg_last3,
                                              v_avg_last5, v_avg_last10,v_avg_last1_b,v_avg_last3_b,v_avg_last5_b,v_avg_last10_b,
                                              v_avg_point, v_avga_point, v_count_b, v_count_win_b, v_game_overtime, v_day_diff,
                                              v_pace_total, v_efg_total, v_tov_total, v_orb_total, v_ftfga_total, v_ortg_total,
                                              v_pace1, v_efg1, v_tov1, v_orb1, v_ftfga1, v_ortg1,
                                              v_pace3, v_efg3, v_tov3, v_orb3, v_ftfga3, v_ortg3,
                                              v_pace5, v_efg5, v_tov5, v_orb5, v_ftfga5, v_ortg5,
                                              v_pace10, v_efg10, v_tov10, v_orb10, v_ftfga10, v_ortg10,
                                              v_avg_p1_b, v_avg_p2_b, v_avg_p3_b, v_avg_p4_b,
                                              v_avg5_p1_b, v_avg5_p2_b, v_avg5_p3_b, v_avg5_p4_b,
                                              v_avg10_p1_b, v_avg10_p2_b, v_avg10_p3_b, v_avg10_p4_b,
                                              v_team_id, v_aux_date))



        connection.commit()


    c_team_history_stat.close()
    c_game.close()
    c_game_date.close()
    c_game_inverse.close()
    c_team.close()
    connection.close()

# calc for streak (number of loses or wins in sequence)
def streakcalc(league, season):
    connection = pymysql.connect(host='localhost',
                                 port=3307,
                                 user='root',
                                 password='',
                                 db='sportbet',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    c_team = connection.cursor()
    c_game = connection.cursor()
    c_update = connection.cursor()

    c_team.execute("SELECT name FROM nba_team where type in (%s)",(league))
    r = c_team.fetchall()

    print "Iniciando calculo de streaks..."

    for k in r:

        v_player = k["name"]

        v_query = "SELECT game.date date,game.team_name player, game.win win"
        v_query = v_query + " FROM nba_team_history game"
        v_query = v_query + " WHERE (game.team_name = %s)"
        v_query = v_query + " and game.season = %s"
        v_query = v_query + " ORDER BY game.date"


        c_game.execute(v_query,(v_player, season))
        s = c_game.fetchall()

        v_win_streak = 0
        v_loss_streak = 0
        v_wins = 0
        v_wins_ant = 0

        for i in s:

            v_game_date = i["date"]
            v_wins = i["win"]

            if v_wins > v_wins_ant:
               v_win_streak = v_win_streak + 1
               v_loss_streak = 0
            else:
               v_win_streak = 0
               v_loss_streak = v_loss_streak + 1

            sql = "UPDATE nba_team_history set win_streak = %s, loss_streak = %s WHERE team_name = %s and date = %s"

            c_update.execute(sql, (v_win_streak, v_loss_streak, v_player, v_game_date))

            v_wins_ant = v_wins


    connection.commit()
    c_update.close()
    c_team.close()
    c_game.close()

# FG% statistics from play by play, quarter by quarter
def fgquarter():

    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 port=3307,
                                 user='root',
                                 password='',
                                 db='sportbet',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    c_teamhome = connection.cursor()
    c_team_fg = connection.cursor()

    print "Calculating new FG per quarter for teams..."

    v_query = " SELECT id, "
    v_query = v_query + " SUM(CASE WHEN home_comment LIKE '%makes%' and quarter = 1 THEN 1 ELSE 0 END) / "
    v_query = v_query + " (SUM(CASE WHEN home_comment LIKE '%makes%' and quarter = 1 THEN 1 ELSE 0 END) + "
    v_query = v_query + " SUM(CASE WHEN home_comment LIKE '%misses%' and quarter = 1 THEN 1 ELSE 0 END)) home_percentual_fg1, "
    v_query = v_query + " SUM(CASE WHEN home_comment LIKE '%makes%' and quarter = 2 THEN 1 ELSE 0 END) / "
    v_query = v_query + " (SUM(CASE WHEN home_comment LIKE '%makes%' and quarter = 2 THEN 1 ELSE 0 END) + "
    v_query = v_query + " SUM(CASE WHEN home_comment LIKE '%misses%' and quarter = 2 THEN 1 ELSE 0 END)) home_percentual_fg2, "
    v_query = v_query + " SUM(CASE WHEN home_comment LIKE '%makes%' and quarter = 3 THEN 1 ELSE 0 END) / "
    v_query = v_query + " (SUM(CASE WHEN home_comment LIKE '%makes%' and quarter = 3 THEN 1 ELSE 0 END) + "
    v_query = v_query + " SUM(CASE WHEN home_comment LIKE '%misses%' and quarter = 3 THEN 1 ELSE 0 END)) home_percentual_fg3, "
    v_query = v_query + " SUM(CASE WHEN home_comment LIKE '%makes%' and quarter = 4 THEN 1 ELSE 0 END) / "
    v_query = v_query + " (SUM(CASE WHEN home_comment LIKE '%makes%' and quarter = 4 THEN 1 ELSE 0 END) + "
    v_query = v_query + " SUM(CASE WHEN home_comment LIKE '%misses%' and quarter = 4 THEN 1 ELSE 0 END)) home_percentual_fg4, "
    v_query = v_query + " SUM(CASE WHEN away_comment LIKE '%makes%' and quarter = 1 THEN 1 ELSE 0 END) / "
    v_query = v_query + " (SUM(CASE WHEN away_comment LIKE '%makes%' and quarter = 1 THEN 1 ELSE 0 END) + "
    v_query = v_query + " SUM(CASE WHEN away_comment LIKE '%misses%' and quarter = 1 THEN 1 ELSE 0 END)) away_percentual_fg1, "
    v_query = v_query + " SUM(CASE WHEN away_comment LIKE '%makes%' and quarter = 2 THEN 1 ELSE 0 END) / "
    v_query = v_query + " (SUM(CASE WHEN away_comment LIKE '%makes%' and quarter = 2 THEN 1 ELSE 0 END) + "
    v_query = v_query + " SUM(CASE WHEN away_comment LIKE '%misses%' and quarter = 2 THEN 1 ELSE 0 END)) away_percentual_fg2, "
    v_query = v_query + " SUM(CASE WHEN away_comment LIKE '%makes%' and quarter = 3 THEN 1 ELSE 0 END) / "
    v_query = v_query + " (SUM(CASE WHEN away_comment LIKE '%makes%' and quarter = 3 THEN 1 ELSE 0 END) + "
    v_query = v_query + " SUM(CASE WHEN away_comment LIKE '%misses%' and quarter = 3 THEN 1 ELSE 0 END)) away_percentual_fg3, "
    v_query = v_query + " SUM(CASE WHEN away_comment LIKE '%makes%' and quarter = 4 THEN 1 ELSE 0 END) / "
    v_query = v_query + " (SUM(CASE WHEN away_comment LIKE '%makes%' and quarter = 4 THEN 1 ELSE 0 END) + "
    v_query = v_query + " SUM(CASE WHEN away_comment LIKE '%misses%' and quarter = 4 THEN 1 ELSE 0 END)) away_percentual_fg4 "
    v_query = v_query + " FROM nba_playbyplay WHERE id in (select id2 from nba_game where "
    v_query = v_query + " fg_home_p1 is null) "
    v_query = v_query + " GROUP BY id "

    c_teamhome.execute(v_query)
    r = c_teamhome.fetchall()

    for k in r:

        v_teamhome_id = k["id"]
        v_teamhome_fg1 = k["home_percentual_fg1"]
        v_teamhome_fg2 = k["home_percentual_fg2"]
        v_teamhome_fg3 = k["home_percentual_fg3"]
        v_teamhome_fg4 = k["home_percentual_fg4"]

        v_teamaway_fg1 = k["away_percentual_fg1"]
        v_teamaway_fg2 = k["away_percentual_fg2"]
        v_teamaway_fg3 = k["away_percentual_fg3"]
        v_teamaway_fg4 = k["away_percentual_fg4"]

        print  k["id"]

        sql = "UPDATE nba_game SET "
        sql = sql + " fg_home_p1 = %s, fg_home_p2 = %s, fg_home_p3 = %s, fg_home_p4 = %s, fg_away_p1 = %s, "
        sql = sql + " fg_away_p2 = %s, fg_away_p3 = %s, fg_away_p4 = %s "
        sql = sql + " WHERE id2 = %s"
        c_team_fg.execute(sql,(v_teamhome_fg1, v_teamhome_fg2, v_teamhome_fg3, v_teamhome_fg4,
                               v_teamaway_fg1, v_teamaway_fg2, v_teamaway_fg3, v_teamaway_fg4 ,v_teamhome_id))

    connection.commit()
    c_teamhome.close()
    c_team_fg.close()
        
    connection.close()

# turnovers statistics from play by play, quarter by quarter
def toquarter():
    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 port=3307,
                                 user='root',
                                 password='',
                                 db='sportbet',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    c_teamhome = connection.cursor()
    c_team_to = connection.cursor()

    print "Calculating new TO per quarter for teams..."

    v_query = " SELECT id, "
    v_query = v_query + " SUM(CASE WHEN home_comment LIKE '%Turnover%' and quarter = 1 THEN 1 ELSE 0 END) to_home_p1, "
    v_query = v_query + " SUM(CASE WHEN home_comment LIKE '%Turnover%' and quarter = 2 THEN 1 ELSE 0 END) to_home_p2, "
    v_query = v_query + " SUM(CASE WHEN home_comment LIKE '%Turnover%' and quarter = 3 THEN 1 ELSE 0 END) to_home_p3, "
    v_query = v_query + " SUM(CASE WHEN home_comment LIKE '%Turnover%' and quarter = 4 THEN 1 ELSE 0 END) to_home_p4, "
    v_query = v_query + " SUM(CASE WHEN away_comment LIKE '%Turnover%' and quarter = 1 THEN 1 ELSE 0 END) to_away_p1, "
    v_query = v_query + " SUM(CASE WHEN away_comment LIKE '%Turnover%' and quarter = 2 THEN 1 ELSE 0 END) to_away_p2, "
    v_query = v_query + " SUM(CASE WHEN away_comment LIKE '%Turnover%' and quarter = 3 THEN 1 ELSE 0 END) to_away_p3, "
    v_query = v_query + " SUM(CASE WHEN away_comment LIKE '%Turnover%' and quarter = 4 THEN 1 ELSE 0 END) to_away_p4 "
    v_query = v_query + " FROM nba_playbyplay WHERE id in (select id2 from nba_game where "
    v_query = v_query + " to_home_p1 is null) "
    v_query = v_query + " GROUP BY id "

    c_teamhome.execute(v_query)
    r = c_teamhome.fetchall()

    for k in r:
        v_teamhome_id = k["id"]
        v_teamhome_to1 = k["to_home_p1"]
        v_teamhome_to2 = k["to_home_p2"]
        v_teamhome_to3 = k["to_home_p3"]
        v_teamhome_to4 = k["to_home_p4"]

        v_teamaway_to1 = k["to_away_p1"]
        v_teamaway_to2 = k["to_away_p2"]
        v_teamaway_to3 = k["to_away_p3"]
        v_teamaway_to4 = k["to_away_p4"]

        print  k["id"]

        sql = "UPDATE nba_game SET "
        sql = sql + " to_home_p1 = %s, to_home_p2 = %s, to_home_p3 = %s, to_home_p4 = %s, to_away_p1 = %s, "
        sql = sql + " to_away_p2 = %s, to_away_p3 = %s, to_away_p4 = %s "
        sql = sql + " WHERE id2 = %s"
        c_team_to.execute(sql, (v_teamhome_to1, v_teamhome_to2, v_teamhome_to3, v_teamhome_to4,
                                v_teamaway_to1, v_teamaway_to2, v_teamaway_to3, v_teamaway_to4, v_teamhome_id))

    connection.commit()
    c_teamhome.close()
    c_team_to.close()

    connection.close()

# rebounds statistics from play by play, quarter by quarter
def rbquarter():
    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 port=3307,
                                 user='root',
                                 password='',
                                 db='sportbet',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    c_teamhome = connection.cursor()
    c_team_rb = connection.cursor()

    print "Calculating new RB per quarter for teams..."

    v_query = " SELECT id, "
    v_query = v_query + " SUM(CASE WHEN home_comment LIKE '%Rebound%' and quarter = 1 THEN 1 ELSE 0 END) rb_home_p1, "
    v_query = v_query + " SUM(CASE WHEN home_comment LIKE '%Rebound%' and quarter = 2 THEN 1 ELSE 0 END) rb_home_p2, "
    v_query = v_query + " SUM(CASE WHEN home_comment LIKE '%Rebound%' and quarter = 3 THEN 1 ELSE 0 END) rb_home_p3, "
    v_query = v_query + " SUM(CASE WHEN home_comment LIKE '%Rebound%' and quarter = 4 THEN 1 ELSE 0 END) rb_home_p4, "
    v_query = v_query + " SUM(CASE WHEN away_comment LIKE '%Rebound%' and quarter = 1 THEN 1 ELSE 0 END) rb_away_p1, "
    v_query = v_query + " SUM(CASE WHEN away_comment LIKE '%Rebound%' and quarter = 2 THEN 1 ELSE 0 END) rb_away_p2, "
    v_query = v_query + " SUM(CASE WHEN away_comment LIKE '%Rebound%' and quarter = 3 THEN 1 ELSE 0 END) rb_away_p3, "
    v_query = v_query + " SUM(CASE WHEN away_comment LIKE '%Rebound%' and quarter = 4 THEN 1 ELSE 0 END) rb_away_p4 "
    v_query = v_query + " FROM nba_playbyplay WHERE id in (select id2 from nba_game where "
    v_query = v_query + " rb_home_p1 is null) "
    v_query = v_query + " GROUP BY id "

    c_teamhome.execute(v_query)
    r = c_teamhome.fetchall()

    for k in r:
        v_teamhome_id = k["id"]
        v_teamhome_rb1 = k["rb_home_p1"]
        v_teamhome_rb2 = k["rb_home_p2"]
        v_teamhome_rb3 = k["rb_home_p3"]
        v_teamhome_rb4 = k["rb_home_p4"]

        v_teamaway_rb1 = k["rb_away_p1"]
        v_teamaway_rb2 = k["rb_away_p2"]
        v_teamaway_rb3 = k["rb_away_p3"]
        v_teamaway_rb4 = k["rb_away_p4"]

        print  k["id"]

        sql = "UPDATE nba_game SET "
        sql = sql + " rb_home_p1 = %s, rb_home_p2 = %s, rb_home_p3 = %s, rb_home_p4 = %s, rb_away_p1 = %s, "
        sql = sql + " rb_away_p2 = %s, rb_away_p3 = %s, rb_away_p4 = %s "
        sql = sql + " WHERE id2 = %s"
        c_team_rb.execute(sql, (v_teamhome_rb1, v_teamhome_rb2, v_teamhome_rb3, v_teamhome_rb4,
                                v_teamaway_rb1, v_teamaway_rb2, v_teamaway_rb3, v_teamaway_rb4, v_teamhome_id))

    connection.commit()
    c_teamhome.close()
    c_team_rb.close()

    connection.close()