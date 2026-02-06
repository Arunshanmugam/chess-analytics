"""
Chess.com Game Downloader

Downloads rapid chess games from Chess.com and organizes them into 
win/loss/draw folders.

Usage:
    python fetch_chess_games.py <username> [--count <number>]

Example:
    python fetch_chess_games.py magnuscarlsen --count 100
"""

import requests
import os
import argparse

def setup_directories(output_dir):
    for result_type in ["win", "loss", "draw"]:
        path = os.path.join(output_dir, result_type)
        os.makedirs(path, exist_ok=True)
    print(f"Directories created in {output_dir}")

def get_archives(username):
    url = f"https://api.chess.com/pub/player/{username}/games/archives"
    try:
        response = requests.get(url, headers={"User-Agent": "ChessGameDownloader/1.0"})
        response.raise_for_status()
        return response.json().get("archives", [])
    except Exception as e:
        print(f"Error fetching archives: {e}")
        return []

def get_games_from_archive(archive_url):
    try:
        response = requests.get(archive_url, headers={"User-Agent": "ChessGameDownloader/1.0"})
        response.raise_for_status()
        return response.json().get("games", [])
    except Exception as e:
        print(f"Error fetching games from {archive_url}: {e}")
        return []

def classify_game(game, username):
    white_user = game["white"]["username"].lower()
    user_color = "white" if white_user == username.lower() else "black"
    result = game[user_color]["result"]
    
    if result == "win":
        return "win"
    elif result in ["checkmated", "timeout", "resigned", "abandoned"]:
        return "loss"
    elif result in ["agreed", "repetition", "stalemate", "insufficient", "50move", "timevsinsufficient"]:
        return "draw"
    else:
        print(f"Unknown result: {result} for game {game.get('url')}")
        return "draw"

def save_game(game, classification, output_dir):
    url = game.get("url", "")
    game_id = url.split("/")[-1] if url else "unknown_id"
    
    filename = f"game_{game_id}.pgn"
    path = os.path.join(output_dir, classification, filename)
    
    pgn = game.get("pgn")
    if pgn:
        with open(path, "w", encoding="utf-8") as f:
            f.write(pgn)
        return True
    return False

def main():
    parser = argparse.ArgumentParser(
        description="Download rapid chess games from Chess.com and organize by result."
    )
    parser.add_argument("username", help="Your Chess.com username")
    parser.add_argument("--count", type=int, default=50, help="Number of games to download (default: 50)")
    parser.add_argument("--output", default="chess_games", help="Output directory (default: chess_games)")
    
    args = parser.parse_args()
    
    username = args.username
    target_count = args.count
    output_dir = args.output
    
    print(f"Downloading last {target_count} rapid games for '{username}'...")
    
    setup_directories(output_dir)
    archives = get_archives(username)
    
    count = 0
    print(f"Found {len(archives)} archives. Processing...")
    
    for archive_url in reversed(archives):
        if count >= target_count:
            break
            
        print(f"Checking archive: {archive_url}")
        games = get_games_from_archive(archive_url)
        
        games.sort(key=lambda x: x.get("end_time", 0), reverse=True)
        
        for game in games:
            if count >= target_count:
                break
                
            if game.get("time_class") == "rapid":
                classification = classify_game(game, username)
                if save_game(game, classification, output_dir):
                    count += 1
                    print(f"[{count}/{target_count}] Saved {classification}: {game.get('url')}")

    print(f"\nDone! Downloaded {count} games to '{output_dir}/'")

if __name__ == "__main__":
    main()
