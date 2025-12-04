-- Migration: Drop unused fields from NBA tables
-- Date: 2025-12-04
-- Description: Removes 26 unused fields that were part of legacy Python 2 statistics system

-- These fields were populated by lib/nba_statistics.py (legacy Python 2 code)
-- but are not used by the current Python 3 system in src/nba_predictor/

-- ============================================================
-- Table: nba_game
-- Removing: Field Goal %, Turnovers, and Rebounds by quarter
-- ============================================================

-- Drop Field Goal percentage columns (8 fields)
ALTER TABLE `nba_game`
  DROP COLUMN IF EXISTS `fg_home_p1`,
  DROP COLUMN IF EXISTS `fg_home_p2`,
  DROP COLUMN IF EXISTS `fg_home_p3`,
  DROP COLUMN IF EXISTS `fg_home_p4`,
  DROP COLUMN IF EXISTS `fg_away_p1`,
  DROP COLUMN IF EXISTS `fg_away_p2`,
  DROP COLUMN IF EXISTS `fg_away_p3`,
  DROP COLUMN IF EXISTS `fg_away_p4`;

-- Drop Turnover columns (8 fields)
ALTER TABLE `nba_game`
  DROP COLUMN IF EXISTS `to_home_p1`,
  DROP COLUMN IF EXISTS `to_home_p2`,
  DROP COLUMN IF EXISTS `to_home_p3`,
  DROP COLUMN IF EXISTS `to_home_p4`,
  DROP COLUMN IF EXISTS `to_away_p1`,
  DROP COLUMN IF EXISTS `to_away_p2`,
  DROP COLUMN IF EXISTS `to_away_p3`,
  DROP COLUMN IF EXISTS `to_away_p4`;

-- Drop Rebound columns (8 fields)
ALTER TABLE `nba_game`
  DROP COLUMN IF EXISTS `rb_home_p1`,
  DROP COLUMN IF EXISTS `rb_home_p2`,
  DROP COLUMN IF EXISTS `rb_home_p3`,
  DROP COLUMN IF EXISTS `rb_home_p4`,
  DROP COLUMN IF EXISTS `rb_away_p1`,
  DROP COLUMN IF EXISTS `rb_away_p2`,
  DROP COLUMN IF EXISTS `rb_away_p3`,
  DROP COLUMN IF EXISTS `rb_away_p4`;

-- Drop index on fg_home_p1 that is no longer needed
ALTER TABLE `nba_game`
  DROP INDEX IF EXISTS `idx_fghomep1`;

-- ============================================================
-- Table: nba_playbyplay
-- Removing: Cumulative score fields (never populated)
-- ============================================================

ALTER TABLE `nba_playbyplay`
  DROP COLUMN IF EXISTS `home_cumulative_score`,
  DROP COLUMN IF EXISTS `away_cumulative_score`;

-- ============================================================
-- Table: nba_team_history
-- Removing: Unused aggregate fields and legacy statistics
-- ============================================================

-- Drop unused points against aggregates (3 fields)
ALTER TABLE `nba_team_history`
  DROP COLUMN IF EXISTS `pointavg3a`,
  DROP COLUMN IF EXISTS `pointavg5a`,
  DROP COLUMN IF EXISTS `pointavg10a`;

-- Drop advanced metrics for last 1 game (6 fields)
ALTER TABLE `nba_team_history`
  DROP COLUMN IF EXISTS `pace_avg1`,
  DROP COLUMN IF EXISTS `efg_avg1`,
  DROP COLUMN IF EXISTS `tov_avg1`,
  DROP COLUMN IF EXISTS `orb_avg1`,
  DROP COLUMN IF EXISTS `ftfga_avg1`,
  DROP COLUMN IF EXISTS `ortg_avg1`;

-- Drop advanced metrics for last 3 games (6 fields)
ALTER TABLE `nba_team_history`
  DROP COLUMN IF EXISTS `pace_avg3`,
  DROP COLUMN IF EXISTS `efg_avg3`,
  DROP COLUMN IF EXISTS `tov_avg3`,
  DROP COLUMN IF EXISTS `orb_avg3`,
  DROP COLUMN IF EXISTS `ftfga_avg3`,
  DROP COLUMN IF EXISTS `ortg_avg3`;

-- Drop advanced metrics for last 5 games (6 fields)
ALTER TABLE `nba_team_history`
  DROP COLUMN IF EXISTS `pace_avg5`,
  DROP COLUMN IF EXISTS `efg_avg5`,
  DROP COLUMN IF EXISTS `tov_avg5`,
  DROP COLUMN IF EXISTS `orb_avg5`,
  DROP COLUMN IF EXISTS `ftfga_avg5`,
  DROP COLUMN IF EXISTS `ortg_avg5`;

-- Drop advanced metrics for last 10 games (6 fields)
ALTER TABLE `nba_team_history`
  DROP COLUMN IF EXISTS `pace_avg10`,
  DROP COLUMN IF EXISTS `efg_avg10`,
  DROP COLUMN IF EXISTS `tov_avg10`,
  DROP COLUMN IF EXISTS `orb_avg10`,
  DROP COLUMN IF EXISTS `ftfga_avg10`,
  DROP COLUMN IF EXISTS `ortg_avg10`;

-- Drop quarter averages for last 5 games (4 fields)
ALTER TABLE `nba_team_history`
  DROP COLUMN IF EXISTS `p1_avg5`,
  DROP COLUMN IF EXISTS `p2_avg5`,
  DROP COLUMN IF EXISTS `p3_avg5`,
  DROP COLUMN IF EXISTS `p4_avg5`;

-- Drop quarter averages for last 10 games (4 fields)
ALTER TABLE `nba_team_history`
  DROP COLUMN IF EXISTS `p1_avg10`,
  DROP COLUMN IF EXISTS `p2_avg10`,
  DROP COLUMN IF EXISTS `p3_avg10`,
  DROP COLUMN IF EXISTS `p4_avg10`;

-- Drop overtime field (1 field)
ALTER TABLE `nba_team_history`
  DROP COLUMN IF EXISTS `overtime`;

-- ============================================================
-- Summary:
-- - Dropped 24 fields from nba_game
-- - Dropped 2 fields from nba_playbyplay
-- - Dropped 36 fields from nba_team_history
-- - Total: 62 unused fields removed
-- ============================================================
