"""
================================================================================
GLOBAL TRADE ROUTE DISRUPTION MONITOR
Institutional Economic & Geopolitical Scenario Intelligence Dashboard
Focus: Maritime Supply Chains, Global Chokepoints, and Impact on India
================================================================================
"""

import dash
from dash import dcc, html, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import networkx as nx
import textwrap

# ==============================================================================
# 1. DATASET: MAJOR MARITIME CHOKEPOINTS & SHIPPING CORRIDORS
# ==============================================================================

ROUTES_DATA = {
    "suez": {
        "name": "Suez Canal Corridor",
        "type": "Canal Chokepoint",
        "region": "Red Sea / Mediterranean",
        "importance": "Handles ~12-15% of global trade and ~30% of global container volume.",
        "india_relevance": "Carries ~35% of India's total merchandise trade ($200B+ annually), including engineering goods, textiles, and chemicals to Europe/US.",
        "weight_to_india": 26.0,
        "default_state": "OPEN",
        "waypoints": [
            (51.92, 4.47),    # Rotterdam
            (49.5, -0.1),     # English Channel
            (36.14, -5.35),   # Gibraltar
            (37.5, 11.5),     # Central Med
            (31.25, 32.3),    # Port Said (Suez North)
            (29.97, 32.55),   # Suez South
            (22.0, 38.0),     # Red Sea
            (12.58, 43.33),   # Bab-el-Mandeb
            (12.0, 50.0),     # Gulf of Aden
            (15.0, 62.0),     # Arabian Sea
            (18.95, 72.82)    # Mumbai (Nhava Sheva)
        ],
        "chokepoint_coord": (30.58, 32.26),
        "primary_alternative": "cape_good_hope",
        "network_edge": ("Mediterranean", "Red_Sea")
    },
    "hormuz": {
        "name": "Strait of Hormuz",
        "type": "Maritime Strait",
        "region": "Persian Gulf / Arabian Sea",
        "importance": "World's most critical energy artery. Approximately 20-21 million barrels/day (~21% of global petroleum consumption).",
        "india_relevance": "Critical vulnerability: Over 60% of India's crude imports, ~90% of LPG imports, and ~55% of LNG imports transit this 21-mile strait.",
        "weight_to_india": 38.0,
        "default_state": "OPEN",
        "waypoints": [
            (27.0, 50.0),     # Persian Gulf (Ras Tanura)
            (26.56, 56.25),   # Strait of Hormuz
            (24.5, 58.5),     # Gulf of Oman
            (22.0, 65.0),     # North Arabian Sea
            (22.75, 69.7)     # Mundra / Kandla Port
        ],
        "chokepoint_coord": (26.56, 56.25),
        "primary_alternative": "east_west_pipeline_gulf",
        "network_edge": ("Persian_Gulf", "Arabian_Sea")
    },
    "malacca": {
        "name": "Strait of Malacca",
        "type": "Maritime Strait",
        "region": "Southeast Asia / Indo-Pacific",
        "importance": "Primary conduit connecting the Indian Ocean with the Pacific. ~85,000 vessels per year; 25% of all traded goods.",
        "india_relevance": "Connects India to East Asian manufacturing giants (China, Japan, South Korea, Taiwan). Vital for electronics, APIs, and critical metals.",
        "weight_to_india": 22.0,
        "default_state": "OPEN",
        "waypoints": [
            (13.08, 80.27),   # Chennai Port
            (6.0, 94.0),      # Great Channel / Andaman Sea
            (3.0, 100.5),     # Strait of Malacca
            (1.35, 103.82),   # Singapore
            (10.0, 110.0),    # South China Sea
            (22.3, 114.17),   # Hong Kong
            (31.23, 121.47)   # Shanghai
        ],
        "chokepoint_coord": (2.5, 101.5),
        "primary_alternative": "sunda_lombok",
        "network_edge": ("Bay_of_Bengal", "South_China_Sea")
    },
    "bab_el_mandeb": {
        "name": "Bab-el-Mandeb Strait",
        "type": "Maritime Strait",
        "region": "Horn of Africa / Red Sea",
        "importance": "Gatekeeper to the southern entrance of the Red Sea; critical bridge between Indian Ocean and Suez Canal.",
        "india_relevance": "Key bottleneck for bilateral trade with Europe and North Africa. Vulnerable to maritime terrorism, asymmetric strikes, and war-risk premiums.",
        "weight_to_india": 24.0,
        "default_state": "OPEN",
        "waypoints": [
            (18.95, 72.82),   # Mumbai
            (13.5, 48.0),     # Gulf of Aden
            (12.58, 43.33),   # Bab-el-Mandeb
            (18.0, 40.0),     # Southern Red Sea
            (27.0, 35.0)      # Northern Red Sea
        ],
        "chokepoint_coord": (12.58, 43.33),
        "primary_alternative": "cape_good_hope",
        "network_edge": ("Gulf_of_Aden", "Red_Sea")
    },
    "cape_good_hope": {
        "name": "Cape of Good Hope Route",
        "type": "Oceanic Bypass Corridor",
        "region": "Southern Africa / South Atlantic",
        "importance": "The historical primary maritime detour circumventing both Suez and Bab-el-Mandeb.",
        "india_relevance": "Serves as the only viable megavessel fallback when the Red Sea is shuttered. Adds 10-15 transit days and 3,500 nautical miles.",
        "weight_to_india": 12.0,
        "default_state": "OPEN",
        "waypoints": [
            (51.92, 4.47),    # Rotterdam
            (28.0, -16.0),    # Canary Islands
            (4.0, -10.0),     # Gulf of Guinea Offshore
            (-15.0, 5.0),     # South Atlantic Ocean
            (-34.35, 18.47),  # Cape of Good Hope
            (-30.0, 35.0),    # East Coast South Africa
            (-10.0, 52.0),    # Western Indian Ocean
            (9.93, 76.26),    # Kochi Port
            (18.95, 72.82)    # Mumbai
        ],
        "chokepoint_coord": (-34.35, 18.47),
        "primary_alternative": "suez",
        "network_edge": ("Atlantic_Hub", "Indian_Ocean_South")
    },
    "panama": {
        "name": "Panama Canal",
        "type": "Interoceanic Canal",
        "region": "Central America",
        "importance": "Links Atlantic and Pacific Oceans; handles ~5% of global trade and 40% of US containerized goods.",
        "india_relevance": "Moderate direct relevance. Affects indirect imports of US crude/LPG, agricultural grains, and machinery routed via the Pacific.",
        "weight_to_india": 8.0,
        "default_state": "OPEN",
        "waypoints": [
            (40.71, -74.0),   # New York
            (25.0, -75.0),    # Bahamas Passage
            (9.10, -79.69),   # Panama Canal
            (5.0, -90.0),     # Eastern Pacific
            (15.0, -120.0),   # Central Pacific
            (35.67, 139.65)   # Tokyo
        ],
        "chokepoint_coord": (9.10, -79.69),
        "primary_alternative": "cape_horn",
        "network_edge": ("Atlantic_North", "Pacific_Central")
    },
    "sunda_lombok": {
        "name": "Sunda & Lombok Straits",
        "type": "Deepwater Archipelagic Straits",
        "region": "Indonesian Archipelago",
        "importance": "Deep-draft alternative corridors to Malacca. Accommodates giant Capesize and VLCC bulkers that cannot clear Malacca's shallow draft.",
        "india_relevance": "Crucial bypass when Malacca experiences naval blockades or severe piracy. Adds 3-5 steaming days from Australian and Pacific ports.",
        "weight_to_india": 10.0,
        "default_state": "OPEN",
        "waypoints": [
            (13.08, 80.27),   # Chennai
            (0.0, 90.0),      # Equatorial Indian Ocean
            (-6.0, 105.0),    # Sunda Strait
            (-8.5, 115.7),    # Lombok Strait
            (0.0, 120.0),     # Makassar Strait
            (20.0, 125.0),    # Philippine Sea
            (31.23, 121.47)   # Shanghai
        ],
        "chokepoint_coord": (-8.5, 115.7),
        "primary_alternative": "malacca",
        "network_edge": ("Indian_Ocean_East", "Philippine_Sea")
    },
    "northern_sea_route": {
        "name": "Northern Sea Route (Arctic)",
        "type": "Polar Maritime Corridor",
        "region": "Arctic Ocean / Siberian Coast",
        "importance": "Shaves ~40% off the distance between European and East Asian ports during ice-free summer windows.",
        "india_relevance": "Strategic corridor for discounted Russian Arctic crude (Novy Port, Prirazlomnoye) and LNG from the Yamal peninsula heading to India/Asia.",
        "weight_to_india": 6.0,
        "default_state": "OPEN",
        "waypoints": [
            (51.92, 4.47),    # Rotterdam
            (68.0, 14.0),     # Norwegian Sea
            (72.0, 35.0),     # Barents Sea (Murmansk)
            (76.0, 80.0),     # Kara Sea
            (75.0, 135.0),    # Laptev Sea
            (65.0, -170.0),   # Bering Strait
            (45.0, 150.0),    # Sea of Okhotsk
            (35.67, 139.65)   # Tokyo
        ],
        "chokepoint_coord": (72.0, 60.0),
        "primary_alternative": "suez",
        "network_edge": ("Atlantic_Arctic", "Pacific_North")
    },
    "english_channel": {
        "name": "English Channel & North Sea",
        "type": "Maritime Bottleneck",
        "region": "Northwest Europe",
        "importance": "Busiest shipping lane globally with over 500 vessel transits per day serving Rotterdam, Antwerp, and Hamburg.",
        "india_relevance": "Terminal gateway for Indian engineering, chemical, and apparel consignments entering mainland northern Europe.",
        "weight_to_india": 7.0,
        "default_state": "OPEN",
        "waypoints": [
            (50.5, -1.0),     # English Channel
            (51.2, 2.0),      # Dover Strait
            (53.0, 4.0)       # North Sea Approaches
        ],
        "chokepoint_coord": (51.2, 2.0),
        "primary_alternative": "round_scotland_bypass",
        "network_edge": ("Atlantic_North", "North_Sea")
    },
    "trans_pacific": {
        "name": "Trans-Pacific Shipping Corridor",
        "type": "Oceanic Container Corridor",
        "region": "Pacific Basin",
        "importance": "Backbone of modern consumer electronics and goods trade between East Asia and North American western ports.",
        "india_relevance": "Indirect impact on global container fleet equilibrium; delays tie up blank sailings and spike global spot freight rates.",
        "weight_to_india": 9.0,
        "default_state": "OPEN",
        "waypoints": [
            (31.23, 121.47),  # Shanghai
            (35.0, 150.0),    # North Pacific Basin
            (37.8, -122.4),   # San Francisco / Long Beach
            (33.74, -118.27)
        ],
        "chokepoint_coord": (38.0, -160.0),
        "primary_alternative": "trans_pacific_polar",
        "network_edge": ("East_Asia_Hub", "US_West_Coast")
    }
}

