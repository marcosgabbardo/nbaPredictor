import datetime
from lib import nba_game, nba_statistics



# this scripts was used to learn python.

# import games scraping from basketbal reference website
# http://www.basketball-reference.com/leagues/NBA_2017_games.html
nba_game.gameimporter('2017','january')

# generate a lot os statistics from analitics games
nba_statistics.statisticGenerator('NBA','2017')
nba_statistics.streakcalc('NBA','2017')


data = datetime.date(2017, 1, 7)

# import play by play games from a specific date
nba_game.playbyplay(data)

# generate a lot os statistics from play by play, quarter by quarter..
nba_statistics.fgquarter()
nba_statistics.toquarter()
nba_statistics.rbquarter()

# some features to control and input handicaps, odds and chance (%) of victory of home team
# this feature is IN CONSTRUCTION
nba_game.handicap('2017-01-09')
nba_game.idformater('2017-01-09')
nba_game.ponderation('2017-01-09')

