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
        return {}
    
    id_to_tag = {}
    try:
        level = nbt.NBTFile(LEVEL_DAT, "rb")
        item_data = level["FML"]["ItemData"]
        for item in item_data:
            val = item["V"].value
            key = item["K"].value
            if isinstance(key, str) and len(key) > 0:
                id_to_tag[val] = key[1:] # Strip Forge's \x01 marker
    except Exception as e:
        print(f"Error parsing level.dat: {e}")
    return id_to_tag

@app.get("/api/players")
def get_players():
    if not os.path.exists(PLAYERDATA_DIR):
        return {"players": []}
    
    players = []
    for f in os.listdir(PLAYERDATA_DIR):
        if f.endswith(".dat"):
            uuid = f[:-4]
            name = "Unknown"
            
            try:
                # Get name from Mojang
                resp = requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid.replace('-', '')}", timeout=2)
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
    uuid = os.path.basename(uuid)
    file_path = os.path.join(PLAYERDATA_DIR, f"{uuid}.dat")
    
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "Player not found"})
    
    id_to_tag = get_id_to_tag()
    
    try:
        player_dat = nbt.NBTFile(file_path, "rb")
        foods_tag = player_dat["ForgeData"]["PlayerPersisted"]["SpiceOfLifeHistory"]["FullHistory"]["Foods"]
        
        eaten = []
        for food in foods_tag:
            if "id" not in food: continue
            
            food_id = food["id"].value
            tag = id_to_tag.get(food_id, str(food_id))
            
            eaten.append({
                "tag": tag,
                "damage": food.get("Damage", {}).value if "Damage" in food else 0,
                "hunger": food.get("Hunger", {}).value if "Hunger" in food else 0
            })
            
        return {"uuid": uuid, "eaten": eaten}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)