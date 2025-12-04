# Database Migrations

## drop_unused_fields.sql

**Date:** 2025-12-04
**Status:** Ready to apply

### Summary
Removes 26 unused database fields that were part of the legacy Python 2 statistics system but are not used by the current Python 3 codebase.

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

### Related Files Changed
- `src/nba_predictor/models/game.py` - Removed field definitions
- `db/db_tables.sql` - Updated CREATE TABLE statements