# ==============================================================================
# 2. DATASET: MAJOR PORTS (INDIAN & GLOBAL)
# ==============================================================================

PORTS_DATA = {
    "Mumbai_Nhava_Sheva": {"lat": 18.95, "lon": 72.95, "country": "India", "type": "Indian Major Port", "desc": "India's premier container hub (JNPA)."},
    "Mundra": {"lat": 22.75, "lon": 69.70, "country": "India", "type": "Indian Major Port", "desc": "Largest commercial and container gateway in India."},
    "Kandla_Deendayal": {"lat": 23.01, "lon": 70.22, "country": "India", "type": "Indian Major Port", "desc": "Critical crude oil, POL and dry bulk terminal."},
    "Kochi": {"lat": 9.93, "lon": 76.26, "country": "India", "type": "Indian Major Port", "desc": "Southern transshipment terminal (Vallarpadam)."},
    "Chennai": {"lat": 13.08, "lon": 80.27, "country": "India", "type": "Indian Major Port", "desc": "Primary manufacturing & automotive export corridor."},
    "Visakhapatnam": {"lat": 17.68, "lon": 83.21, "country": "India", "type": "Indian Major Port", "desc": "Eastern industrial gateway for steel, petroleum, and coal."},
    "Kolkata_Haldia": {"lat": 22.03, "lon": 88.08, "country": "India", "type": "Indian Major Port", "desc": "Riverine terminal serving landlocked states & eastern hinterlands."},
    "Tuticorin_VOC": {"lat": 8.76, "lon": 78.13, "country": "India", "type": "Indian Major Port", "desc": "Major deep-sea port handling textiles and agricultural goods."},
    "Rotterdam": {"lat": 51.92, "lon": 4.47, "country": "Netherlands", "type": "Global Port", "desc": "Largest seaport in Europe."},
    "Singapore": {"lat": 1.35, "lon": 103.82, "country": "Singapore", "type": "Global Port", "desc": "World's largest bunkering & transshipment hub."},
    "Shanghai": {"lat": 31.23, "lon": 121.47, "country": "China", "type": "Global Port", "desc": "World's highest volume container port."},
    "Ras_Tanura": {"lat": 26.65, "lon": 50.16, "country": "Saudi Arabia", "type": "Global Port", "desc": "World's largest offshore crude oil loading terminal."}
}

# ==============================================================================
# 3. ALTERNATIVE ROUTE DYNAMICS & GRAPH TOPOLOGY
# ==============================================================================

