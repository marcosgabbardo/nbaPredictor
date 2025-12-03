# 🚀 Quick Start Guide

Get up and running with NBA Predictor in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- MySQL 5.7+ or MariaDB 10.3+
- Anthropic API key ([get one here](https://console.anthropic.com/))

## Installation

### 1. Clone and Validate

```bash
git clone https://github.com/marcosgabbardo/nbaPredictor.git
cd nbaPredictor

# Validate code before installing dependencies
python3 validate.py
```

You should see:
```
✅ All 16 Python files validated successfully!
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Database

```bash
# Create MySQL database
mysql -u root -p
```

```sql
CREATE DATABASE sportbet CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your settings
nano .env  # or your preferred editor
```

**Required settings in `.env`**:
```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=sportbet

# Anthropic Claude API
ANTHROPIC_API_KEY=your_api_key_here
```

### 5. Initialize Database

```bash
# Create tables
python -m nba_predictor.cli init
```

### 6. Import Team Data

```bash
# Import NBA teams reference data
mysql -u root -p sportbet < db/nba_teams_data.sql
```

## Basic Usage

### Scrape Game Data

```bash
# Scrape games for a specific month
python -m nba_predictor.cli scrape-games 2024 january

# Scrape play-by-play data
python -m nba_predictor.cli scrape-pbp 2024-01-15
```

### Calculate Statistics

```bash
# Generate team statistics for the season
python -m nba_predictor.cli calculate-stats 2024
```

### Make Predictions

```bash
# Predict a specific game
python -m nba_predictor.cli predict "Los Angeles Lakers" "Boston Celtics" 2024-01-20

# Predict all games for a date
python -m nba_predictor.cli predict-date 2024-01-20
```

### Analyze Accuracy

```bash
# Check prediction accuracy (uses API credits)
python -m nba_predictor.cli analyze-accuracy 2024
```

## Typical Workflow

```bash
# 1. Scrape historical data
for month in october november december january; do
    python -m nba_predictor.cli scrape-games 2024 $month
done

# 2. Calculate statistics
python -m nba_predictor.cli calculate-stats 2024

# 3. Make predictions for upcoming games
python -m nba_predictor.cli predict-date 2024-01-25
```

## Example Output

```
🏀 Predicting: Los Angeles Lakers vs Boston Celtics on 2024-01-20

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

## Troubleshooting

### "No module named 'nba_predictor'"

Make sure you're in the virtual environment:
```bash
source venv/bin/activate
```

### "Database connection failed"

Check your `.env` file has correct credentials:
```bash
mysql -u $DB_USER -p$DB_PASSWORD -h $DB_HOST
```

### "Anthropic API error"

Verify your API key:
```bash
echo $ANTHROPIC_API_KEY
```

Get a new one at: https://console.anthropic.com/

## Next Steps

- 📚 Read the full [README.md](README.md) for detailed documentation
- 🔍 Check [VALIDATION_REPORT.md](VALIDATION_REPORT.md) for code quality details
- 🤝 See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- 📋 View [CHANGELOG.md](CHANGELOG.md) for version history

## Support

- **Issues**: [GitHub Issues](https://github.com/marcosgabbardo/nbaPredictor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/marcosgabbardo/nbaPredictor/discussions)

---

**Happy Predicting! 🏀**
