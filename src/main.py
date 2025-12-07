from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import httpx
import os
import pathlib
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
# Static files path relative to project root
BASE_DIR = pathlib.Path(__file__).parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

RIOT_API_KEY = os.getenv("RIOT_API_KEY", "(your_riot_api_key)")
REGION = os.getenv("REGION", "europe")
BASE_URL = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches"


async def fetch_match(match_id: str) -> dict:
    """Fetch match data from Riot API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/{match_id}",
            headers={"X-Riot-Token": RIOT_API_KEY}
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Invalid match ID or API error: {response.text}"
            )
        return response.json()


def parse_match_data(match_data: dict) -> List[Dict]:
    """Parse match data and extract player statistics"""
    players = []
    participants = match_data.get("info", {}).get("participants", [])
    
    for p in participants:
        # Extract role/position (teamPosition is most reliable: TOP, JUNGLE, MIDDLE, BOTTOM, UTILITY)
        # Handle None, empty string, or missing values
        team_position = p.get("teamPosition") or p.get("lane") or ""
        if team_position and str(team_position).strip():
            role = str(team_position).strip().upper()
        else:
            role = "UNKNOWN"
        
        players.append({
            "summonerName": p.get("riotIdGameName") or p.get("gameName") or p.get("summonerName") or "Unknown",
            "championName": p.get("championName", "Unknown"),
            "role": role,
            "gold": p.get("goldEarned", 0),
            "kills": p.get("kills", 0),
            "deaths": p.get("deaths", 0),
            "assists": p.get("assists", 0),
            "CS": p.get("totalMinionsKilled", 0) + p.get("neutralMinionsKilled", 0),
            "damageDealtToChampions": p.get("totalDamageDealtToChampions", 0),
            "damageTaken": p.get("totalDamageTaken", 0),
            "teamId": p.get("teamId", 0),
            "win": p.get("win", False)
        })
    return players


@app.get("/")
async def read_root():
    return FileResponse(str(BASE_DIR / "static" / "index.html"))


@app.get("/match/{match_id}")
async def get_match_data(match_id: str):
    return await fetch_match(match_id)


@app.get("/match/{match_id}/players")
async def get_match_players(match_id: str):
    match_data = await fetch_match(match_id)
    return {"matchId": match_id, "players": parse_match_data(match_data)}


@app.get("/match/{match_id}/player/{player_index}")
async def get_player_data(match_id: str, player_index: int):
    match_data = await fetch_match(match_id)
    players = parse_match_data(match_data)
    
    if not 0 <= player_index < len(players):
        raise HTTPException(
            status_code=404,
            detail=f"Player index {player_index} not found. Valid range: 0-{len(players)-1}"
        )
    
    return {"matchId": match_id, "player": players[player_index]}