ALTERNATIVE_SPECS = {
    "suez_via_cape": {
        "name": "Cape of Good Hope Oceanic Transit",
        "triggered_by": ["suez", "bab_el_mandeb"],
        "required_open": ["cape_good_hope"],
        "origin_destination": "Europe / US East Coast ⟷ Indian Subcontinent & Asia",
        "additional_distance_nm": "+3,500 – 4,200 nautical miles",
        "additional_transit_days": "+10 to 14 days",
        "bunker_cost_delta": "+$400,000 – $800,000 per voyage (fuel burn)",
        "key_constraints": "Severe container equipment imbalances, doubled voyage fuel, port congestion in Durban/Cape Town, heavy southern swells.",
        "waypoints": ROUTES_DATA["cape_good_hope"]["waypoints"]
    },
    "malacca_via_sunda": {
        "name": "Sunda & Lombok Deepwater Bypass",
        "triggered_by": ["malacca"],
        "required_open": ["sunda_lombok"],
        "origin_destination": "Indian Ocean ⟷ East Asia / North Pacific",
        "additional_distance_nm": "+1,200 – 1,800 nautical miles",
        "additional_transit_days": "+3 to 5 days",
        "bunker_cost_delta": "+$150,000 – $250,000 per voyage",
        "key_constraints": "Restricted vessel clearance in Sunda; severe currents in Lombok; limited bunkering infrastructure outside Singapore.",
        "waypoints": ROUTES_DATA["sunda_lombok"]["waypoints"]
    },
    "hormuz_pipeline_bypass": {
        "name": "Saudi Petroline (East-West) & Fujairah Bypass",
        "triggered_by": ["hormuz"],
        "required_open": [],  # Land-based infrastructure
        "origin_destination": "Arabian Gulf Crude Fields ⟷ Red Sea / Gulf of Oman",
        "additional_distance_nm": "Pipeline Transit (0 NM)",
        "additional_transit_days": "+2 to 4 days (tanker relocking)",
        "bunker_cost_delta": "Pipeline tariff + loading surcharges ($2-4/bbl)",
        "key_constraints": "Fixed capacity ceiling (~5 million bbl/day against a 21m bbl/day disruption). Completely unable to evacuate LNG or LPG volumes.",
        "waypoints": [
            (26.0, 50.0),   # Abqaiq
            (24.5, 46.5),   # Riyadh terminal
            (24.0, 38.0),   # Yanbu Port (Red Sea)
            (20.0, 60.0),   # Bypassed offshore tanker meetup
            (18.95, 72.82)  # Mumbai
        ]
    }
}

# ==============================================================================
# 4. ECONOMIC & INDUSTRY IMPACT TAXONOMY
# ==============================================================================

HOUSEHOLD_BASELINE = {
    "fuel": {"name": "Petrol & Diesel (Transport)", "base_status": "Low", "weight": 20},
    "lpg": {"name": "Household LPG (Cooking Gas)", "base_status": "Low", "weight": 20},
    "food": {"name": "Edible Oils, Cereals & Vegetables", "base_status": "Low", "weight": 15},
    "electronics": {"name": "Consumer Electronics & Mobiles", "base_status": "Low", "weight": 10},
    "automobiles": {"name": "Automobiles & 2-Wheelers", "base_status": "Low", "weight": 8},
    "pharma": {"name": "Essential Medicines & Healthcare", "base_status": "Low", "weight": 9},
    "consumer_goods": {"name": "Imported Goods & Packaging", "base_status": "Low", "weight": 6},
    "fertilizer": {"name": "Fertilizers & Crop Production Inputs", "base_status": "Low", "weight": 12}
}

INDUSTRIES_TAXONOMY = [
    {
        "id": "oil_gas",
        "name": "Oil & Gas Refining",
        "disrupted_by": ["hormuz", "bab_el_mandeb", "suez"],
        "dependency": "Crucial import reliance on crude oil (87% imported; ~60% from Persian Gulf).",
        "mechanism": "Force majeure from Gulf terminals triggers immediate crude feedstock shortages, forcing domestic refineries to cut throughput.",
        "exposure": "High Import Exposure (Crude) / High Export Exposure (Refined Diesel/Naphtha)",
        "alternative": "West African (WAF) or Russian Urals via Cape of Good Hope, but at substantial freight premiums."
    },
    {
        "id": "petrochem",
        "name": "Petrochemicals & Plastics",
        "disrupted_by": ["hormuz", "malacca"],
        "dependency": "Imported naphtha, ethane, and monomer feedstocks from the Middle East.",
        "mechanism": "Feedstock delivery failures force plants to operate at fractional capacity, choking packaging and polymer supply chains.",
        "exposure": "Severe Import Dependency",
        "alternative": "Spot domestic polymer blending; sourcing from alternative Southeast Asian crackers."
    },
    {
        "id": "fertilizers",
        "name": "Fertilizers & Agriculture",
        "disrupted_by": ["hormuz", "bab_el_mandeb"],
        "dependency": "Middle Eastern urea, rock phosphate from Jordan/Egypt, and ammonia from Gulf facilities.",
        "mechanism": "Interruption halts fertilizer manufacturing ahead of sowing cycles, driving domestic shortages and inflating agricultural subsidies.",
        "exposure": "Direct Import Sourcing Bottleneck",
        "alternative": "Emergency domestic gas reallocation and Canadian/Moroccan potash sourcing via extended sea lanes."
    },
    {
        "id": "electronics",
        "name": "Electronics & Hardware Assembly",
        "disrupted_by": ["malacca", "sunda_lombok"],
        "dependency": "Components, PCBs, semiconductor assemblies, and displays from Taiwan, China, and South Korea.",
        "mechanism": "Stoppage along East Asian sea lanes starves Indian EMS assembly plants, creating consumer electronics shortages within 14-21 days.",
        "exposure": "Extreme Import Dependency (~70% of BOM value)",
        "alternative": "Air freight for subassemblies, eroding manufacturing margins and swelling retail costs."
    },
    {
        "id": "automotive",
        "name": "Automobile & Auto Components",
        "disrupted_by": ["suez", "bab_el_mandeb", "malacca"],
        "dependency": "Electronic chips and subassemblies from East Asia; specialized steel and precision gearboxes from Germany/EU.",
        "mechanism": "Container equipment shortages and 15-day transit delays disrupt Just-In-Time (JIT) assembly lines across Pune, Chennai, and Manesar.",
        "exposure": "Balanced Import/Export Dependency",
        "alternative": "Buffer stocking and domestic substitute qualification, with lead-times of 3 to 6 months."
    },
    {
        "id": "pharma",
        "name": "Pharmaceuticals & Healthcare",
        "disrupted_by": ["malacca", "suez", "bab_el_mandeb"],
        "dependency": "Key Starting Materials (KSMs) and Active Pharmaceutical Ingredients (APIs) from China; generic formulation exports to Europe/US.",
        "mechanism": "Raw material arrivals stall; outbound cold-chain container consignments to Europe face extended routes and shelf-life degradation.",
        "exposure": "Import-Reliant for APIs (~65%) / High-Volume Finished Formulations Exporter",
        "alternative": "Air cargo for temperature-sensitive drugs; diversified sourcing via domestic PLI-funded API complexes."
    },
    {
        "id": "textiles",
        "name": "Textiles & Ready-Made Garments",
        "disrupted_by": ["suez", "bab_el_mandeb"],
        "dependency": "Apparel and yarn exports to European Union retail chains and high-street brands.",
        "mechanism": "Fast-fashion seasonal deadlines are missed due to delays around the Cape of Good Hope, causing order cancellations and penal discounts.",
        "exposure": "High Export Exposure",
        "alternative": "No viable maritime shortcut; air-lifting samples to preserve buyer contracts."
    },
    {
        "id": "shipping_logistics",
        "name": "Shipping & Freight Logistics",
        "disrupted_by": ["suez", "hormuz", "malacca", "bab_el_mandeb"],
        "dependency": "Unimpeded vessel circulation, bunker availability, and marine insurance underwriting.",
        "mechanism": "War-risk surcharges surge by 400-800%; container turnaround cycles stretch, trapping trade finance and working capital.",
        "exposure": "Direct Sectoral Transmission",
        "alternative": "Repositioning fleets to regional cabotage and feeder services."
    }
]

