# Chess.com Game Analyzer

Download and analyze your rapid chess games from Chess.com with detailed insights.

## Features

**Game Downloader (`fetch_chess_games.py`)**
- Downloads your rapid games from Chess.com
- Automatically classifies games into `win/`, `loss/`, `draw/` folders
- Saves games in standard PGN format

**Game Analyzer (`analyze_chess_games.py`)**
- Parses PGN files and generates a CSV with enriched analytics
- Includes insights like:
  - **Color Played** (White/Black)
  - **Rating Differential** (opponent Elo - your Elo)
  - **Game Length** (Quick/Medium/Long)
  - **Opening Name** (mapped from ECO codes)
  - **Loss Quality** (Quick Loss/Standard Loss/Well-Fought Loss)
  - **Termination Type** (Checkmate/Resignation/Timeout/etc.)

## Installation

```bash
pip install requests
```

## Usage

### 1. Download Games
```bash
python fetch_chess_games.py <your_username> --count 50
```

Options:
- `--count`: Number of games to download (default: 50)
- `--output`: Output directory (default: `chess_games`)

### 2. Analyze Games
```bash
python analyze_chess_games.py <your_username>
```

Options:
- `--input`: Input directory with PGN files (default: `chess_games`)
- `--output`: Output CSV filename (default: `chess_analytics.csv`)

## Example

```bash
# Download last 100 rapid games
python fetch_chess_games.py magnuscarlsen --count 100

# Generate analytics CSV
python analyze_chess_games.py magnuscarlsen --output magnus_stats.csv
```

## Output

The analyzer generates a CSV file with columns:
- `Filename`, `Folder`, `ColorPlayed`, `RatingDiff`
- `MoveCount`, `GameLength`, `OpeningName`
- `LossQuality`, `TerminationType`
- Standard PGN headers (Date, Result, WhiteElo, BlackElo, etc.)

## License

MIT License
