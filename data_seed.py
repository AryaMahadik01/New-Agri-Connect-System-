from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["agri_connect"]   # ✅ match with app.py
products_col = db["products"]

# Clear existing products (optional, avoids duplicates when re-seeding)
products_col.delete_many({})

products_col.insert_many([
    # -------------------- Seeds Data -------------------- 
    {
        "name": "MARIGOLD SEEDS",
        "price": 1799,
        "description": "ASHTAGANDHA PLUS MARIGOLD SEEDS, SUITABLE FOR LONG DISTANCE SHIPPING",
        "image": "images/seeds/fseed1.png",
        "category": "seeds"
    },
    {
        "name": "CALENDULA DOUBLE MIX SEEDS",
        "price": 249,
        "description": "IRIS HYBRID FLOWER CALENDULA DOUBLE MIX SEEDS",
        "image": "images/seeds/fseed2.png",
        "category": "seeds"
    },
    {
        "name": "BALSAM SEEDS",
        "price": 149,
        "description": "IRIS HYBRID FLOWER BALSAM SEEDS",
        "image": "images/seeds/fseed3.png",
        "category": "seeds"
    },
    {
        "name": "COSMOS MIX SEEDS",
        "price": 179,
        "description": "IRIS HYBRID FLOWER COSMOS MIX SEEDS",
        "image": "images/seeds/fseed4.png",
        "category": "seeds"
    },
    {
        "name": "Garden Flowers",
        "price": 59,
        "description": "Hybrid Zinnia Indo American Seeds: Vibrant. Easy-Growing Garden Flowers",
        "image": "images/seeds/fseed5.png",
        "category": "seeds"
    },
    {
        "name": "White Marigold Seeds",
        "price": 144,
        "description": "NS Fl Hybrid Vanilla White Marigold Seeds",
        "image": "images/seeds/fseed6.png",
        "category": "seeds"
    },
    {
        "name": "Mix Flower Seeds",
        "price": 79,
        "description": "NS Fl Hybrid Vinca Pacifica Mix Flower Seeds",
        "image": "images/seeds/fseed7.png",
        "category": "seeds"
    },
    {
        "name": "DWARF BALL MIXED SEEDS",
        "price": 129,
        "description": "NS AGERATUM DWARF BALL MIX",
        "image": "images/seeds/fseed8.png",
        "category": "seeds"
    },
    {
        "name": "Pansy flower SEEDS",
        "price": 99,
        "description": "Pansy Flower Seeds for Garden Area by Indo American",
        "image": "images/seeds/fseed9.png",
        "category": "seeds"
    },
    {
        "name": "MARIGOLDSARPAN SEEDS",
        "price": 1050,
        "description": "SARPAN HYBRID ASTER - AST-I (SEEDS)",
        "image": "images/seeds/fseed10.png",
        "category": "seeds"
    },
    {
        "name": "Watermelon Seeds",
        "price": 400,
        "description": "NS 295 Fl Hybrid Watermelon Seeds",
        "image": "images/seeds/fru-seed1.png",
        "category": "seeds"
    },
    {
        "name": "Muskmelon Seeds",
        "price": 849,
        "description": "NS 910 Fl Hybrid Muskmelon Seeds: Early, High-Yield,Sweet Fruit",
        "image": "images/seeds/fru-seed2.png",
        "category": "seeds"
    },
    {
        "name": "Yellow Watermelon Seeds",
        "price": 1549,
        "description": "Aarohi Yellow Watermelon Seeds: Sweet, High-Yield,Vibrant Flesh",
        "image": "images/seeds/fru-seed3.png",
        "category": "seeds"
    },
    {
        "name": "PAPAYA SEED",
        "price": 2999,
        "description": "SAPNA Fl PAPAYA SEED with Premium quality and Easy to Grow ",
        "image": "images/seeds/fru-seed4.png",
        "category": "seeds"
    },
    {
        "name": "BEANS SEEDS",
        "price": 149,
        "description": "Moraleda Beans Seeds by Seminis High Yield, Long Shelf Life ",
        "image": "images/seeds/beans-seed.png",
        "category": "seeds"
    },
    {
        "name": "BEETROOT SEEDS",
        "price": 269,
        "description": "Red Man Beetroot Seeds by Ashoka for Good Quality Seeds",
        "image": "images/seeds/beetroot-seed.png",
        "category": "seeds"
    },
    {
        "name": "BITTER GOURD SEEDS",
        "price": 340,
        "description": "Akash Fl Hybrid Bitter Gourd Seeds by V.N.R. for Good Yeild",
        "image": "images/seeds/bitter-gourd-seed.png",
        "category": "seeds"
    },
    {
        "name": "BRINGAL SEEDS",
        "price": 179,
        "description": "212 Fl Hybrid Brinjal Seeds by V.N.R. for Good Yeild",
        "image": "images/seeds/bringal-seed.png",
        "category": "seeds"
    },
    {
        "name": "CAULIFLOWER SEEDS",
        "price": 599,
        "description": "CFL 1522 Cauliflower Seeds by Syngenta for Good Growing Farm",
        "image": "images/seeds/cauliflower-seed.png",
        "category": "seeds"
    },
    {
        "name": "CORINDER SEEDS",
        "price": 165,
        "description": "Surabhi Coriander Seeds. Easy to Grow",
        "image": "images/seeds/corinder-seed.png",
        "category": "seeds"
    },
    {
        "name": "CUCUMBER SEEDS",
        "price": 329,
        "description": "Krish Fl Hybrid Cucumber Seeds Good Seeds for Better Yeild",
        "image": "images/seeds/cucumber-seed.png",
        "category": "seeds"
    },
    {
        "name": "GREEN CHILLI SEEDS",
        "price": 349,
        "description": "NS 1101 F1 Green Chilli seeds - High Yield, Medium Pungency Hybrid",
        "image": "images/seeds/greenchilli-seed.png",
        "category": "seeds"
    },
    {
        "name": "RED CHILLI SEEDS",
        "price": 509,
        "description": "HPH 5531 Red Chilli seeds - High Yield, Medium Pungency Hybrid",
        "image": "images/seeds/redchilli-seed.png",
        "category": "seeds"
    },
    {
        "name": "OKRA SEEDS",
        "price": 679,
        "description": "Radhika Bhendi Okra Hybrid Seeds - High Yield, Long Shelf Life",
        "image": "images/seeds/okra-seed.png",
        "category": "seeds"
    },
    # -------------------- Fertilizers Data -------------------- 
    {
        "name": "Instafert Combi",
        "price": 650,
        "description": "Instafert Combi-M.S Grade no.2,EDTA Chelated MixMicronutrient.Contain Iron, Manganese, and Other micro nutrient.",
        "image": "images/fertilizers/fert1.png",
        "category": "fertilizers"
    },
    {
        "name": "UTKRISHTA Micronutrients Fertilizer",
        "price": 300,
        "description": "UTKRISHTA Mixture of Micronutrients Fertilizer-Karnataka Grade, Zn-3%, Fe-2%, Mn-1%, 8-0.5%,Contains Micro-filtered Biological Amino Acids.",
        "image": "images/fertilizers/fert2.png",
        "category": "fertilizers"
    },
    {
        "name": "Parivartan Fertilizer",
        "price": 440,
        "description": "Parivartan NPK 00:52:34 Fertilizer",
        "image": "images/fertilizers/fert3.png",
        "category": "fertilizers"
    },
    {
        "name": "Aries Zn Sulf Fertilizer",
        "price": 225,
        "description": "Aries Zn Sulf Zinc Sulphate Monohydrate.",
        "image": "images/fertilizers/fert4.png",
        "category": "fertilizers"
    },
    {
        "name": "Ferti Max HD Fertilizer",
        "price": 450,
        "description": "Aries Agro Ferti Max HD NPK 00:52:34 water Soluble NPK Fertilizer",
        "image": "images/fertilizers/fert5.png",
        "category": "fertilizers"
    },
    {
        "name": "MacroFert HD Fertilizer",
        "price": 600,
        "description": "Aries MacroFert HD NPK 20: 20: 20 Fertilizer.",
        "image": "images/fertilizers/fert6.png",
        "category": "fertilizers"
    },
    {
        "name": "FertiMax Fertilizer",
        "price": 370,
        "description": "Aries Fertimax 13:00:45 Fertilizer",
        "image": "images/fertilizers/fert7.png",
        "category": "fertilizers"
    },
    {
        "name": "Coromandel 13:0:45 Fertilizer",
        "price": 250,
        "description": "Corornanciel offer the 13:0:45 tortilizer, a specialized blend to enhance flowring fruiting, and Overall crop health",
        "image": "images/fertilizers/fert8.png",
        "category": "fertilizers"
    },
    {
        "name": "Organic Manure Fertilizer",
        "price": 700,
        "description": "Sanchaar—Bio—Enriched Organic Manure (Granulated Soil Conditioner)",
        "image": "images/fertilizers/fert9.png",
        "category": "fertilizers"
    },
    {
        "name": "Rallis Nayazinc Fertilizer",
        "price": 820,
        "description": "Tata Rallis Nayazinc Fertilizer — Zinc Polyphoshate.",
        "image": "images/fertilizers/fert10.png",
        "category": "fertilizers"
    },
    # -------------------- Tools Data --------------------
    {
        "name": "GARDEN SHADE",
        "price": 1599,
        "description": "ANIL PACKAGING GARDEN SHADE NET SHADE NET",
        "image": "images/tools/garden-shade.png",
        "category": "tools"
    },
    {
        "name": "HAND WEEDER",
        "price": 550,
        "description": " BHARAT 2 IN 1 HAND WEEDER WITH STRONG QUALITY",
        "image": "images/tools/hand-weeder.png",
        "category": "tools"
    },
    {
        "name": "HARVESTER WITH BLADE",
        "price": 300,
        "description": "VGT MANGO PLUCKER/HARVESTER WITH SINGLE BLADE",
        "image": "images/tools/harvester-with-blade.png",
        "category": "tools"
    },
    {
        "name": "HEAD TORCH",
        "price": 750,
        "description": "BALWAN SHAKTI LED FLASHLIGHT HEAD TORCH BT.50",
        "image": "images/tools/head-torch.png",
        "category": "tools"
    },
    {
        "name": "KOYTA BLADE",
        "price": 279,
        "description": "Bharat Goa Akadi Without Handle",
        "image": "images/tools/koyta.png",
        "category": "tools"
    },
    {
        "name": "MANUAL WEEDER",
        "price": 499,
        "description": "Bharat IO Inch Manual Weeder - Easy. Efficient Hand Tool for Farming",
        "image": "images/tools/manual-weeder.png",
        "category": "tools"
    },
    {
        "name": "PRUNER WITH SAW",
        "price": 1999,
        "description": "HECTARE ALUMINUM TELESCOPIC LONG REACH (10 FEET) CUT AND HOLD PRUNER WITH SAW",
        "image": "images/tools/pruner-with-saw.png",
        "category": "tools"
    },
    {
        "name": "SPRAY TANK",
        "price": 1599,
        "description": "Neptune NF•IOB Manual Knapsack Sprayer Hand-Operated High-pressure Pump 161 Tank Capacity",
        "image": "images/tools/spray-tank.png",
        "category": "tools"
    },
    {
        "name": "AGRO TOOLSET",
        "price": 1250,
        "description": "A complete agricultural toolset featuring a brush cutter blade, shaft, safety gear, and accessories.",
        "image": "images/tools/toolkit.png",
        "category": "tools"
    },
    {
        "name": "TRACTOR SPRAYER",
        "price": 7000,
        "description": "NEPTUNE TRACTOR MOUNTED SPRAYER (HTP GOLD PLUS)",
        "image": "images/tools/tractor-sprayer.png",
        "category": "tools"
    },
    {
        "name": "WEED MAT",
        "price": 950,
        "description": "ANIL PACKAGING WEED MAT 100 GSM - weed Mat",
        "image": "images/tools/weed-mat.png",
        "category": "tools"
    },
    {
        "name": "SOLAR PANEL",
        "price": 950,
        "description": "MG GREEN 12V IOW SOLAR PANEL",
        "image": "images/tools/10w-solarpanel.png",
        "category": "tools"
    },
    {
        "name": "CHAFF CUTTER",
        "price": 35000,
        "description": "ECOWEALTH VIRAJ 35 CHAFF CUTTER 3 HP",
        "image": "images/tools/chaff-cutter.png",
        "category": "tools"
    },
    {
        "name": "ELECTRIC SPRAY",
        "price": 4950,
        "description": "UJWAL ELECTRICS O.IHP SPRAYER + DRIP INJECTOR",
        "image": "images/tools/electric-spray.png",
        "category": "tools"
    },
    {
        "name": "FILM SHEET",
        "price": 1950,
        "description": "VEDANT REGULAR QUALITY SILVER/BLACK MULCH FILM 1MX400M",
        "image": "images/tools/film-sheet.png",
        "category": "tools"
    },
    {
        "name": "GARDEN WEEDER",
        "price": 20000,
        "description": "NEPTUNE GARDEN MINI POWER TILLER/CULTIVATORJROTARY/WEEDER",
        "image": "images/tools/garden-weeder.png",
        "category": "tools"
    },
    {
        "name": "MOTOR SPRAY",
        "price": 3440,
        "description": "BALWAAN BS-21 21N1 KRISHI SINGLE MOTOR BATTERY SPRAYER 12X8",
        "image": "images/tools/motor-spray.png",
        "category": "tools"
    },
    {
        "name": "WATER PUMP",
        "price": 12000,
        "description": "BALWAAN WP 33R WATER PUMP 3x3 INCH",
        "image": "images/tools/water-pump.png",
        "category": "tools"
    },
    {
        "name": "PLANTING TROWEL",
        "price": 475,
        "description": "WOLF GARTEN PLANTING TROWEL WITH FIX HANDLE (LU-2P)",
        "image": "images/tools/planting-trowel.png",
        "category": "tools"
    },
    {
        "name": "PIPE 300M",
        "price": 999,
        "description": "Siddhi Crip Pipe 300m: Durable, Efficient Irrigation for Gardens",
        "image": "images/tools/pipe-300m.png",
        "category": "tools"
    },
    {
        "name": "MANUAL SEEDER",
        "price": 5000,
        "description": "BALWAAN S-12 AGRICULTURAL 12T MANUAL SEEDER",
        "image": "images/tools/manual-seeder.png",
        "category": "tools"
    },
    # -------------------- Pesticides Data --------------------
    {
        "name": "UPL saaf Fungicide",
        "price": 668,
        "description": "Protect Your Crops Effectively with Dual—Action Fungicide",
        "image": "images/pesticides/pest1.png",
        "category": "pesticides"
    },
    {
        "name": "Dhanuka Sempra Herbicide",
        "price": 1400,
        "description": "Dhanuka Sempra Herbicide—powerful Control Over Nutgrass in Sugarcane & Maize Fields",
        "image": "images/pesticides/pest2.png",
        "category": "pesticides"
    },
    {
        "name": "Profex Super Insecticide",
        "price": 158,
        "description": "JU Active Plant Growth Regulator is a dynamic ethylene-releasing formulation containing Ethephon 39% SL.",
        "image": "images/pesticides/pest3.png",
        "category": "pesticides"
    },
    {
        "name": "Glyphosate Herbicide",
        "price": 145,
        "description": "Exylon — Glyphosate (Ammonium Salt of Glyphosate 71% SG) Herbicide.",
        "image": "images/pesticides/pest4.png",
        "category": "pesticides"
    },
    {
        "name": "Certis Kocide ",
        "price": 2740,
        "description": "Bharat Certis Kocide 3000 Copper Hydroxide 46.1% WG Fungicide.",
        "image": "images/pesticides/pest5.png",
        "category": "pesticides"
    },
    {
        "name": "Valexio Insecticide",
        "price": 1550,
        "description": "Valexio Insecticide — Powered by Prexio Active for Rice Hopper Control.",
        "image": "images/pesticides/pest6.png",
        "category": "pesticides"
    },
    {
        "name": "Baye Insecticide",
        "price": 346,
        "description": "Bayer Admire Imidacloprid 70% WG — Contact & systemic protection from sucking Pests.",
        "image": "images/pesticides/pest7.png",
        "category": "pesticides"
    },
    {
        "name": "Adama Wirazer Herbicide",
        "price": 170,
        "description": "Explore a mordern solution to weed management in rice crops Adama Wirazer Herbicide",
        "image": "images/pesticides/pest8.png",
        "category": "pesticides"
    },
    {
        "name": "HPM Herbicide",
        "price": 250,
        "description": "HPM Dhruv Herbicide Advanced Weed Control with Glyphosate 71% SG",
        "image": "images/pesticides/pest9.png",
        "category": "pesticides"
    },
    {
        "name": "Adama Narkis Herbicide",
        "price": 361,
        "description": "Adama Narkis Herbicide - Dispyribac Sodium 10% SC and it effective against a wide range.",
        "image": "images/pesticides/pest10.png",
        "category": "pesticides"
    }

])