# ==============================================================================
# 5. GRAPH ENGINE & IMPACT SIMULATION MODEL
# ==============================================================================

def build_trade_network(closed_routes):
    """
    Constructs a NetworkX graph of maritime connectivity, evaluates route reachability,
    and identifies dynamic alternative path activations.
    """
    G = nx.Graph()
    
    # Establish base regional nodes
    hubs = [
        "Rotterdam", "Gibraltar", "Mediterranean", "Red_Sea", "Gulf_of_Aden",
        "Persian_Gulf", "Arabian_Sea", "Bay_of_Bengal", "South_China_Sea",
        "Atlantic_Hub", "Indian_Ocean_South", "Atlantic_North", "Pacific_Central",
        "Indian_Ocean_East", "Philippine_Sea", "East_Asia_Hub", "US_West_Coast"
    ]
    for h in hubs:
        G.add_node(h)
        
    # Add graph edges for each open route
    for r_id, r_info in ROUTES_DATA.items():
        if r_id not in closed_routes:
            u, v = r_info["network_edge"]
            G.add_edge(u, v, route_id=r_id, weight=1.0)
            
    # Check whether critical alternatives should trigger
    active_alternatives = []
    
    # Check Cape of Good Hope trigger
    if ("suez" in closed_routes or "bab_el_mandeb" in closed_routes) and ("cape_good_hope" not in closed_routes):
        active_alternatives.append("suez_via_cape")
        
    # Check Sunda/Lombok trigger
    if "malacca" in closed_routes and ("sunda_lombok" not in closed_routes):
        active_alternatives.append("malacca_via_sunda")
        
    # Check Hormuz Pipeline bypass
    if "hormuz" in closed_routes:
        active_alternatives.append("hormuz_pipeline_bypass")
        
    return G, active_alternatives


def calculate_india_disruption_index(closed_routes, active_alternatives):
    """
    Calculates the normalized India Trade Disruption Index (0-100).
    """
    if not closed_routes:
        return 0.0, "Minimal", "Optimal Maritime Freedom"

    raw_weight = sum(ROUTES_DATA[r]["weight_to_india"] for r in closed_routes if r in ROUTES_DATA)
    
    # Compounding penalty for multiple simultaneous disruptions
    compounding_factor = 1.0 + (len(closed_routes) - 1) * 0.12
    
    # Mitigation discount provided by viable alternative routes
    mitigation_discount = 0.0
    if "suez_via_cape" in active_alternatives:
        mitigation_discount += 0.08
    if "malacca_via_sunda" in active_alternatives:
        mitigation_discount += 0.05
    if "hormuz_pipeline_bypass" in active_alternatives:
        mitigation_discount += 0.04
        
    score = raw_weight * compounding_factor * (1.0 - mitigation_discount)
    normalized_score = min(round(score, 1), 100.0)
    
    if normalized_score <= 20.0:
        band = "Low"
        summary = "Localized or absorbable supply chain friction."
    elif normalized_score <= 40.0:
        band = "Moderate"
        summary = "Noticeable maritime delays; freight surcharges emerging."
    elif normalized_score <= 60.0:
        band = "Elevated"
        summary = "Broad export delays, working capital friction, and initial consumer price inflation."
    elif normalized_score <= 80.0:
        band = "High"
        summary = "Critical stress on balance of trade, sovereign energy inventories, and industrial output."
    else:
        band = "Severe"
        summary = "Emergency economic crisis: acute energy rationing, manufacturing curtailments, and surging inflation."
        
    return normalized_score, band, summary


def evaluate_household_impacts(closed_routes):
    """Evaluates dynamic household impacts across 8 consumer-facing verticals."""
    impacts = {}
    for key, baseline in HOUSEHOLD_BASELINE.items():
        impact_level = "Low"
        rationale = "Supplies and consumer pricing remain stable under normal baseline operations."
        
        if key == "fuel":
            if "hormuz" in closed_routes:
                impact_level = "Severe"
                rationale = "Over 60% of crude imports face an immediate bottleneck. Domestic pump prices will face severe upward pressure."
            elif "bab_el_mandeb" in closed_routes or "suez" in closed_routes:
                impact_level = "Moderate"
                rationale = "Longer transit for Russian and Mediterranean crude adds freight and tanker charter costs."
        elif key == "lpg":
            if "hormuz" in closed_routes:
                impact_level = "Severe"
                rationale = "Immediate supply threat: ~90% of imported household cooking LPG transits Hormuz."
        elif key == "fertilizer":
            if "hormuz" in closed_routes and ("suez" in closed_routes or "bab_el_mandeb" in closed_routes):
                impact_level = "Severe"
                rationale = "Dual bottleneck: Middle Eastern ammonia and Egyptian/Jordanian rock phosphate are stranded."
            elif "hormuz" in closed_routes:
                impact_level = "High"
                rationale = "Gulf urea shipments choked. Government subsidy bill escalates; rural planting costs surge."
            elif "bab_el_mandeb" in closed_routes:
                impact_level = "Moderate"
                rationale = "Red Sea phosphate exports delayed, requiring longer journeys around southern Africa."
        elif key == "food":
            if "hormuz" in closed_routes or "suez" in closed_routes:
                impact_level = "Elevated" if ("hormuz" in closed_routes and "suez" in closed_routes) else "Moderate"
                rationale = "Indirect inflation driven by elevated tractor fuel costs, compounded by international delays in imported sunflower and palm oil."
        elif key == "electronics":
            if "malacca" in closed_routes:
                impact_level = "Severe"
                rationale = "Primary semiconductor and component pipelines from East Asia severed. Consumer phone and appliance prices surge."
        elif key == "automobiles":
            if "malacca" in closed_routes or "suez" in closed_routes:
                impact_level = "Moderate"
                rationale = "Delays in European precision subassemblies and East Asian microcontrollers stretch dealership waiting periods."
        elif key == "pharma":
            if "malacca" in closed_routes:
                impact_level = "High"
                rationale = "Over 65% of Active Pharmaceutical Ingredients (APIs) sourced from East Asia are blocked."
            elif "suez" in closed_routes or "bab_el_mandeb" in closed_routes:
                impact_level = "Moderate"
                rationale = "Outbound shipments of finished formulations to EU/US face extended voyage durations."
        elif key == "consumer_goods":
            if len(closed_routes) >= 2:
                impact_level = "High"
                rationale = "Surging ocean container freight rates are passed directly to retail consumers across imported goods."
            elif len(closed_routes) == 1:
                impact_level = "Moderate"
                rationale = "Retailers experience delayed seasonal catalog arrivals and localized stockouts."
                
        impacts[key] = {
            "name": baseline["name"],
            "level": impact_level,
            "rationale": rationale
        }
    return impacts

