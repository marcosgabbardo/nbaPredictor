# Image-Based Lineup Scraper

## Overview

The Image-Based Lineup Scraper uses **Claude Vision API** (Anthropic) to extract NBA lineup data from screenshots. This approach is more reliable than HTML scraping, which can break when websites change their structure or use anti-bot protection.

## Why Image-Based Scraping?

Traditional HTML scraping from sites like RotoWire and Basketball Monster often fails due to:
- Cloudflare protection
- Dynamic JavaScript rendering
- Frequent HTML structure changes
- Anti-bot measures

The image-based approach:
- ✅ Works reliably with any lineup screenshot
- ✅ Resistant to website changes
- ✅ No need to bypass anti-bot protection
- ✅ Can process screenshots from any source (RotoWire, Basketball Monster, ESPN, etc.)

## Setup

### 1. Install Dependencies

All required dependencies are already in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 2. Configure Anthropic API Key

You need an Anthropic API key to use Claude Vision. Add it to your `.env` file:

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

Or set it as an environment variable:
```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

## Usage

### Basic Usage

Import lineups from a screenshot for today's games:

```bash
python import_lineup_from_image.py lineup_screenshot.png
```

### Specify Game Date

Import lineups for a specific date:

```bash
python import_lineup_from_image.py lineup_screenshot.png 2025-12-05
```

### Process Multiple Images

Import lineups from multiple screenshots:

```bash
python import_lineup_from_image.py game1.png game2.png game3.png
```

### Process Multiple Images with Specific Date

```bash
python import_lineup_from_image.py game1.png game2.png 2025-12-06
```

## How to Take Screenshots

### RotoWire Lineups

1. Go to https://www.rotowire.com/basketball/nba-lineups.php
2. Take a screenshot of each game's lineup section
3. Save as PNG or JPEG
4. Run the import script with your screenshot

### Basketball Monster Lineups

1. Go to https://basketballmonster.com/nbalineups.aspx
2. Take screenshots of the lineup tables
3. Save as PNG or JPEG
4. Run the import script

### Tips for Good Screenshots

- ✅ Include the full lineup section with both teams
- ✅ Make sure team names/abbreviations are visible
- ✅ Ensure player names and positions are clear
- ✅ Include injury status indicators if shown
- ❌ Don't crop too tightly - include some context
- ❌ Avoid screenshots with overlapping popups or menus

## Programmatic Usage

You can also use the scraper in your Python code:

```python
from datetime import date
from nba_predictor.scraper.image_lineup_scraper import ImageLineupScraper

# Initialize scraper
scraper = ImageLineupScraper()

# Import from a single image
count = scraper.import_lineups_from_image(
    image_path="lineup_screenshot.png",
    game_date=date(2025, 12, 5)
)
print(f"Imported {count} lineup entries")

# Import from multiple images
image_paths = ["game1.png", "game2.png", "game3.png"]
total = scraper.import_lineups_from_multiple_images(
    image_paths=image_paths,
    game_date=date(2025, 12, 5)
)
print(f"Imported {total} lineup entries total")
```

## Data Structure

The scraper extracts and saves the following information to the `nba_daily_lineup` table:

| Field | Description | Example |
|-------|-------------|---------|
| `scrape_date` | Date when data was scraped | 2025-12-05 |
| `game_date` | Date of the game | 2025-12-05 |
| `team_name` | Full team name | "Los Angeles Lakers" |
| `player_name` | Player's full name | "LeBron James" |
| `position` | Player's position | "SF" |
| `status` | Player's status | "Starter", "OUT", "Questionable" |
| `injury_description` | Injury details (if any) | "Out", "Doubtful" |
| `notes` | Additional notes | null |

## Status Values

The scraper recognizes these status values:

- **Starter**: Player is in the starting lineup
- **Expected Lineup**: Player is expected to play
- **OUT**: Player is out and will not play
- **Doubtful**: Player is unlikely to play
- **Questionable**: Player's status is uncertain
- **GTD**: Game-Time Decision
- **Probable**: Player is likely to play
- **Active**: Player is active and available

## Supported Image Formats

- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- WebP (.webp)

## Troubleshooting

### "Failed to initialize scraper: ..."

- Make sure `ANTHROPIC_API_KEY` is set in your `.env` file or environment
- Check that your API key is valid and has credits

### "Image file not found: ..."

- Verify the image path is correct
- Use absolute paths or paths relative to where you run the script

### "Failed to parse response as JSON: ..."

- The image might be unclear or not showing lineup data
- Try taking a clearer screenshot with better visibility
- Make sure the screenshot shows actual lineup information

### No lineups extracted

- Ensure the screenshot clearly shows:
  - Team names or abbreviations
  - Player names
  - Positions
- Try zooming in on the lineup section before taking the screenshot

## Cost Considerations

The Claude Vision API has usage costs. Each image analysis typically uses:
- Model: Claude 3.5 Sonnet
- Approximate tokens: 1,500-3,000 per image (depending on image size)
- Cost: ~$0.01-0.02 per image at current pricing

For daily usage:
- ~10 games per day = 10 screenshots
- Cost: ~$0.10-0.20 per day
- Monthly: ~$3-6

This is significantly more cost-effective than maintaining complex scraping infrastructure.

## Advantages Over HTML Scraping

| Aspect | HTML Scraping | Image Scraping |
|--------|---------------|----------------|
| Reliability | ❌ Breaks often | ✅ Very reliable |
| Maintenance | ❌ High | ✅ Low |
| Anti-bot issues | ❌ Common | ✅ None |
| Setup complexity | ❌ Complex | ✅ Simple |
| Website independence | ❌ Tied to one site | ✅ Works with any |
| Cost | ✅ Free | ⚠️ Small API cost |

## Future Enhancements

Possible improvements:
- [ ] Automatic screenshot capture from URLs
- [ ] Batch processing of multiple dates
- [ ] Integration with prediction system
- [ ] Automatic scheduling for daily imports
- [ ] Support for video/GIF lineup animations
- [ ] OCR fallback for simple text extraction

## Support

If you encounter issues:
1. Check the logs for detailed error messages
2. Verify your screenshot quality and content
3. Ensure your Anthropic API key is valid
4. Check your database connection settings

For Claude Vision API issues, refer to:
https://docs.anthropic.com/claude/docs/vision