print("✅ Database seeded successfully with sample products!")

# -------------------- Crops Collection --------------------
db.crops.delete_many({})
crops_data = [
    {
        "name": "Wheat",
        "location": "Punjab, Haryana, UP",
        "season": "Rabi",
        "weather": "Cool and dry",
        "description": "Staple crop of India, grown in winter season.",
        "image": "images/seeds/wheat.png"
    },
    {
        "name": "Rice",
        "location": "West Bengal, Bihar, Tamil Nadu",
        "season": "Kharif",
        "weather": "Hot and humid",
        "description": "Major staple crop, requires high water availability.",
        "image": "images/seeds/rice.png"
    },
    {
        "name": "Wheat",
        "location": "Punjab, Haryana, UP",
        "season": "Rabi",
        "weather": "Cool and dry",
        "description": "Staple crop of India, grown in winter season.",
        "image": "images/seeds/wheat.png"
    },
    {
        "name": "Rice",
        "location": "West Bengal, Bihar, Tamil Nadu",
        "season": "Kharif",
        "weather": "Hot and humid",
        "description": "Major staple crop, requires high water availability.",
        "image": "images/seeds/rice.png"
    }
]


db.crops.insert_many(crops_data)
# -------------------- Government Schemes --------------------
db.schemes.delete_many({})
schemes_data = [
    {
        "name": "Pradhan Mantri Fasal Bima Yojana",
        "description": "Crop insurance scheme for farmers’ protection.",
        "link": "https://pmfby.gov.in/"
    },
    {
        "name": "Kisan Credit Card",
        "description": "Provides short-term credit to farmers.",
        "link": "https://www.nabard.org/"
    },
    {
        "name": "Pradhan Mantri Fasal Bima Yojana",
        "description": "Crop insurance scheme for farmers’ protection.",
        "link": "https://pmfby.gov.in/"
    },
    {
        "name": "Kisan Credit Card",
        "description": "Provides short-term credit to farmers.",
        "link": "https://www.nabard.org/"
    }
]
db.schemes.insert_many(schemes_data)

