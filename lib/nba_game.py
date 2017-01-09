import pymysql.cursors
import requests
from bs4 import BeautifulSoup

# import games from basketball reference
def gameimporter(season,month):

    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 port=3307,
                                 user='root',
                                 password='',
                                 db='sportbet',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    BASE_GAME_URL = 'http://www.basketball-reference.com/boxscores/{0}'

    BASE_URL = 'http://www.basketball-reference.com/leagues/NBA_'+ season +'_games-'+ month +'.html'

    if month == 'october':
        month_num = 10
    elif month == 'november':
        month_num = 11
    elif month == 'december':
        month_num = 12
    elif month == 'january':
        month_num = 1
    elif month == 'february':
        month_num = 2
    elif month == 'march':
        month_num = 3
    elif month == 'april':
        month_num = 4
    elif month == 'may':
        month_num = 5
    elif month == 'june':
        month_num = 6


    c_trunc_stat = connection.cursor()
    c_trunc_stat.execute("delete from nba_game where season = %s and month(date) = %s", (season, month_num))
    connection.commit()
    c_trunc_stat.close()

    c_insert_game = connection.cursor()

    print 'Importing new games...'

    r = requests.get(BASE_URL)
    table = BeautifulSoup(r.text, "lxml").table
    for row in table.find_all('tr')[1:]:

        columns = row.find_all('td')
        column_special = row.find_all('th')


        if columns:
            if columns[5].text:

                _id = columns[5].a['href'].split('/boxscores/')[1]
                _home_point = columns[4].text
                _away_point = columns[2].text
                _home_team = columns[3].text
                _away_team = columns[1].text

                _day = column_special[0].text[9:-6]
                _year = column_special[0].text[-4:]

                _date = str(_year) + '-' + str(month_num) + '-' + str(_day)

                print (_date + ' - ' + _home_team + ' vs ' + _away_team)

                _hour = columns[0].text[:-5]
                _overtime = columns[6].text

                # Extra stats
                r = requests.get(BASE_GAME_URL.format(_id))
                table_ext = BeautifulSoup(r.text, 'lxml').find("div", {"id": "all_line_score"})

                ajuda = str(table_ext)
                ajuda = ajuda.replace('<!--', '')
                ajuda = ajuda.replace('-->', '')

                table_ext = BeautifulSoup(ajuda, 'lxml')

                aux = 1
                _id = _id[:-5]

                for row_ext in table_ext.find_all('tr')[2:]:
                    columns_ext = row_ext.find_all('td')

                    if aux == 1:
                        _away_p1 = int(columns_ext[1].text)
                        _away_p2 = int(columns_ext[2].text)
                        _away_p3 = int(columns_ext[3].text)
                        _away_p4 = int(columns_ext[4].text)
                    else:
                        _home_p1 = int(columns_ext[1].text)
                        _home_p2 = int(columns_ext[2].text)
                        _home_p3 = int(columns_ext[3].text)
                        _home_p4 = int(columns_ext[4].text)

                    aux = aux + 1

                table_ext = BeautifulSoup(r.text, "lxml").find('table', id ='four_factors')

                table_ext = BeautifulSoup(r.text, 'lxml').find("div", {"id": "all_four_factors"})

                ajuda = str(table_ext)
                ajuda = ajuda.replace('<!--', '')
                ajuda = ajuda.replace('-->', '')

                table_ext = BeautifulSoup(ajuda, 'lxml')


                aux = 1

                for row_ext in table_ext.find_all('tr')[2:]:
                    columns_ext = row_ext.find_all('td')

                    if aux == 1:
                        _away_pace = float(columns_ext[0].text)
                        _away_efg = float(columns_ext[1].text)
                        _away_tov = float(columns_ext[2].text)
                        _away_orb = float(columns_ext[3].text)
                        _away_ftfga = float(columns_ext[4].text)
                        _away_ortg = float(columns_ext[5].text)
                    else:
                        _home_pace = float(columns_ext[0].text)
                        _home_efg = float(columns_ext[1].text)
                        _home_tov = float(columns_ext[2].text)
                        _home_orb = float(columns_ext[3].text)
                        _home_ftfga = float(columns_ext[4].text)
                        _home_ortg = float(columns_ext[5].text)

                    aux = aux + 1

                sql = "INSERT INTO nba_game (date, home_point, away_point, home_name, away_name, home_p1, home_p2, "
                sql = sql + "home_p3, home_p4, away_p1, away_p2, away_p3, away_p4, home_pace, home_efg, home_tov, "
                sql = sql + "home_orb, home_ftfga, home_ortg, away_pace, away_efg, away_tov, "
                sql = sql + "away_orb, away_ftfga, away_ortg, id2, overtime, season)"
                sql = sql + "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
                sql = sql + "%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                c_insert_game.execute(sql,(_date, _home_point, _away_point, _home_team, _away_team, _home_p1, _home_p2,
                                           _home_p3, _home_p4, _away_p1, _away_p2, _away_p3, _away_p4,_home_pace,
                                           _home_efg,_home_tov,_home_orb,_home_ftfga,_home_ortg, _away_pace,
                                           _away_efg,_away_tov,_away_orb,_away_ftfga,_away_ortg, _id, _overtime, season))

            else:

                _home_team = columns[3].text
                _away_team = columns[1].text

                _day = column_special[0].text[9:-6]
                _year = column_special[0].text[-4:]

                _date = str(_year) + '-' + str(month_num) + '-' + str(_day)

                print (_date + ' - ' + _home_team + ' vs ' + _away_team)

                sql = "INSERT INTO nba_game (date, home_point, away_point, home_name, away_name, home_p1, home_p2, "
                sql = sql + "home_p3, home_p4, away_p1, away_p2, away_p3, away_p4, home_pace, home_efg, home_tov, "
                sql = sql + "home_orb, home_ftfga, home_ortg, away_pace, away_efg, away_tov, "
                sql = sql + "away_orb, away_ftfga, away_ortg, id2, overtime, season)"
                sql = sql + "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
                sql = sql + "%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                c_insert_game.execute(sql, (_date, None, None, _home_team, _away_team, None, None,
                                            None, None, None, None, None, None, None,
                                            None, None, None, None, None, None,
                                            None, None, None, None, None, None, None,
                                            season))



    connection.commit()
    c_insert_game.close()
    connection.close()

