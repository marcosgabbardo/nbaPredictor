# 🏀 NBA Predictor 2.0

> **AI-powered NBA game prediction system** - Completely revitalized with modern Python, SQLAlchemy ORM, and Claude AI integration

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🌟 What's New in Version 2.0

This is a **complete revitalization** of the NBA Predictor project, rebuilt from the ground up with modern technologies and best practices:

- ✅ **Migrated from Python 2.7 to Python 3.11+**
- ✅ **SQLAlchemy ORM** - No more raw SQL, proper database abstraction
- ✅ **Structured Logging** - JSON logs with full traceability using structlog
- ✅ **Claude AI Integration** - Replaced deprecated AWS ML with state-of-the-art AI
- ✅ **Robust Error Handling** - Retry logic, timeouts, comprehensive exception handling
- ✅ **Modern Configuration** - Environment variables with Pydantic validation
- ✅ **Type Hints** - Full type annotations for better IDE support
- ✅ **Modular Architecture** - Clean separation of concerns
- ✅ **CLI Interface** - User-friendly command-line interface

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Features

### Data Collection
- **Automated Web Scraping** from Basketball Reference
- **Image-Based Lineup Scraper** - NEW! Extract lineup data from screenshots using Claude Vision API
- **Game Data**: Scores, quarter-by-quarter breakdowns, basic stats
- **Advanced Metrics**: Pace, eFG%, TOV%, ORB%, FT/FGA, ORtg
- **Play-by-Play Data**: Detailed game progression
- **Daily Lineups**: Starting lineups and injury reports
- **Retry Logic**: Automatic retry on failures with exponential backoff
- **Rate Limiting**: Respectful scraping with delays

### Statistical Analysis
- **Rolling Averages**: Calculate team performance over 1, 3, 5, and 10 game windows
- **Win/Loss Streaks**: Track team momentum
- **Advanced Analytics**: Comprehensive offensive and defensive metrics
- **Historical Tracking**: Time-series data for trend analysis
- **Quarter-Level Analysis**: Performance breakdown by quarter

### AI-Powered Predictions
- **Claude AI Integration**: Leverages Anthropic's Claude Sonnet for predictions
- **Context-Aware Analysis**: Considers recent form, advanced metrics, rest factors
- **Confidence Scores**: Get probability estimates for predictions
- **Detailed Reasoning**: Understand why the AI made its prediction
- **Batch Predictions**: Predict multiple games at once
- **Accuracy Tracking**: Analyze historical prediction performance

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Interface                        │
│                    (User Commands)                           │
└────────────────┬────────────────────────────┬────────────────┘
                 │                            │
        ┌────────▼─────────┐       ┌─────────▼────────┐
        │     Scraper      │       │    Predictor     │
        │  (Data Import)   │       │  (Claude AI)     │
        └────────┬─────────┘       └─────────┬────────┘
                 │                            │
                 │         ┌──────────────────┘
                 │         │
        ┌────────▼─────────▼─────┐
        │   Statistics Engine    │
        │  (Team Performance)    │
        └────────┬───────────────┘
                 │
        ┌────────▼───────────────┐
        │   SQLAlchemy ORM       │
        │   (Data Models)        │
        └────────┬───────────────┘
                 │
        ┌────────▼───────────────┐
        │    MySQL Database      │
        │  (Historical Data)     │
        └────────────────────────┘
```

### Core Components

#### 1. **Scraper Module** (`src/nba_predictor/scraper/`)
- Fetches data from Basketball Reference
- Robust error handling and retry logic
- Respects rate limits
- Parses HTML with BeautifulSoup

#### 2. **Models Module** (`src/nba_predictor/models/`)
- SQLAlchemy ORM models
- Type-safe database operations
- Automatic schema migration support
- Context managers for database sessions

#### 3. **Statistics Module** (`src/nba_predictor/utils/`)
- Calculates rolling averages
- Tracks win/loss streaks
- Computes advanced metrics
- Generates team historical data

#### 4. **Prediction Module** (`src/nba_predictor/prediction/`)
- Claude AI integration
- Context preparation for AI analysis
- Result parsing and validation
- Accuracy tracking

#### 5. **Core Module** (`src/nba_predictor/core/`)
- Configuration management (Pydantic)
- Structured logging (structlog)
- Application settings
- Environment variable handling

## 📦 Installation

### Prerequisites

- **Python 3.11+**
- **MySQL 5.7+** or **MariaDB 10.3+**
- **Anthropic API Key** (for predictions)

### Step 1: Clone the Repository

```bash
git clone https://github.com/marcosgabbardo/nbaPredictor.git
cd nbaPredictor
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

### Step 4: Set Up Database

```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE sportbet CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Import team data
mysql -u root -p sportbet < db/nba_teams_data.sql
```

### Step 5: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