# -------------------- News --------------------
db.news.delete_many({})
news_data = [
    {
        "title": "Monsoon boosts Kharif sowing",
        "summary": "Good rainfall improves sowing of rice and pulses this year.",
        "link": "https://agriculture.gov.in",
        "date": "2025-09-15"
    },
    {
        "title": "Govt announces subsidy on fertilizers",
        "summary": "New subsidy rates to support farmers.",
        "link": "https://pib.gov.in",
        "date": "2025-09-10"
    },
    {
        "title": "Monsoon boosts Kharif sowing",
        "summary": "Good rainfall improves sowing of rice and pulses this year.",
        "link": "https://agriculture.gov.in",
        "date": "2025-09-15"
    },
    {
        "title": "Govt announces subsidy on fertilizers",
        "summary": "New subsidy rates to support farmers.",
        "link": "https://pib.gov.in",
        "date": "2025-09-10"
    }
]
db.news.insert_many(news_data)

# -------------------- Knowledge Hub --------------------
db.knowledge.delete_many({})
knowledge_data = [
    {
        "title": "Organic Farming Guide",
        "content": "Learn how to start organic farming and improve soil health.",
        "link": "https://agricoop.gov.in"
    },
    {
        "title": "Agri-Business Startup Ideas",
        "content": "Top 10 agribusiness ideas for young entrepreneurs.",
        "link": "https://startupindia.gov.in"
    },
    {
        "title": "Organic Farming Guide",
        "content": "Learn how to start organic farming and improve soil health.",
        "link": "https://agricoop.gov.in"
    },
    {
        "title": "Agri-Business Startup Ideas",
        "content": "Top 10 agribusiness ideas for young entrepreneurs.",
        "link": "https://startupindia.gov.in"
    }
]
db.knowledge.insert_many(knowledge_data)

print("✅ Crops, Schemes, News, Knowledge data seeded successfully!")