# nbaPredictor (Python scraper)
Python scraping and repository for nba data and statistics based on basketball reference. 

DB folder contain all scripts from a MYSQL Dump to use as structure for scraped data.
* db_tables.sql - is all structure you will need to put scraped data.
* nba_teams_data.sql - is a table with all nba team and abrev names.

LIB folder contain all source code for scrap and save data
* nba_game.py - core script to scrap and save basic and analytic data from website.
* nba_statistics.py - core script to calculate some statistical indicators like averages and sums.
* nba_csvgenerator.py - under construcion (generate csv files for amazon machine learning).

TEST
* test_nba_server.py - some code to base your tests and understanding of nbaPredictor.
* amazonML.py - under construction, to use to comunicate with AWS and generate predictions.

OBS: This souces is only to learning python programming language and a lot of improvements will be necessary.