# ==============================================================================
# 6. DASHBOARD APPLICATION INSTANTIATION & LAYOUT
# ==============================================================================

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True
)
app.title = "Global Maritime Chokepoint & Trade Disruption Monitor"

TERMINAL_STYLE = {
    "bg_dark": "#0B0F19",
    "card_bg": "#121826",
    "card_border": "#1E293B",
    "accent_blue": "#38BDF8",
    "accent_green": "#10B981",
    "accent_red": "#EF4444",
    "accent_yellow": "#F59E0B",
    "text_main": "#F8FAFC",
    "text_muted": "#94A3B8"
}

def create_header():
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Span("⚓ GLOBAL MARITIME INTELLIGENCE", style={"color": TERMINAL_STYLE["accent_blue"], "fontWeight": "700", "fontSize": "0.8rem", "letterSpacing": "1.5px"}),
                        html.H4("Trade Route Disruption & Sovereign Risk Monitor", className="mb-0 text-white", style={"fontWeight": "700", "letterSpacing": "-0.5px"}),
                        html.Small("Real-time scenario simulation: Chokepoints, Alternative Navigational Arcs & India Macro Exposure", style={"color": TERMINAL_STYLE["text_muted"]})
                    ])
                ], md=6),
                dbc.Col([
                    html.Div(id="header-stats-container", className="d-flex justify-content-md-end gap-3 align-items-center mt-2 mt-md-0")
                ], md=6)
            ], className="w-100 align-items-center")
        ], fluid=True),
        color=TERMINAL_STYLE["card_bg"],
        dark=True,
        className="border-bottom border-secondary py-2 sticky-top",
        style={"borderColor": TERMINAL_STYLE["card_border"]}
    )

def create_map_panel():
    return dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col([
                    html.Span("GEOSPATIAL SITUATIONAL MAP", style={"fontWeight": "700", "fontSize": "0.85rem", "color": TERMINAL_STYLE["accent_blue"], "letterSpacing": "1px"}),
                    html.Span(" — Global Chokepoints & Indian Ocean Port Networks", className="text-muted small")
                ], md=7),
                dbc.Col([
                    html.Div([
                        html.Span("🟢 Active Lane", className="badge bg-dark text-success border border-success me-1"),
                        html.Span("🔴 Closed Lane", className="badge bg-dark text-danger border border-danger me-1"),
                        html.Span("🟡 Alternate Arc", className="badge bg-dark text-warning border border-warning me-1"),
                        html.Span("🔵 Indian Port", className="badge bg-dark text-info border border-info")
                    ], className="text-end small")
                ], md=5)
            ], className="align-items-center")
        ], style={"backgroundColor": TERMINAL_STYLE["card_bg"], "borderBottom": f"1px solid {TERMINAL_STYLE['card_border']}"}),
        
        dbc.CardBody([
            dcc.Graph(
                id="world-trade-map",
                style={"height": "760px", "width": "100%"},
                config={
                    "displayModeBar": False, # Locks the toolbar
                    "scrollZoom": False,     # Prevents zooming out of frame
                    "doubleClick": False,    # Prevents accidental resets
                    "displaylogo": False
                }
            )
        ], className="p-0")
    ], style={"backgroundColor": TERMINAL_STYLE["card_bg"], "borderColor": TERMINAL_STYLE["card_border"], "borderRadius": "8px"})

def create_control_panel():
    return dbc.Card([
        dbc.CardHeader([
            dbc.Tabs([
                dbc.Tab(label="Disruption Controls", tab_id="tab-controls", active_label_style={"color": TERMINAL_STYLE["accent_blue"], "fontWeight": "bold"}),
                dbc.Tab(label="India Household Impact", tab_id="tab-household", active_label_style={"color": TERMINAL_STYLE["accent_blue"], "fontWeight": "bold"}),
                dbc.Tab(label="Industry Exposure", tab_id="tab-industry", active_label_style={"color": TERMINAL_STYLE["accent_blue"], "fontWeight": "bold"}),
                dbc.Tab(label="Model Notes", tab_id="tab-methodology", active_label_style={"color": TERMINAL_STYLE["accent_blue"], "fontWeight": "bold"})
            ], id="right-panel-tabs", active_tab="tab-controls", className="border-0")
        ], style={"backgroundColor": TERMINAL_STYLE["card_bg"], "borderBottom": f"1px solid {TERMINAL_STYLE['card_border']}"}),
        
        dbc.CardBody([
            html.Div(id="tab-content-area", style={"height": "740px", "overflowY": "auto", "paddingRight": "8px"})
        ], className="p-3")
    ], style={"backgroundColor": TERMINAL_STYLE["card_bg"], "borderColor": TERMINAL_STYLE["card_border"], "borderRadius": "8px"})

app.layout = html.Div([
    create_header(),
    dbc.Container([
        dbc.Row([
            dbc.Col(create_map_panel(), lg=7, xl=7, className="mb-3 mb-lg-0"),
            dbc.Col(create_control_panel(), lg=5, xl=5)
        ], className="g-3 mt-1")
    ], fluid=True, className="px-3 pb-3"),
    
    dcc.Store(id="closed-routes-store", data=[])
], style={"backgroundColor": TERMINAL_STYLE["bg_dark"], "minHeight": "100vh", "fontFamily": "Segoe UI, Inter, Roboto, sans-serif"})

# ==============================================================================
# 7. MAP GENERATION ENGINE (CURVED SHIPPING ARCS & GEOJSON RENDERING)
# ==============================================================================

def generate_arc_points(p1, p2, num_points=35):
    """
    Interpolates smooth, realistic curved arcs between waypoints.
    Includes a fix for the International Date Line crossing bug.
    """
    lon1, lon2 = p1[1], p2[1]
    
    # FIX FOR PACIFIC ROUTES: Prevent interpolation from wrapping backwards across the earth
    if lon2 - lon1 > 180:
        lon1 += 360
    elif lon1 - lon2 > 180:
        lon2 += 360
        
    lats = np.linspace(p1[0], p2[0], num_points)
    lons = np.linspace(lon1, lon2, num_points)
    
    lat_delta = p2[0] - p1[0]
    lon_delta = lon2 - lon1
    
    # Reduced the curvature slightly so routes don't bend aggressively over landmasses
    curvature = 0.08 * np.sin(np.pi * np.linspace(0, 1, num_points))
    
    arc_lats = lats - curvature * lon_delta
    arc_lons = lons + curvature * lat_delta
    
    return list(arc_lats), list(arc_lons)


