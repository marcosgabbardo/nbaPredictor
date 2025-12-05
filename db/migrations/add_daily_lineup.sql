-- Migration: Add daily lineup table
-- Description: Store daily starting lineups and injury status from RotoWire
-- Date: 2025-12-05

CREATE TABLE IF NOT EXISTS nba_daily_lineup (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scrape_date DATE NOT NULL,
    game_date DATE NOT NULL,
    team_name VARCHAR(100) NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    position VARCHAR(10),
    status VARCHAR(50) NOT NULL,  -- e.g., 'Starter', 'OUT', 'Questionable', 'GTD', 'Probable', 'Doubtful'
    injury_description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_scrape_date (scrape_date),
    INDEX idx_game_date (game_date),
    INDEX idx_team_name (team_name),
    INDEX idx_player_name (player_name),
    INDEX idx_status (status),
    UNIQUE KEY unique_lineup_entry (scrape_date, game_date, team_name, player_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