Required environment variables:
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`: Database credentials

### Step 6: Initialize Database

```bash
python3 -m nba_predictor.cli init
```

## ⚙️ Configuration

Configuration is managed through environment variables. See `.env.example` for all available options:

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=sportbet

# Scraper
SCRAPER_TIMEOUT=30
SCRAPER_RETRY_ATTEMPTS=3

# Anthropic Claude
ANTHROPIC_API_KEY=your_api_key_here

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## 🎯 Usage

### Command-Line Interface

The CLI provides all functionality through simple commands:

```bash
# Show help
python3 -m nba_predictor.cli --help
```

### 1. Scrape Game Data

```bash
# Scrape games for a specific month
python3 -m nba_predictor.cli scrape-games 2024 january

# Scrape multiple months at once
python3 -m nba_predictor.cli scrape-games 2024 october november december

# Scrape entire season (multiple months)
python3 -m nba_predictor.cli scrape-games 2024 october november december january february march april may june

# Scrape play-by-play data for a date
python3 -m nba_predictor.cli scrape-pbp 2024-01-15
```

### 2. Import Lineups from Screenshots (NEW!)

The new image-based lineup scraper extracts lineup data from screenshots using Claude Vision API.
This is more reliable than HTML scraping and works with any lineup source (RotoWire, Basketball Monster, etc.).

```bash
# Import lineups from a single screenshot
python import_lineup_from_image.py lineup_screenshot.png

# Import lineups for a specific date
python import_lineup_from_image.py lineup_screenshot.png 2024-12-05

# Import from multiple screenshots
python import_lineup_from_image.py game1.png game2.png game3.png

# Test the scraper without saving to database
python test_image_scraper.py lineup_screenshot.png
```

**How to use:**
1. Take a screenshot of NBA lineups from RotoWire, Basketball Monster, or any source
2. Save as PNG or JPEG
3. Run the import script with your screenshot path
4. Data is automatically extracted and saved to the database

See [docs/IMAGE_LINEUP_SCRAPER.md](docs/IMAGE_LINEUP_SCRAPER.md) for detailed documentation.

### 3. Calculate Statistics

```bash
# Generate team statistics for a season
python3 -m nba_predictor.cli calculate-stats 2024
```

### 4. Make Predictions

```bash
# Predict a specific game
python3 -m nba_predictor.cli predict "Los Angeles Lakers" "Boston Celtics" 2024-01-15

# Predict all games for a date
python3 -m nba_predictor.cli predict-date 2024-01-15
```

Example output:
```
🏀 Predicting: Los Angeles Lakers vs Boston Celtics on 2024-01-15

🏆 Predicted Winner: Los Angeles Lakers
📊 Confidence: 68%
📈 Predicted Score: 112 - 108

🔑 Key Factors:
   • Lakers on 3-game win streak with strong offensive rating
   • Home court advantage (Lakers playing at home)
   • Celtics playing second game of back-to-back

📝 Analysis:
   The Lakers enter this matchup with momentum, having won their last 3 games
   with an average margin of 8.5 points. Their offensive rating of 118.2 over
   the last 5 games is significantly higher than Boston's defensive rating...
```

### 4. Analyze Accuracy

```bash
# Check prediction accuracy for a season
python3 -m nba_predictor.cli analyze-accuracy 2024
```

### Typical Workflow

```bash
# 1. Scrape data for the season
# Option A: Scrape all months at once (recommended for efficiency)
python3 -m nba_predictor.cli scrape-games 2024 october november december january february march april may june

# Option B: Scrape month by month in a loop
for month in october november december january february march april may june; do
    python3 -m nba_predictor.cli scrape-games 2024 $month
done

# Option C: Scrape specific months range
python3 -m nba_predictor.cli scrape-games 2024 january february march

# 2. Calculate statistics
python3 -m nba_predictor.cli calculate-stats 2024

# 3. Make predictions for upcoming games
python3 -m nba_predictor.cli predict-date 2024-01-20

# 4. Analyze accuracy
python3 -m nba_predictor.cli analyze-accuracy 2024
```

## 📁 Project Structure

```
nbaPredictor/
├── src/nba_predictor/          # Main package
│   ├── core/                   # Core functionality
│   │   ├── config.py          # Configuration management
│   │   └── logger.py          # Structured logging
│   ├── models/                 # Database models
│   │   ├── database.py        # SQLAlchemy setup
│   │   ├── game.py            # Game models
│   │   └── team.py            # Team models
│   ├── scraper/                # Web scraping
│   │   └── scraper.py         # Basketball Reference scraper
│   ├── prediction/             # AI predictions
│   │   └── claude_predictor.py # Claude AI integration
│   ├── utils/                  # Utilities
│   │   └── statistics.py      # Statistical calculations
│   ├── cli.py                  # Command-line interface
│   └── __main__.py            # Entry point
├── tests/                      # Test suite
├── db/                         # Database schemas
│   ├── db_tables.sql          # Table definitions
│   └── nba_teams_data.sql     # Team reference data
├── logs/                       # Application logs
├── data/                       # Data files
├── requirements.txt            # Dependencies
├── pyproject.toml             # Project configuration
├── .env.example               # Environment template
└── README.md                  # This file
```

## 🔍 How It Works

### 1. Data Collection

The scraper fetches data from [Basketball Reference](https://www.basketball-reference.com/):

```python
from nba_predictor.scraper import BasketballReferenceScraper

