import { Repository } from 'https://shadowtheage.github.io/gtnh/repository.js';
import { ungzip } from 'https://cdn.jsdelivr.net/npm/pako@2.1.0/+esm';

// --- CONFIGURATION: Max Shank Values from the Google Sheet Screenshot ---
// Because the Google Sheet uses hardcoded lists of foods to determine what is 
// "Remaining", we hardcode the target maximums here to recreate it perfectly.
const TIER_TARGETS = {
    'T1 (Raw)': 263 + 68,       // 331 Total Shanks
    'T2 (Basic)': 630 + 30,     // 660 Total Shanks
    'T3 (Intermediate)': 583 + 44, // 627 Total Shanks
    'T4 (Advanced)': 1157 + 107,   // 1264 Total Shanks
};

const CHART_COLORS = {
    obtained: '#9ccc65', // Green
    remaining: '#ef9a9a' // Pink/Red
};

let repo = null;
let charts = {}; // Store Chart instances to destroy/update them

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

// ... (Keep pamFix, manualFix, and modToShort functions exactly as they were in your Vue app) ...
const pamFix = { "harvestcraft:pamcarrotCake": "Carrot Cake" /* ... rest of your pamFix list ... */ };
const manualFix = { "i:BloodArsenal:blood_cake:0": {name: "Blood Cake", mod: "BloodArsenal"} /* ... */ };

function modToShort(mod) {
    if (mod === 'minecraft') return '(Vanilla)';
    if (mod === 'harvestcraft') return '(Pam)';
    return `(${mod})`; // Fallback wrapper
}

// THE CATEGORIZER: A heuristic to replicate the Google Sheet manually categorized lists. 
// For 100% exact parity, you could replace this with a large JSON dictionary exported from the sheet.
function determineTier(name, mod, hunger) {
    const n = name.toLowerCase();
    if (mod === '(Vanilla)' || mod === '(Natura)' || (mod === '(Pam)' && hunger <= 2)) return 'T1 (Raw)';
    if ((mod === '(Pam)' && hunger > 2 && hunger <= 5) || n.includes('cooked') || n.includes('baked') || n.includes('toast')) return 'T2 (Basic)';
    if (n.includes('dough') || n.includes('stew') || n.includes('soup') || (hunger > 5 && hunger <= 8)) return 'T3 (Intermediate)';
    if (n.includes('cake') || n.includes('feast') || n.includes('burger') || n.includes('pizza') || hunger > 8) return 'T4 (Advanced)';
    return 'Other';
}

async function getPrettyItemInfo(itemTag, damage) {
    const r = await loadRepo();
    if (!r) return { name: itemTag, modshort: modToShort(itemTag.split(':')[0]) };

    const itemRepoTag = `i:${itemTag}:${damage}`;
    let item = r.GetById(itemRepoTag) || r.GetById(`i:${itemTag}Item:${damage}`) || manualFix[itemRepoTag];
    
    let name = item ? item.name : (pamFix[itemTag] || itemTag);
    let modshort = modToShort(item ? item.mod : itemTag.split(':')[0]);
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
    const res = await fetch("/api/players");
    const data = await res.json();
    const list = document.getElementById("players-list");
    list.innerHTML = "";
    
    data.players.forEach(p => {
        const card = document.createElement("div");
        card.className = "player-card";
        card.innerHTML = `<img src="${p.face_url}"><h3>${p.name}</h3><button>View Stats</button>`;
        card.addEventListener("click", () => showStats(p));
        list.appendChild(card);
    });
}

async function showStats(player) {
    document.getElementById("players-section").style.display = "none";
    document.getElementById("stats-section").style.display = "block";
    document.getElementById("player-header").innerHTML = `<h2>${player.name}'s Stats</h2>`;
    
    const tbody = document.getElementById("foods-table").querySelector("tbody");
    tbody.innerHTML = "<tr><td colspan='4'>Loading and correlating items from DB...</td></tr>";
    
    const res = await fetch(`/api/stats/${player.uuid}`);
    const data = await res.json();
    await loadRepo();
    
    // Initialize Tracker Data
    let tracker = {
        'T1 (Raw)': 0, 'T2 (Basic)': 0, 'T3 (Intermediate)': 0, 'T4 (Advanced)': 0, 'Other': 0
    };
    let totalObtained = 0;
    
    tbody.innerHTML = "";
    
    for (const f of data.eaten) {
        const info = await getPrettyItemInfo(f.tag, f.damage);
        const tier = determineTier(info.name, info.modshort, f.hunger);
        
        // Add to stats
        if (tracker[tier] !== undefined) tracker[tier] += f.hunger;
        totalObtained += f.hunger;
        
        // Render table
        tbody.innerHTML += `
            <tr>
                <td><strong>${info.name}</strong><br><small style="color:#888">${f.tag}</small></td>
                <td><span class="tier-badge">${tier}</span></td>
                <td>${info.modshort}</td>
                <td>${f.hunger}</td>
            </tr>
        `;
    }
    
    renderDashboard(tracker, totalObtained);
}

function renderDashboard(tracker, totalObtained) {
    // 1. Process Main Dashboard Math
    const overallTarget = TIER_TARGETS['T1 (Raw)'] + TIER_TARGETS['T2 (Basic)'] + TIER_TARGETS['T3 (Intermediate)'] + TIER_TARGETS['T4 (Advanced)'];
    const totalRem = Math.max(0, overallTarget - totalObtained);
    const totalPercent = ((totalObtained / overallTarget) * 100).toFixed(1);
    
    const heartsObtained = Math.floor(totalObtained / 50);
    const heartsRem = Math.floor(overallTarget / 50) - heartsObtained;
    const untilNext = 50 - (totalObtained % 50);

    // Update Text DOM
    document.getElementById('main-obt').innerText = totalObtained;
    document.getElementById('main-rem').innerText = totalRem;
    document.getElementById('main-percent').innerText = `${totalPercent}%`;
    document.getElementById('hearts-obt').innerText = heartsObtained;
    document.getElementById('hearts-rem').innerText = heartsRem;
    document.getElementById('until-next').innerText = untilNext;

    drawChart('main-chart', totalObtained, totalRem);

    // 2. Process Tiers
    ['T1', 'T2', 'T3', 'T4'].forEach(tierId => {
        const fullTier = tierId === 'T1' ? 'T1 (Raw)' : tierId === 'T2' ? 'T2 (Basic)' : tierId === 'T3' ? 'T3 (Intermediate)' : 'T4 (Advanced)';
        const obt = tracker[fullTier];
        const tgt = TIER_TARGETS[fullTier];
        const rem = Math.max(0, tgt - obt);
        const pct = ((obt / tgt) * 100).toFixed(1);
        
        document.getElementById(`${tierId.toLowerCase()}-obt`).innerText = obt;
        document.getElementById(`${tierId.toLowerCase()}-rem`).innerText = rem;
        document.getElementById(`${tierId.toLowerCase()}-percent`).innerText = `${pct}%`;
        
        drawChart(`${tierId.toLowerCase()}-chart`, obt, rem);
    });
}

function drawChart(canvasId, obtained, remaining) {
    if (charts[canvasId]) charts[canvasId].destroy(); // Clear existing chart
    
    const ctx = document.getElementById(canvasId).getContext('2d');
    charts[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Obtained', 'Remaining'],
            datasets: [{
                data: [obtained, remaining],
                backgroundColor: [CHART_COLORS.obtained, CHART_COLORS.remaining],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '70%',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: true }
            }
        }
    });
}