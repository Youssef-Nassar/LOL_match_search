"""
Script to download all League of Legends champion icons from Riot's Data Dragon CDN
"""
import httpx
import os
import json
from pathlib import Path

# Create champions-icons directory if it doesn't exist (relative to project root)
BASE_DIR = Path(__file__).parent.parent
ICONS_DIR = BASE_DIR / "static" / "champions-icons"
ICONS_DIR.mkdir(parents=True, exist_ok=True)

# Data Dragon CDN base URL
DD_VERSION = "14.24.1"  # Latest patch version
BASE_URL = f"https://ddragon.leagueoflegends.com/cdn/{DD_VERSION}"

async def get_champion_list():
    """Fetch the list of all champions from Data Dragon"""
    url = f"{BASE_URL}/data/en_US/champion.json"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {})
        else:
            print(f"Error fetching champion list: {response.status_code}")
            return {}

async def download_champion_icon(champion_id, champion_name):
    """Download a single champion icon"""
    icon_url = f"{BASE_URL}/img/champion/{champion_id}.png"
    icon_path = ICONS_DIR / f"{champion_id.lower()}.png"
    
    # Skip if already exists
    if icon_path.exists():
        print(f"✓ {champion_name} ({champion_id}) - Already exists")
        return True
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(icon_url, timeout=30.0)
            if response.status_code == 200:
                icon_path.write_bytes(response.content)
                print(f"✓ {champion_name} ({champion_id}) - Downloaded")
                return True
            else:
                print(f"✗ {champion_name} ({champion_id}) - Failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"✗ {champion_name} ({champion_id}) - Error: {str(e)}")
        return False

async def main():
    """Main function to download all champion icons"""
    print("Fetching champion list from Data Dragon...")
    champions = await get_champion_list()
    
    if not champions:
        print("Failed to fetch champion list. Trying alternative method...")
        # Fallback: try to get version list first
        try:
            async with httpx.AsyncClient() as client:
                versions_url = "https://ddragon.leagueoflegends.com/api/versions.json"
                versions_response = await client.get(versions_url)
                if versions_response.status_code == 200:
                    versions = versions_response.json()
                    global DD_VERSION
                    DD_VERSION = versions[0]  # Use latest version
                    BASE_URL = f"https://ddragon.leagueoflegends.com/cdn/{DD_VERSION}"
                    print(f"Using latest version: {DD_VERSION}")
                    
                    # Try again with latest version
                    url = f"{BASE_URL}/data/en_US/champion.json"
                    response = await client.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        champions = data.get("data", {})
        except Exception as e:
            print(f"Error: {e}")
            return
    
    if not champions:
        print("Could not fetch champion list. Exiting.")
        return
    
    print(f"\nFound {len(champions)} champions. Starting download...\n")
    
    # Download all champion icons
    import asyncio
    tasks = []
    for champion_id, champion_data in champions.items():
        champion_name = champion_data.get("name", champion_id)
        tasks.append(download_champion_icon(champion_id, champion_name))
    
    results = await asyncio.gather(*tasks)
    
    successful = sum(results)
    print(f"\n{'='*50}")
    print(f"Download complete!")
    print(f"Successfully downloaded: {successful}/{len(champions)} icons")
    print(f"Icons saved to: {ICONS_DIR.absolute()}")
    print(f"{'='*50}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