def build_map_figure(closed_routes, active_alternatives):
    """
    Constructs the master Plotly Geospatial figure with dark bathymetry.
    """
    fig = go.Figure()

    # Layer 1: Render All Major Maritime Corridors
    for r_id, r_info in ROUTES_DATA.items():
        is_closed = r_id in closed_routes
        wps = r_info["waypoints"]
        
        all_lats = []
        all_lons = []
        for i in range(len(wps) - 1):
            arc_lats, arc_lons = generate_arc_points(wps[i], wps[i+1], num_points=15)
            all_lats.extend(arc_lats)
            all_lons.extend(arc_lons)
            
        color = TERMINAL_STYLE["accent_red"] if is_closed else TERMINAL_STYLE["accent_blue"]
        width = 3.5 if is_closed else 2.2
        dash_style = "dash" if is_closed else "solid"
        opacity = 0.85 if is_closed else 0.70
        status_label = "CLOSED (BLOCKED)" if is_closed else "OPEN (OPERATIONAL)"

        wrapped_relevance = "<br>".join(textwrap.wrap(r_info['india_relevance'], width=60))
        wrapped_importance = "<br>".join(textwrap.wrap(r_info['importance'], width=60))

        hover_text = (
            f"<b>{r_info['name'].upper()}</b><br>"
            f"<b>Status:</b> {status_label}<br>"
            f"<b>Type:</b> {r_info['type']}<br>"
            f"<b>Geopolitical Region:</b> {r_info['region']}<br>"
            f"<b>Sovereign Relevance to India:</b><br>{wrapped_relevance}<br><br>"
            f"<b>Global Throughput Significance:</b><br>{wrapped_importance}"
        )

        fig.add_trace(go.Scattergeo(
            lon=all_lons,
            lat=all_lats,
            mode='lines',
            line=dict(width=width, color=color, dash=dash_style),
            opacity=opacity,
            name=r_info["name"],
            hoverinfo='text',
            hovertext=hover_text,
            showlegend=False
        ))

        # Add chokepoint icon markers
        cp_lat, cp_lon = r_info["chokepoint_coord"]
        marker_color = TERMINAL_STYLE["accent_red"] if is_closed else "#38BDF8"
        marker_symbol = "x" if is_closed else "circle"
        marker_size = 11 if is_closed else 6

        fig.add_trace(go.Scattergeo(
            lon=[cp_lon],
            lat=[cp_lat],
            mode='markers',
            marker=dict(size=marker_size, color=marker_color, symbol=marker_symbol, line=dict(width=1.5, color="#FFFFFF")),
            hoverinfo='text',
            hovertext=f"<b>CHOKEPOINT: {r_info['name']}</b><br>Status: {status_label}",
            showlegend=False
        ))

    # Layer 2: Render Dynamic Alternative Routing Arcs (Cyan/Yellow)
    for alt_id in active_alternatives:
        alt_data = ALTERNATIVE_SPECS.get(alt_id)
        if alt_data:
            alt_wps = alt_data["waypoints"]
            alt_lats = []
            alt_lons = []
            for i in range(len(alt_wps) - 1):
                seg_lats, seg_lons = generate_arc_points(alt_wps[i], alt_wps[i+1], num_points=20)
                alt_lats.extend(seg_lats)
                alt_lons.extend(seg_lons)

            wrapped_constraints = "<br>".join(textwrap.wrap(alt_data['key_constraints'], width=60))

            alt_hover = (
                f"<b>ACTIVE DETOUR: {alt_data['name'].upper()}</b><br>"
                f"<b>Corridor:</b> {alt_data['origin_destination']}<br>"
                f"<b>Additional Distance:</b> {alt_data['additional_distance_nm']}<br>"
                f"<b>Transit Penalty:</b> {alt_data['additional_transit_days']}<br>"
                f"<b>Bunker Penalty:</b> {alt_data['bunker_cost_delta']}<br>"
                f"<b>Constraints:</b><br>{wrapped_constraints}"
            )

            fig.add_trace(go.Scattergeo(
                lon=alt_lons,
                lat=alt_lats,
                mode='lines',
                line=dict(width=3.8, color=TERMINAL_STYLE["accent_yellow"], dash="dot"),
                opacity=0.95,
                name=f"Alt: {alt_data['name']}",
                hoverinfo='text',
                hovertext=alt_hover,
                showlegend=False
            ))

    # Layer 3: Render Major Ports & Dedicated Indian Hubs
    for p_name, p_val in PORTS_DATA.items():
        is_india = p_val["country"] == "India"
        p_color = "#38BDF8" if is_india else "#94A3B8"
        p_size = 8 if is_india else 5
        clean_name = p_name.replace("_", " ")

        port_hover = (
            f"<b>PORT: {clean_name}</b> ({p_val['country']})<br>"
            f"<b>Classification:</b> {p_val['type']}<br>"
            f"<b>Operations:</b> {p_val['desc']}"
        )

        fig.add_trace(go.Scattergeo(
            lon=[p_val["lon"]],
            lat=[p_val["lat"]],
            mode='markers+text',
            text=[clean_name if is_india else ""],
            textposition="top right",
            textfont=dict(size=9, color="#E2E8F0"),
            marker=dict(size=p_size, color=p_color, line=dict(width=1, color="#0B0F19")),
            hoverinfo='text',
            hovertext=port_hover,
            showlegend=False
        ))

    # Layer 4: Map Projection & Dark Bathymetry Styling (3D Globe)
    fig.update_geos(
    projection_type="orthographic",
    showcoastlines=True,
    coastlinecolor="#334155",
    showland=True,
    landcolor="#1E2536",
    showocean=True,
    oceancolor="#0B0F19",
    showlakes=True,
    lakecolor="#0B0F19",
    showcountries=True,
    countrycolor="#334155",
    countrywidth=0.8,
    bgcolor="#0B0F19",

    projection_rotation=dict(lat=20.0, lon=65.0, roll=0),
    projection_scale=1.0,

    domain=dict(x=[0, 1], y=[0, 1]),
    fitbounds=False,
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=TERMINAL_STYLE["card_bg"],
        plot_bgcolor=TERMINAL_STYLE["card_bg"],
        hoverlabel=dict(
            bgcolor="#1E293B",
            font_size=12,
            font_color="#F8FAFC",
            font_family="Consolas, monospace"
        ),
        dragmode="pan",
        uirevision="locked" # Remembers your camera angle rotation between clicks
    )

    return fig

