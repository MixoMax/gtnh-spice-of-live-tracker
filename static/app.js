import { Repository } from 'https://shadowtheage.github.io/gtnh/repository.js';
import { ungzip } from 'https://cdn.jsdelivr.net/npm/pako@2.1.0/+esm';

let repo = null;
let tiersDB = null;

let currentTracker = null;
let currentTiersDB = null;
let currentSelectedTier = "T1 (Raw)";

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

async function loadTiers() {
    if (tiersDB) return tiersDB;
    try {
        const response = await fetch("/api/tiers");
        tiersDB = await response.json();
    } catch (e) {
        console.error("Failed to load tiers DB", e);
    }
    return tiersDB;
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
        list.innerHTML = "";

        const serverCard = document.createElement("div");
        serverCard.className = "player-card";
        serverCard.innerHTML = `
            <img src="https://minecraft.wiki/images/thumb/Minecraft_social_icon.png/600px-Minecraft_social_icon.png" alt="Minecraft social logo">
            <h3>Server</h3>
            <p style="font-size: 0.8rem; color: #aaa; margin-bottom: 1rem; word-break: break-all;">Stats of all players combined</p>
            <button>View Stats</button>
        `;
        serverCard.addEventListener("click", () => showStatsAll("https://minecraft.wiki/images/thumb/Minecraft_social_icon.png/600px-Minecraft_social_icon.png"));
        list.appendChild(serverCard);
        
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
    
    // Switch to skeleton view
    document.getElementById("stats-content").style.display = "none";
    document.getElementById("stats-skeleton").style.display = "block";
    
    document.getElementById("player-header").innerHTML = `
        <div class="player-header-flex">
            <img src="${player.face_url}" alt="${player.name}">
            <div><h2>${player.name}'s Tracker</h2><p style="color:#aaa;">${player.uuid}</p></div>
        </div>`;
    
    try {
        const [resStats, tiersBackend] = await Promise.all([
            fetch(`/api/stats/${player.uuid}`).then(x => x.json()),
            loadTiers()
        ]);
        
        const tracker = {
            total_overall_shanks: 0,
            obtained_overall_shanks: 0,
            tiers: {}
        };
        
        const TIER_ORDER = ["T1 (Raw)", "T2 (Basic)", "T3 (Intermediate)", "T4 (Advanced)"];

        for (const [t, data] of Object.entries(tiersBackend)) {
            tracker.total_overall_shanks += data.total_shanks;
            tracker.tiers[t] = {
                obtained_shanks: 0,
                total_shanks: data.total_shanks,
                matched_items: new Set()
            };
        }

        // 1. Resolve all eaten items in parallel
        await loadRepo();
        const resolvedFoods = await Promise.all(resStats.eaten.map(async f => {
            const info = await getPrettyItemInfo(f.tag, f.damage);
            return { ...f, ...info };
        }));

        // 2. Cross reference with Tier Database
        for (const f of resolvedFoods) {
            const fullName = f.name + ' ' + f.modshort;
            const shortName = f.name;

            for (const [tierName, tierData] of Object.entries(tiersBackend)) {
                const foundShanks = tierData.foods[fullName] !== undefined ? tierData.foods[fullName] : 
                                   (tierData.foods[shortName] !== undefined ? tierData.foods[shortName] : null);
                
                if (foundShanks !== null) {
                    const matchKey = tierData.foods[fullName] !== undefined ? fullName : shortName;
                    
                    if (!tracker.tiers[tierName].matched_items.has(matchKey)) {
                        tracker.tiers[tierName].matched_items.add(matchKey);
                        tracker.tiers[tierName].obtained_shanks += foundShanks;
                        tracker.obtained_overall_shanks += foundShanks;
                    }
                    break;
                }
            }
        }
        
        // Expose globally for switching tiers
        currentTracker = tracker;
        currentTiersDB = tiersBackend;

        // Switch to content view
        document.getElementById("stats-skeleton").style.display = "none";
        document.getElementById("stats-content").style.display = "block";

        // 3. Render Top Dashboard (Live Tracker)
        const total = tracker.total_overall_shanks;
        const obt = tracker.obtained_overall_shanks;
        const rem = total - obt;
        
        const pct = total > 0 ? (obt / total * 100).toFixed(1) : 0.0;
        const remaining_pct = total > 0 ? (rem / total * 100).toFixed(1) : 100.0;
        
        document.getElementById("overall-pct").textContent = `${pct}%`;
        document.getElementById("overall-remaining-pct").textContent = `${remaining_pct}%`;
        document.getElementById("overall-donut-pct").textContent = `${pct}%`;
        document.getElementById("overall-donut").style.setProperty("--pct", `${pct}%`);
        
        document.getElementById("shanks-remaining").textContent = rem;
        document.getElementById("shanks-obtained").textContent = obt;
        
        const heartsObt = Math.floor(obt / 50);
        const heartsRem = Math.floor(rem / 50);
        const untilNext = 50 - (obt % 50);

        document.getElementById("hearts-remaining").textContent = heartsRem;
        document.getElementById("hearts-obtained").textContent = heartsObt;
        document.getElementById("until-next").textContent = untilNext;

        // 4. Render the 4 Small Tier Donuts
        const chartsContainer = document.getElementById("tier-charts-container");
        chartsContainer.innerHTML = "";

        TIER_ORDER.forEach(tier => {
            const data = tracker.tiers[tier];
            const tPct = data.total_shanks > 0 ? (data.obtained_shanks / data.total_shanks * 100).toFixed(1) : 0;
            const tRem = data.total_shanks - data.obtained_shanks;
            
            const card = document.createElement("div");
            card.className = "tier-card";
            card.innerHTML = `
                <h4>${tier}</h4>
                <div class="tier-donut-container">
                    <div class="donut donut-small" style="--pct: ${tPct}%">
                        <div class="donut-content">${tPct}%</div>
                    </div>
                </div>
                <div class="tier-stats">
                    <strong>${tRem}</strong> Shanks Remaining<br>
                    <strong style="color: #f5b041">${data.obtained_shanks}</strong> Shanks Obtained
                </div>
            `;
            chartsContainer.appendChild(card);
        });

        // 5. Render Tier Selector and Table
        renderTierSelector();
        renderTierTable(currentSelectedTier);

    } catch (e) {
        console.error("Error generating stats:", e);
        document.getElementById("stats-skeleton").innerHTML = "<p style='color:red;'>An error occurred loading stats.</p>";
    }
}

