import sys
import os

sys.path.append(r"c:\Users\Sukhi R Rao\Desktop\ShopSmart_AI")

from database import get_db_connection

def seed():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Insert/Get categories
        categories = ["Electronics", "Home Office", "Smart Home", "Books", "Sports", "Home Appliances"]
        category_ids = {}
        for cat in categories:
            cursor.execute("SELECT category_id FROM categories WHERE category_name=%s", (cat,))
            row = cursor.fetchone()
            if row:
                category_ids[cat] = row["category_id"]
            else:
                cursor.execute("INSERT INTO categories (category_name) VALUES (%s)", (cat,))
                category_ids[cat] = cursor.lastrowid
        print("Categories mapping:", category_ids)
        
        # 2. Insert/Get brands
        brands = ["Audio Engineering", "Workstation", "Furniture AI", "Computing", "Tablets", "Smart Home", "Apple", "Samsung", "Sony"]
        brand_ids = {}
        for brand in brands:
            cursor.execute("SELECT brand_id FROM brands WHERE brand_name=%s", (brand,))
            row = cursor.fetchone()
            if row:
                brand_ids[brand] = row["brand_id"]
            else:
                cursor.execute("INSERT INTO brands (brand_name) VALUES (%s)", (brand,))
                brand_ids[brand] = cursor.lastrowid
        print("Brands mapping:", brand_ids)
        
        # 3. Clean existing products (we can mark them inactive or delete them if no foreign key issues)
        # To avoid breaking historical data, let's delete cart items, recommendations etc. for a clean seed.
        cursor.execute("DELETE FROM cart_items")
        cursor.execute("DELETE FROM wishlist")
        cursor.execute("DELETE FROM recommendations")
        cursor.execute("DELETE FROM browsing_history")
        cursor.execute("DELETE FROM product_views")
        cursor.execute("DELETE FROM order_items")
        cursor.execute("DELETE FROM reviews")
        cursor.execute("DELETE FROM product_images")
        cursor.execute("DELETE FROM inventory")
        cursor.execute("DELETE FROM products")
        conn.commit()
        print("Cleared old products, inventory, and relational logs.")
        
        # 4. Insert Premium Products
        premium_products = [
            {
                "name": "Acoustic Pro-X Wireless",
                "category": "Electronics",
                "brand": "Audio Engineering",
                "price": 349.00,
                "stock": 25,
                "image": "acoustic_pro.png",
                "desc": "Adaptive noise cancellation with AI-driven spatial audio tuning for immersive sound."
            },
            {
                "name": "Vista 32\" Curved 4K",
                "category": "Electronics",
                "brand": "Workstation",
                "price": 899.00,
                "stock": 15,
                "image": "vista_monitor.png",
                "desc": "Nano-IPS technology with built-in AI auto-calibration for color-accurate professional tasks."
            },
            {
                "name": "ErgoFit Neural Desk Chair",
                "category": "Home Office",
                "brand": "Furniture AI",
                "price": 1250.00,
                "stock": 10,
                "image": "ergofit_chair.png",
                "desc": "Self-adjusting lumbar support with heat-mapping fabric for all-day comfort."
            },
            {
                "name": "ThinkPad X1 AI Edition",
                "category": "Electronics",
                "brand": "Computing",
                "price": 1899.00,
                "stock": 8,
                "image": "thinkpad_laptop.png",
                "desc": "Optimized for AI workloads with a dedicated NPU and 32GB high-speed memory."
            },
            {
                "name": "Creative Slate Pro",
                "category": "Home Office",
                "brand": "Tablets",
                "price": 1099.00,
                "stock": 12,
                "image": "creative_slate.png",
                "desc": "Perfect for digital artists with a pressure-sensitive surface and lag-free performance."
            },
            {
                "name": "EchoSphere AI Duo",
                "category": "Smart Home",
                "brand": "Smart Home",
                "price": 199.00,
                "stock": 30,
                "image": "echosphere_speakers.png",
                "desc": "Stereo smart speaker system with built-in private voice assistant."
            },
            {
                "name": "Precision Master Chronograph",
                "category": "Electronics",
                "brand": "Sony",
                "price": 1299.00,
                "stock": 5,
                "image": "chronograph_watch.png",
                "desc": "A luxury chronograph watch designed with ultimate precision and classic style."
            },
            {
                "name": "SonicPro Studio Gen 4",
                "category": "Electronics",
                "brand": "Audio Engineering",
                "price": 349.50,
                "stock": 18,
                "image": "sonicpro_headphones.png",
                "desc": "Professional studio monitor headphones with balanced audio response."
            },
            {
                "name": "AuraBeam Smart Desk Lamp",
                "category": "Smart Home",
                "brand": "Smart Home",
                "price": 89.00,
                "stock": 40,
                "image": "desk_lamp.png",
                "desc": "Smart desk lamp with adjustable color temperature and ambient sensing light control."
            }
        ]
        
        for p in premium_products:
            cursor.execute(
                """
                INSERT INTO products 
                (product_name, category_id, price, stock, image_url, brand_id, description, status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Active')
                """,
                (
                    p["name"],
                    category_ids[p["category"]],
                    p["price"],
                    p["stock"],
                    p["image"],
                    brand_ids[p["brand"]],
                    p["desc"]
                )
            )
        
        conn.commit()
        print("Successfully seeded premium products!")
        
        # Verify
        cursor.execute("SELECT COUNT(*) as count FROM products")
        print("Total products in db now:", cursor.fetchone()["count"])
        
    except Exception as e:
        conn.rollback()
        print("Error during seeding:", e)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed()
