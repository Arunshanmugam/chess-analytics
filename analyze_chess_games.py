"""
Chess Game Analytics

Parses downloaded PGN files and generates a CSV with enriched analytics.

Usage:
    python analyze_chess_games.py <username> [--input <dir>] [--output <file>]

Example:
    python analyze_chess_games.py magnuscarlsen --output my_analytics.csv
"""

import os
import csv
import re
import argparse

# Common ECO code to Opening Name mapping
ECO_OPENINGS = {
    "A00": "Uncommon Opening", "A01": "Nimzo-Larsen Attack", "A02": "Bird's Opening",
    "A04": "Reti Opening", "A10": "English Opening", "A20": "English Opening",
    "A28": "English Opening: Four Knights", "A40": "Queen's Pawn Game", "A45": "Trompowsky Attack",
    "A46": "Indian Game", "A48": "London System",
    "B00": "Uncommon King's Pawn Opening", "B01": "Scandinavian Defense",
    "B02": "Alekhine's Defense", "B07": "Pirc Defense", "B10": "Caro-Kann Defense",
    "B12": "Caro-Kann Defense", "B20": "Sicilian Defense", "B21": "Sicilian: Smith-Morra Gambit",
    "B22": "Sicilian: Alapin", "B27": "Sicilian Defense", "B30": "Sicilian Defense",
    "B40": "Sicilian Defense", "B44": "Sicilian: Taimanov",
    "B50": "Sicilian Defense", "B90": "Sicilian: Najdorf",
    "C00": "French Defense", "C02": "French: Advance Variation",
    "C20": "King's Pawn Game", "C21": "Center Game", "C23": "Bishop's Opening",
    "C25": "Vienna Game", "C28": "Vienna Game",
    "C40": "King's Knight Opening", "C42": "Petrov's Defense", "C44": "Scotch Game",
    "C45": "Scotch Game", "C46": "Three Knights Game", "C47": "Four Knights Game",
    "C50": "Italian Game", "C55": "Italian Game: Two Knights",
    "C60": "Ruy Lopez", "C65": "Ruy Lopez: Berlin Defense",
    "D00": "Queen's Pawn Game", "D02": "London System", "D06": "Queen's Gambit",
    "D10": "Slav Defense", "D11": "Slav Defense", "D20": "Queen's Gambit Accepted",
    "D23": "Queen's Gambit Accepted", "D30": "Queen's Gambit Declined",
    "D31": "Queen's Gambit Declined", "D35": "Queen's Gambit Declined",
    "D37": "Queen's Gambit Declined", "D55": "Queen's Gambit Declined",
    "E00": "Indian Defense", "E04": "Catalan Opening",
    "E10": "Indian Defense", "E20": "Nimzo-Indian Defense", "E24": "Nimzo-Indian Defense",
    "E60": "King's Indian Defense", "E70": "King's Indian Defense",
}

def parse_pgn(filepath):
    """Parses a PGN file and returns headers and move count."""
    headers = {}
    moves_text = ""
    in_moves = False
    
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                match = re.match(r'\[(\w+)\s+"(.*)"\]', line)
                if match:
                    headers[match.group(1)] = match.group(2)
            elif line == "":
                if headers:
                    in_moves = True
            elif in_moves:
                moves_text += " " + line
    
    move_numbers = re.findall(r'(\d+)\.\s', moves_text)
    move_count = int(move_numbers[-1]) if move_numbers else 0
    
    return headers, move_count

def classify_game_length(move_count):
    if move_count < 20:
        return "Quick"
    elif move_count <= 40:
        return "Medium"
    else:
        return "Long"

def get_opening_name(eco_code):
    if not eco_code:
        return "Unknown"
    if eco_code in ECO_OPENINGS:
        return ECO_OPENINGS[eco_code]
    for length in [2, 1]:
        prefix = eco_code[:length]
        for key, value in ECO_OPENINGS.items():
            if key.startswith(prefix):
                return value
    return "Unknown"

