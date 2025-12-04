# Database Migrations

## drop_unused_fields.sql

**Date:** 2025-12-04
**Status:** Ready to apply

### Summary
Removes 62 unused database fields that were part of the legacy Python 2 statistics system but are not used by the current Python 3 codebase.

**IMPORTANT:** This migration also fixes a critical bug in `claude_predictor.py` that was attempting to read fields that were never populated.

### Affected Tables

#### `nba_game` (24 fields removed)
- **Field Goal Percentages (8 fields):** `fg_home_p1-4`, `fg_away_p1-4`
  - These were calculated from play-by-play data using `lib/nba_statistics.py::fgquarter()`
  - Not used in current system

- **Turnovers by Quarter (8 fields):** `to_home_p1-4`, `to_away_p1-4`
  - These were calculated from play-by-play data using `lib/nba_statistics.py::toquarter()`
  - Not used in current system

- **Rebounds by Quarter (8 fields):** `rb_home_p1-4`, `rb_away_p1-4`
  - These were calculated from play-by-play data using `lib/nba_statistics.py::rbquarter()`
  - Not used in current system

#### `nba_playbyplay` (2 fields removed)
- **Cumulative Scores:** `home_cumulative_score`, `away_cumulative_score`
  - These fields were defined in the schema but never populated
  - Not used in current system

#### `nba_team_history` (36 fields removed)
- **Points Against Aggregates (3 fields):** `pointavg3a`, `pointavg5a`, `pointavg10a`
  - Never calculated by `src/nba_predictor/utils/statistics.py`
  - `claude_predictor.py` was incorrectly trying to read these

- **Advanced Metrics - Last 1 Game (6 fields):** `pace_avg1`, `efg_avg1`, `tov_avg1`, `orb_avg1`, `ftfga_avg1`, `ortg_avg1`
  - Never calculated by current system
  - `claude_predictor.py` was incorrectly trying to read these instead of `*_avg` fields

- **Advanced Metrics - Last 3 Games (6 fields):** `pace_avg3`, `efg_avg3`, `tov_avg3`, `orb_avg3`, `ftfga_avg3`, `ortg_avg3`
  - Never calculated by current system

- **Advanced Metrics - Last 5 Games (6 fields):** `pace_avg5`, `efg_avg5`, `tov_avg5`, `orb_avg5`, `ftfga_avg5`, `ortg_avg5`
  - Never calculated by current system

- **Advanced Metrics - Last 10 Games (6 fields):** `pace_avg10`, `efg_avg10`, `tov_avg10`, `orb_avg10`, `ftfga_avg10`, `ortg_avg10`
  - Never calculated by current system

- **Quarter Averages - Last 5 (4 fields):** `p1_avg5`, `p2_avg5`, `p3_avg5`, `p4_avg5`
  - Never calculated by current system

- **Quarter Averages - Last 10 (4 fields):** `p1_avg10`, `p2_avg10`, `p3_avg10`, `p4_avg10`
  - Never calculated by current system

- **Overtime (1 field):** `overtime`
  - Never populated by current system

### How to Apply

**Option 1: Direct MySQL/MariaDB**
```bash
mysql -u your_user -p your_database < db/migrations/drop_unused_fields.sql
```

**Option 2: Via application (after running migration)**
The SQLAlchemy models in `src/nba_predictor/models/game.py` have been updated to match the new schema. If you recreate tables using:
```python
from nba_predictor.models import create_tables
create_tables()
```

The new tables will automatically be created without these fields.

### Verification

After applying the migration, verify with:
```sql
-- Should show 30 fields (down from 54)
DESCRIBE nba_game;

-- Should show 7 fields (down from 9)
DESCRIBE nba_playbyplay;

-- Should show 29 fields (down from 65)
DESCRIBE nba_team_history;
```

### Rollback

If you need to rollback this migration, you can restore the fields with:
```sql
-- Restore nba_game fields
ALTER TABLE `nba_game`
  ADD COLUMN `fg_home_p1` decimal(10,3) DEFAULT NULL,
  ADD COLUMN `fg_home_p2` decimal(10,3) DEFAULT NULL,
  -- ... (add remaining fields)
```

**Note:** However, these fields will be empty since the current system doesn't populate them.

### Bug Fix Included
This migration fixes a critical bug where `claude_predictor.py` was attempting to read fields that were never populated:
- Changed from `pace_avg1` → `pace_avg` (and all other advanced metrics)
- Changed from `pointavg3a/5a/10a` → only `pointavg1a` and `pointavga`

### Related Files Changed
- `src/nba_predictor/models/game.py` - Removed unused field definitions from Game and PlayByPlay
- `src/nba_predictor/models/team.py` - Removed 36 unused field definitions from TeamHistory
- `src/nba_predictor/prediction/claude_predictor.py` - Fixed to read correct fields that are actually populated
- `db/db_tables.sql` - Updated CREATE TABLE statements for all three tables
