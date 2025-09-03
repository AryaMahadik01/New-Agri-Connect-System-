from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["agri_connect"]   # ✅ match with app.py
products_col = db["products"]

# Clear existing products (optional, avoids duplicates when re-seeding)
products_col.delete_many({})

# Insert sample products
products_col.insert_many([
    {
        "name": "Wheat Seeds",
        "price": 100,
        "description": "High-yield wheat seeds suitable for multiple soil types.",
        "image": "images/wheat.png"
    },
    {
        "name": "Rice Seeds",
        "price": 120,
        "description": "Premium quality rice seeds for healthy crop growth.",
        "image": "images/rice.png"
    },
    {
        "name": "Organic Fertilizer",
        "price": 250,
        "description": "100% natural organic fertilizer to boost soil fertility.",
        "image": "images/fertilizer.png"
    },
    {
        "name": "Insecticide A",
        "price": 150,
        "description": "Effective protection against common crop pests.",
        "image": "images/insecticide.png"
    },
    {
        "name": "Tractor Tool Set",
        "price": 5000,
        "description": "Durable farming tools to support agricultural work.",
        "image": "images/tools.png"
    }
])

print("✅ Database seeded successfully with sample products!")