# ==============================================================================
# 8. DASH CALLBACKS & INTERACTIVE STATE ORCHESTRATION
# ==============================================================================

@app.callback(
    Output("closed-routes-store", "data"),
    Input({"type": "route-toggle", "route_id": ALL}, "value"),
    Input("reset-all-btn", "n_clicks"),
    State("closed-routes-store", "data"),
    prevent_initial_call=True
)
def manage_disrupted_routes(toggle_values, reset_clicks, current_closed):
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_closed

    trigger_id = ctx.triggered[0]["prop_id"]

    if "reset-all-btn" in trigger_id:
        return []

    new_closed = []
    for comp, is_open in zip(ctx.inputs_list[0], toggle_values):
        route_key = comp["id"]["route_id"]
        if not is_open:
            new_closed.append(route_key)

    return new_closed


@app.callback(
    Output("header-stats-container", "children"),
    Input("closed-routes-store", "data")
)
def render_header_metrics(closed_routes):
    G, active_alts = build_trade_network(closed_routes)
    score, band, _ = calculate_india_disruption_index(closed_routes, active_alts)

    score_color = TERMINAL_STYLE["accent_green"]
    if score > 20: score_color = TERMINAL_STYLE["accent_blue"]
    if score > 40: score_color = TERMINAL_STYLE["accent_yellow"]
    if score > 60: score_color = "#FB923C"
    if score > 80: score_color = TERMINAL_STYLE["accent_red"]

    return [
        html.Div([
            html.Small("ACTIVE DISRUPTIONS", className="d-block text-muted", style={"fontSize": "0.68rem"}),
            html.Span(f"{len(closed_routes)} CHOKEPOINTS", className="badge bg-danger text-white", style={"fontSize": "0.85rem"})
        ], className="text-center px-2 border-end border-secondary"),

        html.Div([
            html.Small("ACTIVE BYPASS DETOURS", className="d-block text-muted", style={"fontSize": "0.68rem"}),
            html.Span(f"{len(active_alts)} DETOURS", className="badge bg-warning text-dark", style={"fontSize": "0.85rem"})
        ], className="text-center px-2 border-end border-secondary"),

        html.Div([
            html.Small("INDIA DISRUPTION INDEX", className="d-block text-muted", style={"fontSize": "0.68rem"}),
            html.Span(f"{score}/100 [{band.upper()}]", className="badge text-white", style={"backgroundColor": score_color, "fontSize": "0.88rem"})
        ], className="text-center px-2")
    ]


@app.callback(
    Output("world-trade-map", "figure"),
    Input("closed-routes-store", "data")
)
def update_map(closed_routes):
    G, active_alts = build_trade_network(closed_routes)
    return build_map_figure(closed_routes, active_alts)