# import play by play from basketball reference
def playbyplay(date):

    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 port=3307,
                                 user='root',
                                 password='',
                                 db='sportbet',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    c_team = connection.cursor()
    c_insert_game = connection.cursor()

    print 'Deleting play by play...'

    c_trunc_stat = connection.cursor()
    c_trunc_stat.execute("delete from nba_playbyplay where id in (select id2 from nba_game where date = %s )",  date)
    connection.commit()
    c_trunc_stat.close()


    print 'Selecting play by play games...'
    c_team.execute("SELECT id2 FROM nba_game where id2 is not null and date = %s order by date", date)
    r = c_team.fetchall()

    print 'Importing play by play...'

    for k in r:

        _id = k["id2"]

        BASE_GAME_URL = 'http://www.basketball-reference.com/boxscores/pbp/'+ _id + '.html'

        print _id

        r = requests.get(BASE_GAME_URL)

        for table in BeautifulSoup(r.text, "lxml").find_all('table', attrs={'id':'pbp'}):

            for row in table.find_all('tr'):

                if row.get('id') == 'q1':
                    _quarter = 1
                elif row.get('id') == 'q2':
                    _quarter = 2
                elif row.get('id') == 'q3':
                    _quarter = 3
                elif row.get('id') == 'q4':
                    _quarter = 4
                elif row.get('id') == 'q5':
                    _quarter = 5
                elif row.get('id') == 'q6':
                    _quarter = 6
                elif row.get('id') == 'q7':
                    _quarter = 7
                elif row.get('id') == 'q8':
                    _quarter = 8
                elif row.get('id') == 'q9':
                    _quarter = 9
                elif row.get('id') == 'q10':
                    _quarter = 10
                else:
                    _quarter = _quarter

                columns = row.find_all('td')
                if columns:

                    try:
                        if columns[5].text:

                            _duration = 720 - ((int(columns[0].text[-7:-5])*60) + int(columns[0].text[-4:-2]))
                            _away_comment = columns[1].text.replace("!@#$%^&*()[]{};:,./<>?\|`~-=_+", "")
                            _away_score = columns[2].text[1:]
                            _home_comment = columns[5].text.replace("!@#$%^&*()[]{};:,./<>?\|`~-=_+", "")
                            _home_score= columns[4].text[1:]


                            if _away_comment == '':
                                _away_comment = ''
                            if _home_comment == '':
                                _home_comment = ''

                            if _away_score == '':
                                _away_score = 0
                            if _home_score == '':
                                _home_score = 0

                            sql = "INSERT INTO nba_playbyplay (id, quarter, duration, home_comment, home_score, away_comment, away_score) "
                            sql = sql + "VALUES (%s, %s, %s, %s, %s, %s, %s )"
                            c_insert_game.execute(sql,(_id, _quarter, _duration, _home_comment, _home_score,_away_comment, _away_score))

                    except IndexError:
                            gotdata = 'null'

        connection.commit()
    c_insert_game.close()
    connection.close()

