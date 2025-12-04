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
-- Table structure for table `nba_game`
--

DROP TABLE IF EXISTS `nba_game`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `nba_game` (
  `date` date DEFAULT NULL,
  `home_point` int(3) DEFAULT NULL,
  `away_point` int(3) DEFAULT NULL,
  `home_name` varchar(50) DEFAULT NULL,
  `away_name` varchar(50) DEFAULT NULL,
  `home_p1` int(3) DEFAULT NULL,
  `home_p2` int(3) DEFAULT NULL,
  `home_p3` int(3) DEFAULT NULL,
  `home_p4` int(3) DEFAULT NULL,
  `away_p1` int(3) DEFAULT NULL,
  `away_p2` int(3) DEFAULT NULL,
  `away_p3` int(3) DEFAULT NULL,
  `away_p4` int(3) DEFAULT NULL,
  `home_pace` decimal(7,3) DEFAULT NULL,
  `home_efg` decimal(7,3) DEFAULT NULL,
  `home_tov` decimal(7,3) DEFAULT NULL,
  `home_orb` decimal(7,3) DEFAULT NULL,
  `home_ftfga` decimal(7,3) DEFAULT NULL,
  `home_ortg` decimal(7,3) DEFAULT NULL,
  `away_pace` decimal(7,3) DEFAULT NULL,
  `away_efg` decimal(7,3) DEFAULT NULL,
  `away_tov` decimal(7,3) DEFAULT NULL,
  `away_orb` decimal(7,3) DEFAULT NULL,
  `away_ftfga` decimal(7,3) DEFAULT NULL,
  `away_ortg` decimal(7,3) DEFAULT NULL,
  `id2` varchar(50) DEFAULT NULL,
  `overtime` varchar(2) DEFAULT NULL,
  `season` varchar(10) DEFAULT NULL,
  KEY `idx_date` (`date`),
  KEY `idx_id2` (`id2`),
  KEY `idx_season_nbagame` (`season`),
  KEY `idxhomename` (`home_name`),
  KEY `idxawayname` (`away_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `nba_playbyplay`
--

DROP TABLE IF EXISTS `nba_playbyplay`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `nba_playbyplay` (
  `id` varchar(50) DEFAULT NULL,
  `quarter` varchar(2) DEFAULT NULL,
  `duration` decimal(10,2) DEFAULT NULL,
  `home_comment` varchar(4000) DEFAULT NULL,
  `home_score` int(2) DEFAULT NULL,
  `away_comment` varchar(4000) DEFAULT NULL,
  `away_score` int(2) DEFAULT NULL,
  KEY `edx_id` (`id`),
  KEY `idx_quarter` (`quarter`),
  KEY `idx_duration` (`duration`),
  KEY `idx_composite` (`id`,`quarter`,`duration`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `nba_ponderation`
--

DROP TABLE IF EXISTS `nba_ponderation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `nba_ponderation` (
  `id` varchar(30) NOT NULL DEFAULT '',
  `date` date DEFAULT NULL,
  `home_name` varchar(50) DEFAULT NULL,
  `away_name` varchar(50) DEFAULT NULL,
  `value` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `nba_team_history`
--

DROP TABLE IF EXISTS `nba_team_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `nba_team_history` (
  `team_name` varchar(50) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `last1` int(10) DEFAULT NULL,
  `last3` int(10) DEFAULT NULL,
  `last5` int(10) DEFAULT NULL,
  `last10` int(10) DEFAULT NULL,
  `pointavg1` decimal(10,2) DEFAULT NULL,
  `pointavg3` decimal(10,2) DEFAULT NULL,
  `pointavg5` decimal(10,2) DEFAULT NULL,
  `pointavg10` decimal(10,2) DEFAULT NULL,
  `pointavg1a` decimal(10,2) DEFAULT NULL,
  `pointavg` decimal(10,2) DEFAULT NULL,
  `pointavga` decimal(10,2) DEFAULT NULL,
  `game` int(10) DEFAULT NULL,
  `win` int(10) DEFAULT NULL,
  `day_diff` int(3) DEFAULT NULL,
  `pace_avg` decimal(10,2) DEFAULT NULL,
  `efg_avg` decimal(10,2) DEFAULT NULL,
  `tov_avg` decimal(10,2) DEFAULT NULL,
  `orb_avg` decimal(10,2) DEFAULT NULL,
  `ftfga_avg` decimal(10,2) DEFAULT NULL,
  `ortg_avg` decimal(10,2) DEFAULT NULL,
  `win_streak` int(3) DEFAULT NULL,
  `loss_streak` int(3) DEFAULT NULL,
  `season` int(4) DEFAULT NULL,
  `p1_avg` decimal(10,3) DEFAULT NULL,
  `p2_avg` decimal(10,3) DEFAULT NULL,
  `p3_avg` decimal(10,3) DEFAULT NULL,
  `p4_avg` decimal(10,3) DEFAULT NULL,
  KEY `idx_team_name` (`team_name`),
  KEY `idx_date_hist` (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `odd`
--

DROP TABLE IF EXISTS `odd`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `odd` (
  `id` varchar(30) NOT NULL DEFAULT '',
  `date` date DEFAULT NULL,
  `type` varchar(50) DEFAULT NULL,
  `handicap` decimal(10,2) DEFAULT NULL,
  `bet` char(1) DEFAULT NULL,
  `odd` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-01-09 10:40:19