async function showStatsAll(image) {
    document.getElementById("players-section").style.display = "none";
    document.getElementById("stats-section").style.display = "block";
    
    // Switch to skeleton view
    document.getElementById("stats-content").style.display = "none";
    document.getElementById("stats-skeleton").style.display = "block";
    
    document.getElementById("player-header").innerHTML = `
        <div class="player-header-flex">
            <img src="${image}" alt="Combined">
            <div><h2>Combined's Tracker</h2><p style="color:#aaa;">Stats of all players combined</p></div>
        </div>`;
    
    try {
        const [resStats, tiersBackend] = await Promise.all([
            fetch(`/api/stats/all`).then(x => x.json()),
            loadTiers()
        ]);
        
        console.log("Combined stats:", resStats);
        const tracker = {
            total_overall_shanks: 0,
            obtained_overall_shanks: 0,
            tiers: {},
            eatenFullCount: 0
        };
        
        const TIER_ORDER = ["T1 (Raw)", "T2 (Basic)", "T3 (Intermediate)", "T4 (Advanced)"];

        for (const [t, data] of Object.entries(tiersBackend)) {
            tracker.total_overall_shanks += data.total_shanks;
            tracker.tiers[t] = {
                obtained_shanks: 0,
                total_shanks: data.total_shanks,
                matched_items: new Set()
            };
        }

        // 1. Resolve all eaten items in parallel
        await loadRepo();
        const resolvedFoods = await Promise.all(resStats.eaten.map(async f => {
            const info = await getPrettyItemInfo(f.tag, f.damage);
            return { ...f, ...info };
        }));

        // 2. Cross reference with Tier Database
        for (const f of resolvedFoods) {
            const fullName = f.name + ' ' + f.modshort;
            const shortName = f.name;

            for (const [tierName, tierData] of Object.entries(tiersBackend)) {
                const foundShanks = tierData.foods[fullName] !== undefined ? tierData.foods[fullName] : 
                                   (tierData.foods[shortName] !== undefined ? tierData.foods[shortName] : null);
                
                if (foundShanks !== null) {
                    const matchKey = tierData.foods[fullName] !== undefined ? fullName : shortName;
                    
                    if (!tracker.tiers[tierName].matched_items.has(matchKey)) {
                        tracker.tiers[tierName].matched_items.add(matchKey);
                        tracker.tiers[tierName].obtained_shanks += foundShanks;
                        tracker.obtained_overall_shanks += foundShanks;
                        if(f.count === resStats.playerCount) {
                            tracker.eatenFullCount += foundShanks;
                        }
                    }
                    break;
                }
            }
        }
        
        // Expose globally for switching tiers
        currentTracker = tracker;
        currentTiersDB = tiersBackend;

        // Switch to content view
        document.getElementById("stats-skeleton").style.display = "none";
        document.getElementById("stats-content").style.display = "block";

        // 3. Render Top Dashboard (Live Tracker)
        const total = tracker.total_overall_shanks;
        const obt = tracker.obtained_overall_shanks;
        const rem = total - obt;
        const fullObt = tracker.eatenFullCount;
        
        const pct = total > 0 ? (fullObt / total * 100).toFixed(1) : 0.0;
        const remaining_pct = 100 - pct;
        
        document.getElementById("overall-pct").textContent = `${pct}%`;
        document.getElementById("overall-remaining-pct").textContent = `${remaining_pct}%`;
        document.getElementById("overall-donut-pct").textContent = `${pct}%`;
        document.getElementById("overall-donut").style.setProperty("--pct", `${pct}%`);
        
        document.getElementById("shanks-remaining").textContent = rem;
        document.getElementById("shanks-obtained").textContent = obt;
        
        const heartsObt = Math.floor(obt / 50);
        const heartsRem = Math.floor(rem / 50);
        const untilNext = 50 - (obt % 50);

        document.getElementById("hearts-remaining").textContent = heartsRem;
        document.getElementById("hearts-obtained").textContent = heartsObt;
        document.getElementById("until-next").textContent = untilNext;

        // 4. Render the 4 Small Tier Donuts
        const chartsContainer = document.getElementById("tier-charts-container");
        chartsContainer.innerHTML = "";

        TIER_ORDER.forEach(tier => {
            const data = tracker.tiers[tier];
            const tPct = data.total_shanks > 0 ? (data.obtained_shanks / data.total_shanks * 100).toFixed(1) : 0;
            const tRem = data.total_shanks - data.obtained_shanks;
            
            const card = document.createElement("div");
            card.className = "tier-card";
            card.innerHTML = `
                <h4>${tier}</h4>
                <div class="tier-donut-container">
                    <div class="donut donut-small" style="--pct: ${tPct}%">
                        <div class="donut-content">${tPct}%</div>
                    </div>
                </div>
                <div class="tier-stats">
                    <strong>${tRem}</strong> Shanks Remaining<br>
                    <strong style="color: #f5b041">${data.obtained_shanks}</strong> Shanks Obtained
                </div>
            `;
            chartsContainer.appendChild(card);
        });

        // 5. Render Tier Selector and Table
        renderTierSelector();
        renderTierTable(currentSelectedTier);

    } catch (e) {
        console.error("Error generating stats:", e);
        document.getElementById("stats-skeleton").innerHTML = "<p style='color:red;'>An error occurred loading stats.</p>";
    }
}

