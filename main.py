"""
Backend API for Supermarket Price Finder
Optimized for Render.com deployment
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import sqlite3
from datetime import datetime
import os

app = FastAPI(
    title="Supermarket Price Finder API",
    description="Israeli Supermarket Price Comparison API",
    version="1.0.0"
)

# CORS for Android
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path
DB_PATH = os.getenv("DB_PATH", "supermarket.db")

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with sample data for Render"""
    if os.path.exists(DB_PATH):
        return
    
    print("🔨 Creating initial database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stores (
            store_id TEXT PRIMARY KEY,
            chain_id TEXT,
            chain_name TEXT,
            subchain_id TEXT,
            subchain_name TEXT,
            store_name TEXT,
            city_id TEXT,
            city_name TEXT,
            city_type TEXT,
            address TEXT,
            phone TEXT,
            opening_hours TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            barcode TEXT UNIQUE,
            product_name TEXT,
            manufacturer TEXT,
            category TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            store_id TEXT,
            price REAL,
            unit_price REAL,
            unit TEXT,
            last_update TEXT,
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (store_id) REFERENCES stores(store_id)
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_city_name ON stores(city_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chain ON stores(chain_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_product_name ON products(product_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_store ON prices(store_id)")
    
    # Insert sample data - Israeli cities and stores
    cities_data = [
        ("tel_aviv", "תל אביב-יפו"),
        ("jerusalem", "ירושלים"),
        ("haifa", "חיפה"),
        ("rishon", "ראשון לציון"),
        ("petah_tikva", "פתח תקווה"),
        ("ashdod", "אשדוד"),
        ("netanya", "נתניה"),
        ("beer_sheva", "באר שבע"),
        ("holon", "חולון"),
        ("ramat_gan", "רמת גן"),
        ("ashkelon", "אשקלון"),
        ("rehovot", "רחובות"),
        ("bat_yam", "בת ים"),
        ("herzliya", "הרצליה"),
        ("kfar_saba", "כפר סבא"),
        ("hadera", "חדרה"),
        ("modi_in", "מודיעין"),
        ("ramla", "רמלה"),
        ("raanana", "רעננה"),
        ("lod", "לוד"),
    ]
    
    chains = [
        ("shufersal", "שופרסל"),
        ("rami_levy", "רמי לוי"),
        ("victory", "ויקטורי"),
        ("yohananof", "יוחננוף"),
        ("mega", "מגה בעיר"),
        ("keshet", "קשת טעמים"),
        ("hatzi_hinam", "חצי חינם"),
        ("mahsani_hashuk", "מחסני השוק"),
        ("super_pharm", "סופר-פארם"),
        ("tiv_taam", "טיב טעם"),
    ]
    
    subchains = [
        ("shufersal_deal", "shufersal", "שופרסל דיל"),
        ("shufersal_sheli", "shufersal", "שופרסל שלי"),
        ("shufersal_universe", "shufersal", "יוניברס"),
    ]
    
    # Generate stores for each city
    store_counter = 1
    for city_id, city_name in cities_data:
        for chain_id, chain_name in chains[:6]:  # First 6 chains
            # Regular stores
            for i in range(2):
                subchain_id = None
                subchain_name = None
                
                # Add subchains for Shufersal
                if chain_id == "shufersal" and i < len(subchains):
                    subchain_id, _, subchain_name = subchains[i]
                
                store_name = f"{chain_name} {city_name}"
                if subchain_name:
                    store_name = f"{subchain_name} {city_name}"
                
                cursor.execute("""
                    INSERT INTO stores VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"store_{store_counter}",
                    chain_id,
                    chain_name,
                    subchain_id,
                    subchain_name,
                    store_name,
                    city_id,
                    city_name,
                    "עיר",
                    f"רחוב הראשי {store_counter}, {city_name}",
                    f"03-{1234567 + store_counter}",
                    "א׳-ה׳ 08:00-22:00, ו׳ 08:00-15:00"
                ))
                store_counter += 1
    
    # Insert sample products - common Israeli grocery items
    products = [
        ("7290000000001", "חלב תנובה 3%", "תנובה", "חלב ומוצרי חלב"),
        ("7290000000002", "לחם פרוס שחור", "אנג'ל", "לחמים"),
        ("7290000000003", "גבינה צהובה עמק", "תנובה", "גבינות"),
        ("7290000000004", "יוגורט יופלה תות", "יופלה", "מוצרי חלב"),
        ("7290000000005", "ביצים L גד", "גד", "ביצים"),
        ("7290000000006", "שמן קנולה", "עמק הירדן", "שמנים"),
        ("7290000000007", "סוכר לבן", "סוגת", "בסיסי"),
        ("7290000000008", "קפה עלית", "עלית", "שתייה חמה"),
        ("7290000000009", "תה ויסוצקי", "ויסוצקי", "שתייה חמה"),
        ("7290000000010", "שוקולד פרה", "שטראוס", "חטיפים"),
        ("7290000000011", "ביסלי גריל", "אסם", "חטיפים"),
        ("7290000000012", "במבה אסם", "אסם", "חטיפים"),
        ("7290000000013", "קורנפלקס תלמה", "תלמה", "דגני בוקר"),
        ("7290000000014", "שמפו סנסודיין", "סנסודיין", "טיפוח"),
        ("7290000000015", "משחת שיניים קולגייט", "קולגייט", "טיפוח"),
        ("7290000000016", "טישו לוטוס", "לוטוס", "נייר"),
        ("7290000000017", "נייר טואלט סופט", "סופט", "נייר"),
        ("7290000000018", "אורז בסמטי", "סוגת", "בסיסי"),
        ("7290000000019", "פסטה ברילה", "ברילה", "פסטות"),
        ("7290000000020", "רוטב עגבניות פרימה", "פרימה", "רטבים"),
        ("7290000000021", "טונה סטרקיסט", "סטרקיסט", "שימורים"),
        ("7290000000022", "חומוס אחלה", "אחלה", "ממרחים"),
        ("7290000000023", "טחינה קרם", "קרם", "ממרחים"),
        ("7290000000024", "ריבת תות שופרסל", "שופרסל", "ממרחים"),
        ("7290000000025", "מיץ תפוזים פרימור", "פרימור", "משקאות"),
        ("7290000000026", "קוקה קולה 1.5 ליטר", "קוקה קולה", "משקאות"),
        ("7290000000027", "מים מינרליים נביעות", "נביעות", "מים"),
        ("7290000000028", "גזר ארוז", "ירקות", "פירות וירקות"),
        ("7290000000029", "תפוח עץ", "ירקות", "פירות וירקות"),
        ("7290000000030", "בננות", "ירקות", "פירות וירקות"),
    ]
    
    for i, (barcode, name, manufacturer, category) in enumerate(products):
        cursor.execute("""
            INSERT INTO products VALUES (?, ?, ?, ?, ?)
        """, (f"prod_{i+1}", barcode, name, manufacturer, category))
    
    # Insert prices for each product in each store
    import random
    for i in range(1, store_counter):
        store_id = f"store_{i}"
        for j in range(1, len(products) + 1):
            product_id = f"prod_{j}"
            base_price = 5.0 + (j * 2.5)
            price = round(base_price + random.uniform(-2, 3), 2)
            
            cursor.execute("""
                INSERT INTO prices (product_id, store_id, price, unit_price, unit, last_update)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                store_id,
                price,
                price,
                "יחידה",
                datetime.now().isoformat()
            ))
    
    conn.commit()
    conn.close()
    print(f"✅ Database created with {store_counter-1} stores and {len(products)} products!")

# Initialize DB on startup
init_db()

@app.get("/")
def root():
    return {
        "message": "🛒 Supermarket Price Finder API",
        "version": "1.0.0",
        "status": "running",
        "description": "Israeli Supermarket Price Comparison",
        "endpoints": {
            "cities": "/api/v1/cities/search?q=תל",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/api/v1/cities/search")
def search_cities(q: str):
    """חיפוש ערים"""
    if len(q) < 2:
        return []
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            city_id as id,
            city_name as name,
            city_type as type,
            COUNT(DISTINCT store_id) as storesCount
        FROM stores
        WHERE city_name LIKE ?
        GROUP BY city_id, city_name, city_type
        ORDER BY city_name
    """, (f'%{q}%',))
    
    results = []
    for row in cursor.fetchall():
        results.append({
            "id": str(row['id']),
            "name": row['name'],
            "type": row['type'] or "עיר",
            "storesCount": row['storesCount']
        })
    
    conn.close()
    return results

@app.get("/api/v1/cities/{city_id}/chains")
def get_city_chains(city_id: str):
    """קבלת רשתות בעיר"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT 
            chain_id as id,
            chain_name as name
        FROM stores
        WHERE city_id = ?
        ORDER BY chain_name
    """, (city_id,))
    
    results = []
    for row in cursor.fetchall():
        results.append({
            "id": str(row['id']),
            "name": row['name'],
            "logo": None
        })
    
    conn.close()
    return results

@app.get("/api/v1/chains/{chain_id}/subchains")
def get_subchains(chain_id: str, city: Optional[str] = None):
    """קבלת תת-רשתות"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = """
        SELECT DISTINCT 
            subchain_id as id,
            chain_id as chainId,
            subchain_name as name
        FROM stores
        WHERE chain_id = ?
        AND subchain_id IS NOT NULL
    """
    params = [chain_id]
    
    if city:
        query += " AND city_id = ?"
        params.append(city)
    
    query += " ORDER BY subchain_name"
    
    cursor.execute(query, params)
    
    results = []
    for row in cursor.fetchall():
        results.append({
            "id": str(row['id']),
            "chainId": str(row['chainId']),
            "name": row['name'],
            "logo": None
        })
    
    conn.close()
    return results

@app.get("/api/v1/stores")
def get_stores(chain: Optional[str] = None, subchain: Optional[str] = None, city: Optional[str] = None):
    """קבלת סניפים"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            store_id as id,
            chain_id as chainId,
            subchain_id as subChainId,
            store_name as name,
            city_name as city,
            address,
            phone,
            opening_hours as openingHours
        FROM stores
        WHERE 1=1
    """
    params = []
    
    if chain:
        query += " AND chain_id = ?"
        params.append(chain)
    
    if subchain:
        query += " AND subchain_id = ?"
        params.append(subchain)
    
    if city:
        query += " AND city_id = ?"
        params.append(city)
    
    query += " ORDER BY store_name"
    
    cursor.execute(query, params)
    
    results = []
    for row in cursor.fetchall():
        results.append({
            "id": str(row['id']),
            "chainId": str(row['chainId']),
            "subChainId": str(row['subChainId']) if row['subChainId'] else None,
            "name": row['name'],
            "city": row['city'],
            "address": row['address'],
            "phone": row['phone'],
            "openingHours": row['openingHours'],
            "latitude": None,
            "longitude": None
        })
    
    conn.close()
    return results

@app.get("/api/v1/stores/{store_id}/products/search")
def search_products(store_id: str, q: str):
    """חיפוש מוצרים בסניף"""
    if len(q) < 2:
        return []
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            p.product_id,
            p.barcode,
            p.product_name,
            p.manufacturer,
            p.category,
            pr.price,
            pr.unit_price as unitPrice,
            pr.unit,
            pr.last_update as lastUpdate
        FROM products p
        JOIN prices pr ON p.product_id = pr.product_id
        WHERE pr.store_id = ?
        AND p.product_name LIKE ?
        ORDER BY p.product_name
        LIMIT 50
    """, (store_id, f'%{q}%'))
    
    results = []
    for row in cursor.fetchall():
        results.append({
            "product": {
                "id": str(row['product_id']),
                "barcode": row['barcode'],
                "name": row['product_name'],
                "manufacturer": row['manufacturer'],
                "category": row['category']
            },
            "price": {
                "productId": str(row['product_id']),
                "storeId": store_id,
                "price": row['price'],
                "unitPrice": row['unitPrice'],
                "unit": row['unit'],
                "currency": "ILS",
                "lastUpdate": row['lastUpdate'] or datetime.now().isoformat()
            }
        })
    
    conn.close()
    return results

@app.get("/health")
def health():
    """Health check"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM stores")
        store_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "stores": store_count,
            "products": product_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
