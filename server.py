import os
import requests
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from nbt import nbt

app = FastAPI()

WORLD_DIR = os.getenv("WORLD_DIR", "/mnt/ssd/docker-data/mc/gtnh/World")
PLAYERDATA_DIR = os.path.join(WORLD_DIR, "playerdata")
LEVEL_DAT = os.path.join(WORLD_DIR, "level.dat")

def get_id_to_tag():
    """Reads level.dat to generate a mapping from numerical item IDs to String tags"""
    if not os.path.exists(LEVEL_DAT):
        print(f"Warning: {LEVEL_DAT} not found.")
        return {}
    
    id_to_tag = {}
    try:
        level = nbt.NBTFile(LEVEL_DAT, "rb")
        item_data = level["FML"]["ItemData"]
        for item in item_data:
            val = item["V"].value
            key = item["K"].value
            # Slice the first character (usually Forge's \x01 marker) as the Vue app did
            if isinstance(key, str) and len(key) > 0:
                tag = key[1:]
                id_to_tag[val] = tag
    except Exception as e:
        print(f"Error parsing level.dat: {e}")
    return id_to_tag

@app.get("/api/players")
def get_players():
    """Enumerates uuid.dat files and fetches player info."""
    if not os.path.exists(PLAYERDATA_DIR):
        return {"players": []}
    
    players = []
    for f in os.listdir(PLAYERDATA_DIR):
        if f.endswith(".dat"):
            uuid = f[:-4]
            name = "Unknown"
            uuid_no_dashes = uuid.replace("-", "")
            
            # Fetch name from Mojang in the backend to avoid browser CORS errors
            try:
                resp = requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid_no_dashes}", timeout=2)
                if resp.status_code == 200:
                    name = resp.json().get("name", "Unknown")
            except Exception:
                pass
            
            players.append({
                "uuid": uuid,
                "name": name,
                "face_url": f"https://api.mineatar.io/face/{uuid}?scale=12"
            })
    return {"players": players}

@app.get("/api/stats/{uuid}")
def get_player_stats(uuid: str):
    """Generates and returns Spice of Life stats for a player."""
    uuid = os.path.basename(uuid)  # Sanitize input to prevent directory traversal

    file_path = os.path.join(PLAYERDATA_DIR, f"{uuid}.dat")
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "Player not found"})
    
    id_to_tag = get_id_to_tag()
    
    try:
        player_dat = nbt.NBTFile(file_path, "rb")
        foods_tag = player_dat["ForgeData"]["PlayerPersisted"]["SpiceOfLifeHistory"]["FullHistory"]["Foods"]
        
        eaten = []
        categories = {}
        
        for food in foods_tag:
            if "id" not in food:
                continue
            food_id = food["id"].value
            damage = food["Damage"].value if "Damage" in food else 0
            hunger = food["Hunger"].value if "Hunger" in food else 0
            
            tag = id_to_tag.get(food_id, str(food_id))
            mod = tag.split(":")[0] if ":" in tag else "unknown"
            
            eaten.append({
                "id": food_id,
                "tag": tag,
                "damage": damage,
                "hunger": hunger,
                "mod": mod
            })
            categories[mod] = categories.get(mod, 0) + 1
            
        total_eaten = len(eaten)
        percentages = {}
        for mod, count in categories.items():
            percentages[mod] = round((count / total_eaten) * 100, 2) if total_eaten > 0 else 0
            
        return {
            "uuid": uuid,
            "total_eaten": total_eaten,
            "eaten": eaten,
            "categories": categories,
            "percentages": percentages,
            # Note: Accurately calculating `not_eaten` requires a full GTNH food dictionary which is not stored in NBT natively.
            "not_eaten": [] 
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Mount the frontend directory
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)