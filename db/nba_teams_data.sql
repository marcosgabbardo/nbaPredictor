-- MySQL dump 10.13  Distrib 5.6.24, for osx10.8 (x86_64)
--
-- Host: localhost    Database: sportbet
-- ------------------------------------------------------
-- Server version	5.6.26

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `nba_team`
--

DROP TABLE IF EXISTS `nba_team`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `nba_team` (
  `name` varchar(50) DEFAULT NULL,
  `type` varchar(20) DEFAULT NULL,
  `abrev` varchar(3) DEFAULT NULL,
  KEY `idx_name` (`name`),
  KEY `idx_type` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `nba_team`
--

LOCK TABLES `nba_team` WRITE;
/*!40000 ALTER TABLE `nba_team` DISABLE KEYS */;
INSERT INTO `nba_team` VALUES ('Atlanta Hawks','NBA','ATL'),('Chicago Bulls','NBA','CHI'),('Golden State Warriors','NBA','GSW'),('Boston Celtics','NBA','BOS'),('Brooklyn Nets','NBA','BRK'),('Detroit Pistons','NBA','DET'),('Houston Rockets','NBA','HOU'),('Los Angeles Lakers','NBA','LAL'),('Memphis Grizzlies','NBA','MEM'),('Miami Heat','NBA','MIA'),('Milwaukee Bucks','NBA','MIL'),('Oklahoma City Thunder','NBA','OKC'),('Orlando Magic','NBA','ORL'),('Phoenix Suns','NBA','PHO'),('Portland Trail Blazers','NBA','POR'),('Sacramento Kings','NBA','SAC'),('Toronto Raptors','NBA','TOR'),('Indiana Pacers','NBA','IND'),('Los Angeles Clippers','NBA','LAC'),('New York Knicks','NBA','NYK'),('Cleveland Cavaliers','NBA','CLE'),('Denver Nuggets','NBA','DEN'),('Philadelphia 76ers','NBA','PHI'),('San Antonio Spurs','NBA','SAS'),('New Orleans Pelicans','NBA','NOP'),('Washington Wizards','NBA','WAS'),('Charlotte Hornets','NBA','CHO'),('Minnesota Timberwolves','NBA','MIN'),('Dallas Mavericks','NBA','DAL'),('Utah Jazz','NBA','UTA');
/*!40000 ALTER TABLE `nba_team` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-01-09 10:41:30
