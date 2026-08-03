import { Repository } from 'https://shadowtheage.github.io/gtnh/repository.js';
import { ungzip } from 'https://cdn.jsdelivr.net/npm/pako@2.1.0/+esm';

let repo = null;

async function loadRepo() {
    if (repo) return repo;
    try {
        const response_data = await fetch("https://shadowtheage.github.io/gtnh/data/data.bin").then(x => x.arrayBuffer());
        repo = Repository.load(ungzip(new Uint8Array(response_data)).buffer);
    } catch (e) {
        console.error("Failed to load ShadowTheAge repo", e);
    }
    return repo;
}

const pamFix = {
    "harvestcraft:pamcarrotCake": "Carrot Cake",
    "harvestcraft:pamcheeseCake": "Cheese Cake",
    "harvestcraft:pamcherrycheeseCake": "Cherry Cheese Cake",
    "harvestcraft:pampineappleupsidedownCake": "Pineapple Upside Down Cake",
    "harvestcraft:pamchocolatesprinkleCake": "Chocolate Sprinkles Cake",
    "harvestcraft:pamredvelvetCake": "Red Velvet Cake",
    "harvestcraft:pamlamingtonCake": "Lamington",
    "harvestcraft:pampavlovaCake": "Pavlova",
    "harvestcraft:pamholidayCake": "Holiday Cake",
    "harvestcraft:pampumpkincheeseCake": "Pumpkin Cheese Cake"
};

const manualFix = {
    "i:BloodArsenal:blood_cake:0": {name: "Blood Cake", mod: "BloodArsenal"},
    "i:TConstruct:strangeFood:2": {name: "Bacon", mod: "TConstruct"},
    "i:Forestry:beverage:1": {name: "Curative Mead", mod: "Forestry"}
};

function modToShort(mod) {
    switch (mod) {
        case 'gregtech': return '(GT)';
        case 'harvestcraft': return '(Pam)';
        case 'Natura': return '(Natura)';
        case 'Forestry': return '(Forestry)';
        case 'TConstruct': return '(TiC)';
        case 'ExtraTrees': return '(ET)';
        case 'TwilightForest': return '(TF)';
        case 'witchery': return '(Witchery)';
        case 'ThaumicHorizons': return '(TC)';
        case 'etfuturum': return '(EFR)';
        case 'BiomesOPlenty': return '(BoP)';
        case 'cookingforblockheads': return '(Cooking for BH)';
        case 'minecraft': return '(Vanilla)';
        default: return mod;
    }
}

async function getPrettyItemInfo(itemTag, damage) {
    const r = await loadRepo();
    if (!r) return { name: itemTag, modshort: modToShort(itemTag.split(':')[0]) };

    if (itemTag === "minecraft:golden_apple") {
        return { name: damage === 0 ? "Golden Apple (Ingots)" : "Golden Apple (Blocks)", modshort: modToShort("minecraft") };
    } else if (pamFix[itemTag]) {
        return { name: pamFix[itemTag], modshort: modToShort("harvestcraft") };
    }

    const itemRepoTag = "i:" + itemTag + ":" + damage;
    let item = r.GetById(itemRepoTag);
    if (!item) {
        const itemRepoTagCake = "i:" + itemTag + "Item" + ":" + damage;
        item = r.GetById(itemRepoTagCake);
        if (!item) {
            item = manualFix[itemRepoTag];
            if (!item) return { name: itemTag, modshort: modToShort(itemTag.split(':')[0]) };
        }
    }
    
    let name = item.name;
    let modshort = modToShort(item.mod);
    
    // Fixes based on Vue logic mappings
    if (modshort === "(GT)" && name === "Dough") {
        switch (damage) {
            case 32561: name = "Dough in Bread Shape"; break;
            case 32562: name = "Dough in Bun Shape"; break;
            case 32563: name = "Dough in Baguette Shape"; break;
        }
    }
    if (modshort === "(GT)" && name === "Fries" && damage === 32204) name = "Fries (In Foil)";
    if (modshort === "(Natura)" && itemTag === "Natura:natura.stewbowl") {
        name = damage >= 14 ? "Glowshroom " : "Mushroom ";
        switch (damage % 14) {
            case 0: name += "Stew 1"; break;
            case 3: name += "Stew 2"; break;
            case 5: name += "Stew 3"; break;
            case 12: name += "Stew 4"; break;
            case 13: name += "Stew 5"; break;
        }
    }
    return { name, modshort };
}

document.addEventListener("DOMContentLoaded", () => {
    loadPlayers();
    document.getElementById("back-btn").addEventListener("click", () => {
        document.getElementById("stats-section").style.display = "none";
        document.getElementById("players-section").style.display = "block";
    });
});

async function loadPlayers() {
    try {
        const res = await fetch("/api/players");
        const data = await res.json();
        const list = document.getElementById("players-list");
        
        data.players.forEach(p => {
            const card = document.createElement("div");
            card.className = "player-card";
            card.innerHTML = `
                <img src="${p.face_url}" alt="${p.name}">
                <h3>${p.name}</h3>
                <p style="font-size: 0.8rem; color: #aaa; margin-bottom: 1rem; word-break: break-all;">${p.uuid}</p>
                <button>View Stats</button>
            `;
            card.addEventListener("click", () => showStats(p));
            list.appendChild(card);
        });
    } catch (e) {
        console.error("Error loading players:", e);
    }
}

async function showStats(player) {
    document.getElementById("players-section").style.display = "none";
    document.getElementById("stats-section").style.display = "block";
    
    document.getElementById("player-header").innerHTML = `
        <div class="player-header-flex">
            <img src="${player.face_url}" alt="${player.name}">
            <div><h2>${player.name}'s Stats</h2><p style="color:#aaa;">${player.uuid}</p></div>
        </div>`;
    
    document.getElementById("total-eaten").textContent = "Loading...";
    document.getElementById("category-list").innerHTML = "<li>Loading...</li>";
    const tbody = document.getElementById("foods-table").querySelector("tbody");
    tbody.innerHTML = "<tr><td colspan='3'>Loading foods... (Might take a sec to map ID names)</td></tr>";
    
    try {
        const res = await fetch(`/api/stats/${player.uuid}`);
        const data = await res.json();
        
        document.getElementById("total-eaten").textContent = data.total_eaten;
        const catList = document.getElementById("category-list");
        catList.innerHTML = "";
        
        // Render Categories Sorted
        const sortedCats = Object.keys(data.percentages).sort((a, b) => data.percentages[b] - data.percentages[a]);
        sortedCats.forEach(cat => {
            const li = document.createElement("li");
            li.innerHTML = `<span>${cat}</span> <span>${data.percentages[cat]}% (${data.categories[cat]})</span>`;
            catList.appendChild(li);
        });
        
        // Prep mapping repository parallel promise
        await loadRepo();
        tbody.innerHTML = "";
        
        // Render detailed eaten table
        for (const f of data.eaten) {
            const tr = document.createElement("tr");
            const info = await getPrettyItemInfo(f.tag, f.damage);
            
            tr.innerHTML = `
                <td><strong>${info.name}</strong> <br><small style="color:#aaa">${f.tag}:${f.damage}</small></td>
                <td>${info.modshort}</td>
                <td>${f.hunger}</td>
            `;
            tbody.appendChild(tr);
        }
    } catch (e) {
        console.error("Error loading stats:", e);
    }
}