scraper = BasketballReferenceScraper()
# Scrape a single month
scraper.import_games("2024", "january")

# Or scrape multiple months at once
for month in ["october", "november", "december"]:
    scraper.import_games("2024", month)
```

Data collected includes:
- Game scores (total and by quarter)
- Four Factors: Pace, eFG%, TOV%, ORB%, FT/FGA, ORtg
- Play-by-play events with timestamps

### 2. Statistical Analysis

The statistics engine calculates rolling metrics:

```python
from nba_predictor.utils.statistics import StatisticsCalculator

calculator = StatisticsCalculator()
calculator.generate_team_statistics("2024")
calculator.calculate_streaks("2024")
```

Metrics include:
- Win/loss records over different windows (1, 3, 5, 10 games)
- Point averages (offensive and defensive)
- Advanced efficiency metrics
- Momentum indicators (streaks)
- Rest factors (days between games)

### 3. AI-Powered Predictions

Claude AI analyzes team statistics and makes predictions:

```python
from nba_predictor.prediction import ClaudePredictor

predictor = ClaudePredictor()
prediction = predictor.predict_game("Lakers", "Celtics", date(2024, 1, 15))
```

The AI considers:
- **Recent Form**: Last 1, 3, 5, 10 games performance
- **Offensive Efficiency**: Points scored, shooting percentages
- **Defensive Efficiency**: Points allowed, opponent shooting
- **Advanced Metrics**: Pace, turnover rates, rebounding
- **Momentum**: Win/loss streaks
- **Rest**: Days since last game
- **Home Court**: Advantage factor

### 4. Data Models

#### Game Model
```python
class Game(Base):
    date: date
    home_name: str
    away_name: str
    home_point: int
    away_point: int
    # ... advanced stats
```

#### Team History Model
```python
class TeamHistory(Base):
    team_name: str
    date: date
    last1, last3, last5, last10: int  # Wins in windows
    pointavg1, pointavg3, ...: Decimal  # Scoring averages
    pace_avg, efg_avg, ...: Decimal  # Advanced metrics
    win_streak, loss_streak: int  # Momentum
```

## 🛠️ Development

### Code Quality

The project uses modern Python tooling:

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/

# Run tests
pytest
```

### Adding New Features

1. **New Scraper**: Extend `BasketballReferenceScraper`
2. **New Metric**: Add to `StatisticsCalculator`
3. **New Model**: Create in `src/nba_predictor/models/`
4. **New CLI Command**: Add to `src/nba_predictor/cli.py`

### Database Migrations

For schema changes, use Alembic:

```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

## 📊 Database Schema

### Tables

- **`nba_team`**: Team reference data (30 NBA teams)
- **`nba_game`**: Game results and statistics
- **`nba_playbyplay`**: Detailed play-by-play events
- **`nba_team_history`**: Team performance time series (60+ metrics per date)

### Key Relationships

```
Team (1) ─────── (*) TeamHistory
            ↓
Game (1) ─────── (*) PlayByPlay
```

## 🔒 Security

- **Environment Variables**: Sensitive data never hardcoded
- **SQL Injection Protection**: ORM prevents SQL injection
- **API Key Management**: Secure credential storage
- **Rate Limiting**: Prevents overwhelming external services

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check MySQL is running
sudo systemctl status mysql

# Verify credentials in .env
mysql -u $DB_USER -p$DB_PASSWORD -h $DB_HOST
```

**Import Errors**
```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Scraping Failures**
```bash
# Check internet connection
ping www.basketball-reference.com

# Increase timeout in .env
SCRAPER_TIMEOUT=60
```

**API Errors**
```bash
# Verify API key
echo $ANTHROPIC_API_KEY

# Check API quota
# Visit: https://console.anthropic.com/
```

## 📈 Performance

- **Scraping**: ~2-3 seconds per game
- **Statistics**: ~1 minute for full season (30 teams)
- **Prediction**: ~2-5 seconds per game (Claude API call)
- **Database**: Optimized indexes for fast queries

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Check coverage
pytest --cov=nba_predictor --cov-report=html
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Basketball Reference** for providing comprehensive NBA data
- **Anthropic** for the Claude AI API
- **SQLAlchemy** for excellent ORM capabilities
- **structlog** for structured logging

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/marcosgabbardo/nbaPredictor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/marcosgabbardo/nbaPredictor/discussions)

## 🗺️ Roadmap

- [ ] Web dashboard for visualizations
- [ ] Real-time game tracking
- [ ] Player-level statistics
- [ ] Multi-model ensemble predictions
- [ ] Historical backtest framework
- [ ] REST API for predictions
- [ ] Docker containerization
- [ ] Automated daily predictions

---

**Made with ❤️ and 🏀 by the NBA Predictor Team**

*Revitalized and modernized in 2024*