@app.callback(
    Output("tab-content-area", "children"),
    Input("right-panel-tabs", "active_tab"),
    Input("closed-routes-store", "data")
)
def render_panel_tabs(active_tab, closed_routes):
    G, active_alts = build_trade_network(closed_routes)
    score, band, summary = calculate_india_disruption_index(closed_routes, active_alts)

    if active_tab == "tab-controls":
        index_card = dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Span("SOVEREIGN TRADE DISRUPTION INDEX", style={"fontSize": "0.75rem", "color": TERMINAL_STYLE["text_muted"], "fontWeight": "600"}),
                        html.H2(f"{score} / 100", className="mb-0", style={"color": TERMINAL_STYLE["accent_yellow"] if score > 30 else TERMINAL_STYLE["accent_green"], "fontWeight": "800"}),
                        html.Small(f"Severity Tier: {band}", style={"fontWeight": "600", "color": "#F8FAFC"})
                    ], width=7),
                    dbc.Col([
                        dbc.Progress(value=score, max=100, color="danger" if score > 60 else "warning" if score > 30 else "success", style={"height": "14px", "borderRadius": "4px"}),
                        html.Small(summary, className="d-block text-muted mt-2", style={"fontSize": "0.72rem", "lineHeight": "1.2"})
                    ], width=5)
                ], className="align-items-center")
            ], className="py-2")
        ], className="mb-3", style={"backgroundColor": "#1A2234", "borderColor": TERMINAL_STYLE["card_border"]})

        toggle_rows = []
        for r_id, r_info in ROUTES_DATA.items():
            is_open = r_id not in closed_routes
            status_badge = dbc.Badge("OPEN 🟢", color="success", className="me-2") if is_open else dbc.Badge("CLOSED 🔴", color="danger", className="me-2")
            
            toggle_rows.append(
                dbc.ListGroupItem([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.B(r_info["name"], style={"fontSize": "0.85rem", "color": "#FFFFFF"}),
                                html.Small(f" — {r_info['type']} ({r_info['region']})", className="text-muted d-block", style={"fontSize": "0.72rem"})
                            ])
                        ], width=8),
                        dbc.Col([
                            html.Div([
                                status_badge,
                                dbc.Switch(
                                    id={"type": "route-toggle", "route_id": r_id},
                                    value=is_open,
                                    className="d-inline-block"
                                )
                            ], className="d-flex align-items-center justify-content-end")
                        ], width=4)
                    ], className="align-items-center")
                ], style={"backgroundColor": "#121826", "borderColor": "#1E293B", "padding": "0.6rem 0.8rem"})
            )

        routes_control_card = dbc.Card([
            dbc.CardHeader([
                dbc.Row([
                    dbc.Col(html.Span("CHOKEPOINT OPERATIONAL STATUS", style={"fontSize": "0.8rem", "fontWeight": "700", "color": TERMINAL_STYLE["accent_blue"]})),
                    dbc.Col(
                        dbc.Button("RESET ALL ROUTES", id="reset-all-btn", size="sm", color="outline-danger", style={"fontSize": "0.7rem", "fontWeight": "600"}),
                        className="text-end"
                    )
                ], className="align-items-center")
            ], style={"backgroundColor": "#1A2234", "borderBottom": f"1px solid {TERMINAL_STYLE['card_border']}"}),
            dbc.ListGroup(toggle_rows, flush=True)
        ], className="mb-3", style={"borderColor": TERMINAL_STYLE["card_border"]})

        alt_cards = []
        if active_alts:
            for alt_id in active_alts:
                alt = ALTERNATIVE_SPECS[alt_id]
                alt_cards.append(
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.Span("DYNAMIC BYPASS ACTIVATED", className="badge bg-warning text-dark mb-1", style={"fontSize": "0.68rem"}),
                                html.H6(alt["name"], className="text-white mb-1", style={"fontWeight": "700"}),
                                html.P(f"Transit Corridor: {alt['origin_destination']}", className="text-muted small mb-2"),
                                dbc.Row([
                                    dbc.Col([
                                        html.Small("Distance Penalty:", className="text-muted d-block"),
                                        html.B(alt["additional_distance_nm"], className="text-warning", style={"fontSize": "0.78rem"})
                                    ], width=6),
                                    dbc.Col([
                                        html.Small("Voyage Delay:", className="text-muted d-block"),
                                        html.B(alt["additional_transit_days"], className="text-warning", style={"fontSize": "0.78rem"})
                                    ], width=6)
                                ], className="mb-2"),
                                html.Small(f"Bunker Expense Delta: {alt['bunker_cost_delta']}", className="d-block text-muted mb-1", style={"fontSize": "0.72rem"}),
                                html.Small(f"Vulnerability Notes: {alt['key_constraints']}", className="d-block text-danger", style={"fontSize": "0.72rem"})
                            ])
                        ], className="p-2")
                    ], className="mb-2", style={"backgroundColor": "#161F30", "borderColor": TERMINAL_STYLE["accent_yellow"]})
                )
        else:
            alt_cards.append(
                html.Div([
                    html.P("No active alternative bypasses required. Primary maritime corridors are operating within baseline specifications.", className="text-muted small text-center p-3")
                ])
            )

        alt_section = dbc.Card([
            dbc.CardHeader(
                html.Span("ACTIVE ALTERNATIVE ROUTING & DETOUR METRICS", style={"fontSize": "0.8rem", "fontWeight": "700", "color": TERMINAL_STYLE["accent_yellow"]}),
                style={"backgroundColor": "#1A2234", "borderBottom": f"1px solid {TERMINAL_STYLE['card_border']}"}
            ),
            dbc.CardBody(alt_cards, className="p-2")
        ], style={"borderColor": TERMINAL_STYLE["card_border"]})

        return html.Div([index_card, routes_control_card, alt_section])

    elif active_tab == "tab-household":
        household_data = evaluate_household_impacts(closed_routes)
        cards = []
        for k, v in household_data.items():
            lvl = v["level"]
            badge_color = "success"
            if lvl == "Moderate": badge_color = "info"
            elif lvl == "Elevated": badge_color = "warning"
            elif lvl == "High": badge_color = "danger"
            elif lvl == "Severe": badge_color = "danger"

            cards.append(
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6(v["name"], className="text-white mb-1", style={"fontSize": "0.88rem", "fontWeight": "600"}),
                                html.P(v["rationale"], className="text-muted mb-0", style={"fontSize": "0.75rem", "lineHeight": "1.3"})
                            ], width=9),
                            dbc.Col([
                                dbc.Badge(f"{lvl.upper()}", color=badge_color, className="w-100 py-1", style={"fontSize": "0.75rem"})
                            ], width=3, className="text-end")
                        ], className="align-items-center")
                    ], className="p-2")
                ], className="mb-2", style={"backgroundColor": "#141C2E", "borderColor": TERMINAL_STYLE["card_border"]})
            )

        return html.Div([
            html.Div([
                html.H6("Sovereign Household Vulnerability Matrix", className="text-white mb-1", style={"fontWeight": "700"}),
                html.P("Evaluates transmission channels from maritime chokepoints to retail prices, domestic supplies, and cost of living in India.", className="text-muted small mb-3")
            ]),
            html.Div(cards)
        ])

    elif active_tab == "tab-industry":
        industry_cards = []
        for ind in INDUSTRIES_TAXONOMY:
            relevant_closed = [r for r in ind["disrupted_by"] if r in closed_routes]
            is_affected = len(relevant_closed) > 0

            status_badge = dbc.Badge("AT RISK", color="danger") if is_affected else dbc.Badge("NORMAL", color="success")
            border_color = TERMINAL_STYLE["accent_red"] if is_affected else TERMINAL_STYLE["card_border"]

            industry_cards.append(
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            dbc.Row([
                                dbc.Col(html.H6(ind["name"], className="text-white mb-1", style={"fontWeight": "700"}), width=9),
                                dbc.Col(status_badge, width=3, className="text-end")
                            ]),
                            html.Small(f"Direct Dependency: {ind['dependency']}", className="d-block text-muted mb-1", style={"fontSize": "0.75rem"}),
                            html.Small(f"Disruption Mechanism: {ind['mechanism']}", className="d-block text-warning mb-1", style={"fontSize": "0.73rem"}),
                            html.Small(f"Exposure Profile: {ind['exposure']}", className="d-block text-info mb-1", style={"fontSize": "0.72rem"}),
                            html.Small(f"Strategic Alternative: {ind['alternative']}", className="d-block text-muted", style={"fontSize": "0.72rem"})
                        ])
                    ], className="p-2")
                ], className="mb-2", style={"backgroundColor": "#141C2E", "borderColor": border_color})
            )

        return html.Div([
            html.Div([
                html.H6("Indian Industrial Exposure & Corporate Risk", className="text-white mb-1", style={"fontWeight": "700"}),
                html.P("Dynamic impact propagation across supply chain nodes, raw material feedstocks, and export commitments.", className="text-muted small mb-3")
            ]),
            html.Div(industry_cards)
        ])

    elif active_tab == "tab-methodology":
        return html.Div([
            dbc.Card([
                dbc.CardBody([
                    html.H6("DATA & SCENARIO MODEL ASSUMPTIONS", className="text-info mb-2", style={"fontWeight": "700"}),
                    html.P(
                        "This dashboard is an analytical simulation tool designed for economic scenario testing, "
                        "risk assessments, and educational intelligence. The trade flows, route dependencies, "
                        "household impacts, and industrial exposure ratings are modeled representations. "
                        "They illustrate structural dependencies rather than definitive price forecasts.",
                        className="text-muted small mb-3"
                    ),
                    html.H6("Key Structural Formulations:", className="text-white small", style={"fontWeight": "700"}),
                    html.Ul([
                        html.Li("India Disruption Index: Calculated via route exposure weightings (w_i), multiplied by a compounding multi-chokepoint penalty factor, offset by dynamic mitigation discounts when bypass corridors remain navigable.", className="text-muted small mb-2"),
                        html.Li("Graph Representation: Formulated as a NetworkX graph with oceanic trade nodes. Disrupted edges are pruned to evaluate path availability and trigger alternative corridor visual traces.", className="text-muted small mb-2"),
                        html.Li("Household & Industrial Models: Real-world empirical import/export sensitivities (e.g., 87% crude import exposure, 90% LPG Hormuz transit) establish qualitative and directional risk tiers (Low/Moderate/Elevated/High/Severe).", className="text-muted small")
                    ], className="ps-3 mb-3"),
                    html.Div([
                        html.Small("Notice: Actual real-world shipping dislocations depend on vessel inventory depth, strategic reserve drawdowns, war-risk reinsurance surcharges, bilateral government currency swaps, and diplomatic exemptions.", className="text-warning small fst-italic")
                    ])
                ], className="p-3")
            ], style={"backgroundColor": "#141C2E", "borderColor": TERMINAL_STYLE["card_border"]})
        ])

# ==============================================================================
# 9. EXECUTION ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    app.run(debug=True, port=8050)