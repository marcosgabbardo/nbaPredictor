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
-- Summary:
-- - Dropped 24 fields from nba_game
-- - Dropped 2 fields from nba_playbyplay
-- - Total: 26 unused fields removed
-- ============================================================