function renderTierSelector() {
    const selector = document.getElementById("tier-selector");
    selector.innerHTML = "";
    const tiers = Object.keys(currentTiersDB);
    
    if (!tiers.includes(currentSelectedTier)) {
        currentSelectedTier = tiers[0];
    }
    
    tiers.forEach(tier => {
        const btn = document.createElement("button");
        btn.textContent = tier;
        btn.className = (tier === currentSelectedTier) ? "active" : "";
        btn.addEventListener("click", () => {
            currentSelectedTier = tier;
            renderTierSelector(); 
            renderTierTable(tier);
        });
        selector.appendChild(btn);
    });
}

function renderTierTable(tier) {
    const tbody = document.getElementById("foods-table").querySelector("tbody");
    tbody.innerHTML = "";
    
    if (!currentTiersDB || !currentTracker) return;
    
    const tierData = currentTiersDB[tier];
    const matchedSet = currentTracker.tiers[tier].matched_items;
    
    const foods = Object.entries(tierData.foods);
    
    // Sort logic to easily find missing foods! 
    // Missing foods (false) appear at the top, then sorts by name
    foods.sort((a, b) => {
        const aEaten = matchedSet.has(a[0]);
        const bEaten = matchedSet.has(b[0]);
        if (aEaten === bEaten) {
            return a[0].localeCompare(b[0]);
        }
        return aEaten ? 1 : -1;
    });

    foods.forEach(([foodName, shanks]) => {
        const isEaten = matchedSet.has(foodName);
        const tr = document.createElement("tr");
        
        tr.innerHTML = `
            <td><strong>${foodName}</strong></td>
            <td>${shanks}</td>
            <td class="${isEaten ? 'status-eaten' : 'status-missing'}">${isEaten ? 'Eaten ✓' : 'Not Eaten ❌'}</td>
        `;
        tbody.appendChild(tr);
    });
}