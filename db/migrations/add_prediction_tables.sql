-- Migration: Add AI prediction tables
-- Date: 2025-12-05
-- Description: Creates tables to store AI predictions for future evaluation
--
-- IMPORTANT: This script is compatible with MySQL 5.7+ and MariaDB 10.0+

-- ============================================================
-- Table: nba_prediction
-- Purpose: Store AI predictions for NBA games
-- ============================================================

CREATE TABLE IF NOT EXISTS `nba_prediction` (
  `id` int(11) NOT NULL AUTO_INCREMENT,

  -- Game reference
  `game_id` varchar(50) DEFAULT NULL,
  `game_date` date NOT NULL,
  `season` varchar(10) DEFAULT NULL,

  -- Teams
  `home_team` varchar(50) NOT NULL,
  `away_team` varchar(50) NOT NULL,

  -- Prediction details
  `predicted_winner` varchar(50) NOT NULL,
  `confidence` decimal(5,2) NOT NULL,
  `predicted_home_score` int(11) NOT NULL,
  `predicted_away_score` int(11) NOT NULL,

  -- Analysis
  `analysis` text NOT NULL,

  -- Metadata
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `model_version` varchar(50) DEFAULT NULL,

  -- Actual results (to be filled after the game)
  `actual_winner` varchar(50) DEFAULT NULL,
  `actual_home_score` int(11) DEFAULT NULL,
  `actual_away_score` int(11) DEFAULT NULL,
  `is_correct` tinyint(1) DEFAULT NULL,

  PRIMARY KEY (`id`),
  KEY `idx_game_id` (`game_id`),
  KEY `idx_game_date` (`game_date`),
  KEY `idx_season` (`season`),
  KEY `idx_home_team` (`home_team`),
  KEY `idx_away_team` (`away_team`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Table: nba_prediction_factor
-- Purpose: Store key factors for each prediction
-- ============================================================

CREATE TABLE IF NOT EXISTS `nba_prediction_factor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `prediction_id` int(11) NOT NULL,
  `factor` text NOT NULL,
  `order` int(11) NOT NULL DEFAULT 0,

  PRIMARY KEY (`id`),
  KEY `idx_prediction_id` (`prediction_id`),
  CONSTRAINT `fk_prediction_factor_prediction`
    FOREIGN KEY (`prediction_id`)
    REFERENCES `nba_prediction` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Summary:
-- - Created nba_prediction table for AI predictions
-- - Created nba_prediction_factor table for prediction factors
-- - Added indexes for efficient querying
-- - Added foreign key constraint for data integrity
-- ============================================================