# under construction
def handicap(date):

    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 port=3307,
                                 user='root',
                                 password='',
                                 db='sportbet',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    c_odd = connection.cursor()

    print 'Insert today games odds...'

    sql = "insert into odd ( "
    sql = sql + "SELECT "
    sql = sql + "concat(year(nba_game.date), "
    sql = sql + "case when length(month(nba_game.date)) = 1 then concat(0,month(nba_game.date)) else month(nba_game.date) end, "
    sql = sql + "case when length(day(nba_game.date)) = 1 then concat(0,day(nba_game.date)) else day(nba_game.date) end, "
    sql = sql + "'0', abrev )id, nba_game.date date, 'HANDICAP', null, 'N', null "
    sql = sql + "FROM nba_team, nba_game "
    sql = sql + "WHERE nba_team.name = nba_game.home_name and nba_game.date = %s) "

    c_odd.execute(sql, date)
    r = c_odd.fetchall()

    connection.commit()

    c_odd.close()
# under construction
def ponderation(date):

    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 port=3307,
                                 user='root',
                                 password='',
                                 db='sportbet',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    c_odd = connection.cursor()

    print 'Insert today games ponderations...'

    sql = "insert into nba_ponderation ( "
    sql = sql + "SELECT "
    sql = sql + "concat(year(nba_game.date), "
    sql = sql + "case when length(month(nba_game.date)) = 1 then concat(0,month(nba_game.date)) else month(nba_game.date) end, "
    sql = sql + "case when length(day(nba_game.date)) = 1 then concat(0,day(nba_game.date)) else day(nba_game.date) end, "
    sql = sql + "'0', abrev )id, nba_game.date date, nba_game.home_name, nba_game.away_name, null "
    sql = sql + "FROM nba_team, nba_game "
    sql = sql + "WHERE nba_team.name = nba_game.home_name and nba_game.date = %s) "

    c_odd.execute(sql, date)
    r = c_odd.fetchall()

    connection.commit()

    c_odd.close()
# under construction
def idformater(date):

    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 port=3307,
                                 user='root',
                                 password='',
                                 db='sportbet',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    c_team = connection.cursor()
    c_update_game = connection.cursor()

    sql = " select CONCAT(YEAR(game.date), "
    sql = sql + " CASE WHEN LENGTH(MONTH(game.date)) = 1 THEN CONCAT(0, MONTH(game.date)) "
    sql = sql + " ELSE MONTH(game.date) END, "
    sql = sql + " CASE WHEN LENGTH(DAY(game.date)) = 1 THEN CONCAT(0, DAY(game.date)) "
    sql = sql + " ELSE DAY(game.date) END, '0', abrev) id, "
    sql = sql + " game.home_name home_name, game.away_name away_name, game.date date"
    sql = sql + " FROM nba_team, nba_game game "
    sql = sql + " WHERE nba_team.name = game.home_name and game.date = %s "

    c_team.execute(sql, date)
    r = c_team.fetchall()

    print 'updating id'

    for k in r:

        _id = k["id"]
        _home_name = k["home_name"]
        _away_name = k["away_name"]
        _date = k["date"]

        print _id

        sql = "UPDATE nba_game set id2 = %s where home_name = %s and away_name = %s and date = %s "
        c_update_game.execute(sql,(_id, _home_name, _away_name, _date))



        connection.commit()
    c_update_game.close()
    connection.close()