# nbaPredictor (Python scraper)
Python scraping and repository for nba data and statistics based on basketball reference. This code is under havely developemnt.

<b>DB folder contain all scripts from a MYSQL Dump to use as structure for scraped data.</b>
* db_tables.sql - is all structure you will need to put scraped data.
* nba_teams_data.sql - is a table with all nba team and abrev names.

<b> LIB folder contain all source code for scrap and save data </b>
* nba_game.py - core script to scrap and save basic and analytic data from website.
* nba_statistics.py - core script to calculate some statistical indicators like averages and sums.
* nba_csvgenerator.py - under construcion (generate csv files for amazon machine learning).

<b> TEST </b>
* test_nba_server.py - some code to base your tests and understanding of nbaPredictor.
* amazonML.py - under construction, to use to comunicate with AWS and generate predictions.

<b> Data Structure </b>

* NBA_TEAM: table with all nba team names and abreviations.
* NBA_GAME: analytic game table with scores and game statistics.
* NBA_PLAYBYPLAY: analytic game table with play by play data.
* NBA_TEAM_HISTORY: table with processed data and statistics, turn by turn (day by day)... this table accumulates all data from previous games until last game and create a sintetic data information for the next game.
* NBA_PONDERATION: under construction, will be used for user guesses.
* ODD: under construction, will save all handicaps and odds from some sportbet websites to use in comparation with your data.

<b> How to use </b>
 - With nbaPredictor you can test your strategies for handicaping. 

Ex:
1. First import all data from last 3 season.
2. Create a sql to select and create a handicap prevision indicator, like this one:

```sql
SELECT 
    nba_game.id2,
    nba_game.season,
    nba_game.date,
    home.team_name home_team_name,
    away.team_name away_team_name,
    ROUND(((((away.efg_avg - home.efg_avg) * 100 * 1.5 + 
    (away.ftfga_avg - home.ftfga_avg) * 100 * 0.3 + 
    (away.tov_avg - home.tov_avg) * - 1.5 + 
    (away.orb_avg - home.orb_avg) * 0.5) * 1.16 + 
    (away.day_diff - home.day_diff) * 0.5 + 
    (away.win_streak - home.win_streak) * - 0.1 + 
    (away.loss_streak - home.loss_streak) * 0.15 + 
    (away.win - home.win) * 0.15 + 
    (away.pointavg - home.pointavg) * - 0.14 + 
    (away.pointavg10 - home.pointavg10) * - 0.02 + 
    (away.last5 - home.last5) * 0.15 + 
    (away.last3 - home.last3) * - 0.1 + 
    (away.last10 - home.last10) * 0.15 + 
    (away.last1 - home.last1) * - 0.6 + 
    (away.efg_avg1 - home.efg_avg1) * 100 * - 0.02 + 
    (away.tov_avg1 - home.tov_avg1) * 0.13 + 
    (away.orb_avg1 - home.orb_avg1) * - 0.01 + 
    (away.ftfga_avg1 - home.ftfga_avg1) * - 0.4 + 
    (away.pointavg1a - home.pointavg1a) * - 0.04 + 
    (away.ortg_avg3 - home.ortg_avg3) * - 0.03 + 
    (away.ortg_avg5 - home.ortg_avg5) * - 0.03 + 
    (away.ortg_avg10 - home.ortg_avg10) * - 0.02 + 
	(away.ortg_avg - home.ortg_avg) * + 0.05  
	)) + 2,
            0) predictor,
  --  odd.handicap,        
  --  nba_ponderation.value ponderation,
    (home.pointavga - home.pointavg) media_diff_pontos,
    (nba_game.away_point - nba_game.home_point) decisor
FROM
    nba_game, -- left outer join odd on (odd.id = nba_game.id2),
    nba_team_history home,
    nba_team_history away
   -- ,nba_ponderation
WHERE
    nba_game.home_name = home.team_name
        AND nba_game.away_name = away.team_name
        AND home.date = nba_game.date
        AND away.date = nba_game.date
        AND nba_game.season IN (2017)
        AND nba_game.date = '2017-01-07'
        AND home.efg_avg10 <> 0
      --  AND nba_ponderation.date = nba_game.date
      --  AND nba_ponderation.home_name = home.team_name
      --  AND nba_ponderation.away_name = away.team_name
    --  AND nba_ponderation.value > 60
ORDER BY nba_game.date
```

Note that you can create your own indicator and compare in a simple sql with decisor (real result of handicap), and evaluate with a standard deviation analisys, remember, smaller standard deviation between decisor and prediction better is your indicator. (handicap predictor by sportbet houses have am average standard deviation of 12 points in handicap full-time scores)


OBS: This souces is only to learning python programming language and a lot of improvements will be necessary.
