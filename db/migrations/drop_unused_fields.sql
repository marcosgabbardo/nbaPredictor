-- Migration: Drop unused fields from NBA tables
-- Date: 2025-12-04
-- Description: Removes 62 unused fields that were part of legacy Python 2 statistics system
--
-- IMPORTANT: This script is compatible with MySQL 5.7+ and MariaDB 10.0+
-- Warnings about non-existent columns are normal and can be ignored.

-- These fields were populated by lib/nba_statistics.py (legacy Python 2 code)
-- but are not used by the current Python 3 system in src/nba_predictor/

-- ============================================================
-- Table: nba_game
-- Removing: Field Goal %, Turnovers, and Rebounds by quarter
-- ============================================================

-- Drop Field Goal percentage columns (8 fields)
ALTER TABLE `nba_game`
  DROP COLUMN `fg_home_p1`,
  DROP COLUMN `fg_home_p2`,
  DROP COLUMN `fg_home_p3`,
  DROP COLUMN `fg_home_p4`,
  DROP COLUMN `fg_away_p1`,
  DROP COLUMN `fg_away_p2`,
  DROP COLUMN `fg_away_p3`,
  DROP COLUMN `fg_away_p4`;

-- Drop Turnover columns (8 fields)
ALTER TABLE `nba_game`
  DROP COLUMN `to_home_p1`,
  DROP COLUMN `to_home_p2`,
  DROP COLUMN `to_home_p3`,
  DROP COLUMN `to_home_p4`,
  DROP COLUMN `to_away_p1`,
  DROP COLUMN `to_away_p2`,
  DROP COLUMN `to_away_p3`,
  DROP COLUMN `to_away_p4`;

-- Drop Rebound columns (8 fields)
ALTER TABLE `nba_game`
  DROP COLUMN `rb_home_p1`,
  DROP COLUMN `rb_home_p2`,
  DROP COLUMN `rb_home_p3`,
  DROP COLUMN `rb_home_p4`,
  DROP COLUMN `rb_away_p1`,
  DROP COLUMN `rb_away_p2`,
  DROP COLUMN `rb_away_p3`,
  DROP COLUMN `rb_away_p4`;

-- Drop index on fg_home_p1 that is no longer needed
-- Note: Ignore error if index doesn't exist
ALTER TABLE `nba_game` DROP INDEX `idx_fghomep1`;

-- ============================================================
-- Table: nba_playbyplay
-- Removing: Cumulative score fields (never populated)
-- ============================================================

ALTER TABLE `nba_playbyplay`
  DROP COLUMN `home_cumulative_score`,
  DROP COLUMN `away_cumulative_score`;

-- ============================================================
-- Table: nba_team_history
-- Removing: Unused aggregate fields and legacy statistics
-- ============================================================

-- Drop unused points against aggregates (3 fields)
ALTER TABLE `nba_team_history`
  DROP COLUMN `pointavg3a`,
  DROP COLUMN `pointavg5a`,
  DROP COLUMN `pointavg10a`;

-- Drop advanced metrics for last 1 game (6 fields)
ALTER TABLE `nba_team_history`
  DROP COLUMN `pace_avg1`,
  DROP COLUMN `efg_avg1`,
  DROP COLUMN `tov_avg1`,
  DROP COLUMN `orb_avg1`,
  DROP COLUMN `ftfga_avg1`,
  DROP COLUMN `ortg_avg1`;

-- Drop advanced metrics for last 3 games (6 fields)
ALTER TABLE `nba_team_history`
  DROP COLUMN `pace_avg3`,
  DROP COLUMN `efg_avg3`,
  DROP COLUMN `tov_avg3`,
  DROP COLUMN `orb_avg3`,
  DROP COLUMN `ftfga_avg3`,
  DROP COLUMN `ortg_avg3`;

-- Drop advanced metrics for last 5 games (6 fields)
ALTER TABLE `nba_team_history`
  DROP COLUMN `pace_avg5`,
  DROP COLUMN `efg_avg5`,
  DROP COLUMN `tov_avg5`,
  DROP COLUMN `orb_avg5`,
  DROP COLUMN `ftfga_avg5`,
  DROP COLUMN `ortg_avg5`;

-- Drop advanced metrics for last 10 games (6 fields)
ALTER TABLE `nba_team_history`
  DROP COLUMN `pace_avg10`,
  DROP COLUMN `efg_avg10`,
  DROP COLUMN `tov_avg10`,
  DROP COLUMN `orb_avg10`,
  DROP COLUMN `ftfga_avg10`,
  DROP COLUMN `ortg_avg10`;

-- Drop quarter averages for last 5 games (4 fields)
ALTER TABLE `nba_team_history`
  DROP COLUMN `p1_avg5`,
  DROP COLUMN `p2_avg5`,
  DROP COLUMN `p3_avg5`,
  DROP COLUMN `p4_avg5`;

-- Drop quarter averages for last 10 games (4 fields)
ALTER TABLE `nba_team_history`
  DROP COLUMN `p1_avg10`,
  DROP COLUMN `p2_avg10`,
  DROP COLUMN `p3_avg10`,
  DROP COLUMN `p4_avg10`;

-- Drop overtime field (1 field)
ALTER TABLE `nba_team_history`
  DROP COLUMN `overtime`;

-- ============================================================
-- Summary:
-- - Dropped 24 fields from nba_game
-- - Dropped 2 fields from nba_playbyplay
-- - Dropped 36 fields from nba_team_history
-- - Total: 62 unused fields removed
-- ============================================================