def classify_loss_quality(folder, move_count):
    if folder != "loss":
        return "N/A"
    if move_count < 15:
        return "Quick Loss"
    elif move_count < 30:
        return "Standard Loss"
    else:
        return "Well-Fought Loss"

def classify_termination(termination):
    if not termination:
        return "Unknown"
    term_lower = termination.lower()
    if "checkmate" in term_lower:
        return "Checkmate"
    elif "resignation" in term_lower:
        return "Resignation"
    elif "timeout" in term_lower:
        return "Timeout"
    elif "abandoned" in term_lower:
        return "Abandoned"
    elif "agreement" in term_lower:
        return "Draw by Agreement"
    elif "repetition" in term_lower:
        return "Draw by Repetition"
    elif "stalemate" in term_lower:
        return "Stalemate"
    elif "insufficient" in term_lower:
        return "Insufficient Material"
    else:
        return "Other"

def main():
    parser = argparse.ArgumentParser(
        description="Analyze downloaded chess PGN files and generate CSV analytics."
    )
    parser.add_argument("username", help="Your Chess.com username (used for color/rating calculations)")
    parser.add_argument("--input", default="chess_games", help="Input directory with PGN files (default: chess_games)")
    parser.add_argument("--output", default="chess_analytics.csv", help="Output CSV file (default: chess_analytics.csv)")
    
    args = parser.parse_args()
    
    username = args.username
    games_dir = args.input
    output_file = args.output
    
    print(f"Scanning '{games_dir}' for PGN files...")
    
    games_data = []
    
    for root, dirs, files in os.walk(games_dir):
        for file in files:
            if file.lower().endswith(".pgn"):
                filepath = os.path.join(root, file)
                headers, move_count = parse_pgn(filepath)
                folder = os.path.basename(root)
                
                # Determine color played
                white_user = headers.get("White", "").lower()
                color_played = "White" if white_user == username.lower() else "Black"
                
                # Rating differential
                try:
                    white_elo = int(headers.get("WhiteElo", 0))
                    black_elo = int(headers.get("BlackElo", 0))
                    if color_played == "White":
                        rating_diff = black_elo - white_elo
                    else:
                        rating_diff = white_elo - black_elo
                except ValueError:
                    rating_diff = 0
                
                game = {
                    "Filename": file,
                    "Folder": folder,
                    "ColorPlayed": color_played,
                    "RatingDiff": rating_diff,
                    "MoveCount": move_count,
                    "GameLength": classify_game_length(move_count),
                    "OpeningName": get_opening_name(headers.get("ECO")),
                    "LossQuality": classify_loss_quality(folder, move_count),
                    "TerminationType": classify_termination(headers.get("Termination")),
                    **{k: headers.get(k, "") for k in [
                        "Event", "Site", "Date", "White", "Black", "Result",
                        "WhiteElo", "BlackElo", "TimeControl", "ECO", "Termination", "Link"
                    ]}
                }
                games_data.append(game)

    if not games_data:
        print("No PGN files found.")
        return

    print(f"Found {len(games_data)} games. Generating CSV...")

    fieldnames = [
        "Filename", "Folder", "ColorPlayed", "RatingDiff", "MoveCount", "GameLength",
        "OpeningName", "LossQuality", "TerminationType",
        "Event", "Site", "Date", "White", "Black", "Result",
        "WhiteElo", "BlackElo", "TimeControl", "ECO", "Termination", "Link"
    ]
    
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for game in games_data:
            writer.writerow(game)
            
    print(f"\nSuccessfully generated '{output_file}' with {len(games_data)} records.")
    print("\nColumns included:")
    print("  - ColorPlayed, RatingDiff, MoveCount, GameLength")
    print("  - OpeningName, LossQuality, TerminationType")
    print("  - Plus standard PGN headers (Event, Date, Result, etc.)")

if __name__ == "__main__":
    main()
