import sys
sys.path.append(r"c:\Users\Sukhi R Rao\Desktop\ShopSmart_AI")
from database import get_db_connection

def seed_extra():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # ── CATEGORIES ──────────────────────────────────────────────
        extra_cats = [
            "Electronics", "Home Office", "Smart Home", "Gaming",
            "Fitness & Sports", "Fashion & Accessories", "Kitchen & Dining",
            "Photography", "Audio", "Wearables"
        ]
        cat_ids = {}
        for cat in extra_cats:
            cursor.execute("SELECT category_id FROM categories WHERE category_name=%s", (cat,))
            row = cursor.fetchone()
            if row:
                cat_ids[cat] = row["category_id"]
            else:
                cursor.execute("INSERT INTO categories (category_name) VALUES (%s)", (cat,))
                cat_ids[cat] = cursor.lastrowid
        print("Categories:", cat_ids)

        # ── BRANDS ─────────────────────────────────────────────────
        extra_brands = [
            "Audio Engineering", "Workstation", "Furniture AI", "Computing",
            "Tablets", "Smart Home", "Apple", "Samsung", "Sony",
            "PixelForge", "SwiftGear", "NexusWear", "CulinaryPro",
            "ZenFit", "RaptorGaming", "LumaLens", "VoltTech",
            "AeroStyle", "CoreDrive", "PulseAudio"
        ]
        brand_ids = {}
        for brand in extra_brands:
            cursor.execute("SELECT brand_id FROM brands WHERE brand_name=%s", (brand,))
            row = cursor.fetchone()
            if row:
                brand_ids[brand] = row["brand_id"]
            else:
                cursor.execute("INSERT INTO brands (brand_name) VALUES (%s)", (brand,))
                brand_ids[brand] = cursor.lastrowid
        print("Brands:", brand_ids)

        # ── PRODUCTS ───────────────────────────────────────────────
        # We keep existing images for the original 9 and assign image names
        # for new products that will fall back to emoji in the UI.
        products = [
            # ── ELECTRONICS ──
            {"name": "NexusBook Pro 16",          "cat": "Electronics",         "brand": "Computing",      "price": 2199.00, "stock": 7,  "img": "nexusbook_pro.png",       "desc": "16-inch OLED display, 64GB RAM, 2TB NVMe SSD. Built for creators and engineers."},
            {"name": "Galaxy Tab Ultra S9",        "cat": "Electronics",         "brand": "Samsung",        "price": 1099.00, "stock": 14, "img": "galaxy_tab.png",           "desc": "12.4-inch Dynamic AMOLED tablet with S-Pen and 120Hz refresh rate."},
            {"name": "iPhone 16 Pro Max",          "cat": "Electronics",         "brand": "Apple",          "price": 1399.00, "stock": 20, "img": "iphone_16.png",            "desc": "A18 Pro chip, 48MP ProRAW camera system, titanium design."},
            {"name": "Sony BRAVIA 8 OLED 65\"",   "cat": "Electronics",         "brand": "Sony",           "price": 2499.00, "stock": 5,  "img": "sony_bravia.png",          "desc": "XR Cognitive Processor, Acoustic Surface Audio+, Dolby Vision & Atmos."},
            {"name": "DualCore UHD Projector",     "cat": "Electronics",         "brand": "VoltTech",       "price": 799.00,  "stock": 9,  "img": "projector.png",            "desc": "4K laser projector with 3000 lumens, ideal for home cinema setups."},
            {"name": "Portable SSD 4TB",           "cat": "Electronics",         "brand": "CoreDrive",      "price": 249.00,  "stock": 35, "img": "portable_ssd.png",         "desc": "USB-C Gen 2×2 with AES 256-bit encryption and 2000 MB/s transfer speeds."},

            # ── HOME OFFICE ──
            {"name": "StandDesk Pro Motorized",    "cat": "Home Office",         "brand": "Furniture AI",   "price": 699.00,  "stock": 12, "img": "standdesk_pro.png",        "desc": "Electric sit-stand desk with memory presets and anti-collision sensors."},
            {"name": "MX Master 4S Mouse",         "cat": "Home Office",         "brand": "Computing",      "price": 129.00,  "stock": 40, "img": "mx_master.png",            "desc": "Ergonomic wireless mouse with MagSpeed scroll wheel and multi-device support."},
            {"name": "Keychron Q3 Mechanical",     "cat": "Home Office",         "brand": "Workstation",    "price": 169.00,  "stock": 22, "img": "keychron_q3.png",          "desc": "Tenkeyless hot-swappable mechanical keyboard with RGB backlighting."},
            {"name": "UltraWide 49\" Curved",      "cat": "Home Office",         "brand": "Workstation",    "price": 1299.00, "stock": 6,  "img": "ultrawide_monitor.png",    "desc": "Super ultrawide DQHD display for immersive multi-window productivity."},
            {"name": "Webcam 4K ProStream",        "cat": "Home Office",         "brand": "PixelForge",     "price": 199.00,  "stock": 28, "img": "webcam_prostream.png",     "desc": "4K 60fps webcam with AI background blur and low-light enhancement."},

            # ── SMART HOME ──
            {"name": "SmartThings Hub v4",         "cat": "Smart Home",          "brand": "Smart Home",     "price": 129.00,  "stock": 30, "img": "smarthings_hub.png",       "desc": "Central hub for Matter, Zigbee, and Z-Wave smart home devices."},
            {"name": "AI Robot Vacuum Pro",        "cat": "Smart Home",          "brand": "VoltTech",       "price": 549.00,  "stock": 18, "img": "robot_vacuum.png",         "desc": "LiDAR navigation, self-emptying bin, and AI room mapping."},
            {"name": "Smart Doorbell Cam 2K",      "cat": "Smart Home",          "brand": "Smart Home",     "price": 179.00,  "stock": 25, "img": "doorbell_cam.png",         "desc": "2K HDR video, package detection alerts and two-way noise-cancelling audio."},
            {"name": "Smart Thermostat Elite",     "cat": "Smart Home",          "brand": "VoltTech",       "price": 249.00,  "stock": 20, "img": "smart_thermostat.png",     "desc": "AI-learning thermostat that adapts to your schedule and reduces energy use by 23%."},

            # ── GAMING ──
            {"name": "RaptorX Pro Controller",     "cat": "Gaming",              "brand": "RaptorGaming",   "price": 89.00,   "stock": 45, "img": "raptor_controller.png",    "desc": "Pro gaming controller with Hall-effect triggers and 40h battery life."},
            {"name": "Predator Gaming Chair",      "cat": "Gaming",              "brand": "Furniture AI",   "price": 499.00,  "stock": 8,  "img": "gaming_chair.png",         "desc": "4D armrests, magnetic head pillow, and lumbar support for marathon sessions."},
            {"name": "OLED Gaming Monitor 27\"",   "cat": "Gaming",              "brand": "Workstation",    "price": 799.00,  "stock": 10, "img": "oled_monitor.png",         "desc": "QHD OLED, 240Hz, 0.03ms GTG, NVIDIA G-Sync and AMD FreeSync Premium Pro."},
            {"name": "Mechanical Gaming KB RGB",   "cat": "Gaming",              "brand": "RaptorGaming",   "price": 149.00,  "stock": 30, "img": "gaming_keyboard.png",      "desc": "Optical-mechanical switches with per-key RGB, PTFE feet and USB pass-through."},
            {"name": "Gaming Headset 7.1",        "cat": "Gaming",              "brand": "PulseAudio",     "price": 129.00,  "stock": 22, "img": "gaming_headset.png",       "desc": "Virtual 7.1 surround sound, detachable beam microphone and 50mm drivers."},
            {"name": "PS5 DualSense Edge",        "cat": "Gaming",              "brand": "Sony",           "price": 199.00,  "stock": 15, "img": "dualsense_edge.png",       "desc": "Customisable pro controller with swappable stick caps and back buttons."},

            # ── FITNESS & SPORTS ──
            {"name": "ZenFit Smart Scale Pro",     "cat": "Fitness & Sports",    "brand": "ZenFit",         "price": 79.00,   "stock": 35, "img": "smart_scale.png",          "desc": "Measures 17 body metrics including BMI, muscle mass, and hydration via BIA."},
            {"name": "Air Resistance Rower",       "cat": "Fitness & Sports",    "brand": "ZenFit",         "price": 899.00,  "stock": 6,  "img": "rowing_machine.png",       "desc": "Air resistance concept-style rowing ergometer with PM5 performance monitor."},
            {"name": "Wireless Earbuds Sport",     "cat": "Fitness & Sports",    "brand": "PulseAudio",     "price": 149.00,  "stock": 40, "img": "sport_earbuds.png",        "desc": "IPX7 waterproof, 36h total battery, secure ear fins and wind-noise reduction."},
            {"name": "Adjustable Dumbbell Set",    "cat": "Fitness & Sports",    "brand": "SwiftGear",      "price": 349.00,  "stock": 12, "img": "dumbbell_set.png",         "desc": "Replaces 15 dumbbells, 5–52.5 lbs per hand with single dial adjustment."},
            {"name": "Smart Jump Rope",            "cat": "Fitness & Sports",    "brand": "ZenFit",         "price": 59.00,   "stock": 50, "img": "smart_rope.png",           "desc": "Digital counter, calorie tracker, and Bluetooth sync with companion app."},

            # ── FASHION & ACCESSORIES ──
            {"name": "Titanium Minimalist Wallet", "cat": "Fashion & Accessories","brand": "AeroStyle",     "price": 79.00,   "stock": 60, "img": "titanium_wallet.png",      "desc": "RFID-blocking 6-card titanium wallet with quick-eject mechanism."},
            {"name": "Leather Laptop Backpack",    "cat": "Fashion & Accessories","brand": "AeroStyle",     "price": 189.00,  "stock": 20, "img": "leather_backpack.png",     "desc": "Full-grain leather, USB-A charging port, padded 16\" laptop sleeve."},
            {"name": "Polaroid Sunglasses Elite",  "cat": "Fashion & Accessories","brand": "NexusWear",     "price": 129.00,  "stock": 30, "img": "sunglasses_elite.png",     "desc": "Polarized UV400 lenses with ultra-thin titanium frame. Unisex design."},
            {"name": "Stainless Tumbler 40oz",     "cat": "Fashion & Accessories","brand": "SwiftGear",     "price": 45.00,   "stock": 80, "img": "tumbler_40oz.png",         "desc": "Triple-wall vacuum insulation keeps drinks cold 72h or hot 18h."},

            # ── KITCHEN & DINING ──
            {"name": "AI Smart Coffee Maker",      "cat": "Kitchen & Dining",    "brand": "CulinaryPro",    "price": 299.00,  "stock": 18, "img": "smart_coffee.png",         "desc": "Brew via app, schedule 6 profiles, and built-in bean grinder with freshness sensor."},
            {"name": "Pro Chef Knife Set 8pc",     "cat": "Kitchen & Dining",    "brand": "CulinaryPro",    "price": 199.00,  "stock": 25, "img": "knife_set.png",            "desc": "German high-carbon stainless steel, full tang, ergonomic pakkawood handles."},
            {"name": "Air Fryer XL 7Qt",           "cat": "Kitchen & Dining",    "brand": "VoltTech",       "price": 139.00,  "stock": 30, "img": "air_fryer.png",            "desc": "7-in-1 functions: air fry, roast, bake, dehydrate, broil, reheat, and keep warm."},
            {"name": "Espresso Machine Pro",       "cat": "Kitchen & Dining",    "brand": "CulinaryPro",    "price": 699.00,  "stock": 10, "img": "espresso_machine.png",     "desc": "15-bar pressure pump, PID temperature control, dual boiler, steam wand."},

            # ── PHOTOGRAPHY ──
            {"name": "Mirrorless Camera A7 V",     "cat": "Photography",         "brand": "LumaLens",       "price": 3299.00, "stock": 4,  "img": "mirrorless_a7.png",        "desc": "61MP BSI sensor, 5-axis IBIS, 8K video, dual card slots — the pro's choice."},
            {"name": "Drone Pro 4K Foldable",      "cat": "Photography",         "brand": "PixelForge",     "price": 799.00,  "stock": 9,  "img": "drone_4k.png",             "desc": "3-axis gimbal, obstacle avoidance, 46-min flight time, 4K/60fps HDR."},
            {"name": "GorillaPod Flex Tripod",     "cat": "Photography",         "brand": "LumaLens",       "price": 59.00,   "stock": 45, "img": "gorillapod.png",           "desc": "Flexible tripod with magnetic feet, supports up to 5kg payload."},
            {"name": "ND Filter Kit 10-piece",     "cat": "Photography",         "brand": "LumaLens",       "price": 89.00,   "stock": 30, "img": "nd_filter_kit.png",        "desc": "Multi-coated nano-glass ND2-ND1000 filters in a premium protective case."},

            # ── AUDIO ──
            {"name": "Floor Standing Speaker Pair","cat": "Audio",               "brand": "PulseAudio",     "price": 1499.00, "stock": 5,  "img": "floor_speakers.png",       "desc": "2.5-way bass-reflex towers, 6.5\" woofer, 95dB sensitivity, bi-wireable."},
            {"name": "DAC Amp Combo Desktop",      "cat": "Audio",               "brand": "PulseAudio",     "price": 399.00,  "stock": 12, "img": "dac_amp.png",              "desc": "32-bit/768kHz PCM, DSD512, balanced XLR/4.4mm outputs, MQA decoder."},
            {"name": "Studio Condenser Mic XLR",   "cat": "Audio",               "brand": "Audio Engineering","price":249.00,  "stock": 20, "img": "condenser_mic.png",        "desc": "Large-diaphragm cardioid condenser, -10dB pad, low-cut filter, shockmount."},

            # ── WEARABLES ──
            {"name": "Galaxy Watch Ultra 47mm",    "cat": "Wearables",           "brand": "Samsung",        "price": 699.00,  "stock": 18, "img": "galaxy_watch.png",         "desc": "Titanium case, health sensor cluster, 60h battery, 10ATM + MIL-STD-810H."},
            {"name": "Apple Watch Ultra 2",        "cat": "Wearables",           "brand": "Apple",          "price": 799.00,  "stock": 15, "img": "apple_watch_ultra.png",    "desc": "49mm titanium, dual-frequency GPS, Action Button, and 36h battery."},
            {"name": "Smart Ring Health Tracker",  "cat": "Wearables",           "brand": "NexusWear",      "price": 299.00,  "stock": 25, "img": "smart_ring.png",           "desc": "Continuous SpO2, HRV, body temp, sleep staging. 7-day battery life."},
            {"name": "AR Glasses NexusView",       "cat": "Wearables",           "brand": "NexusWear",      "price": 999.00,  "stock": 7,  "img": "ar_glasses.png",           "desc": "Waveguide AR display, spatial audio, 6-DOF tracking, all-day wearability."},
        ]

        inserted = 0
        skipped  = 0
        for p in products:
            # Skip if already exists
            cursor.execute("SELECT product_id FROM products WHERE product_name=%s", (p["name"],))
            if cursor.fetchone():
                skipped += 1
                continue

            cat_id   = cat_ids.get(p["cat"])
            brand_id = brand_ids.get(p["brand"])
            if not cat_id or not brand_id:
                print(f"  ⚠ Skipping {p['name']} — missing cat/brand")
                continue

            cursor.execute(
                """INSERT INTO products
                   (product_name, category_id, price, stock, image_url, brand_id, description, status)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,'Active')""",
                (p["name"], cat_id, p["price"], p["stock"], p["img"], brand_id, p["desc"])
            )
            # Add to inventory table if it exists
            pid = cursor.lastrowid
            try:
                cursor.execute(
                    "INSERT INTO inventory (product_id, quantity, reorder_level) VALUES (%s,%s,5)",
                    (pid, p["stock"])
                )
            except Exception:
                pass  # inventory table might not exist or might have different schema
            inserted += 1

        conn.commit()
        print(f"\n✅ Done! Inserted: {inserted} | Skipped (already exist): {skipped}")

        cursor.execute("SELECT COUNT(*) AS cnt FROM products")
        print(f"📦 Total products in DB: {cursor.fetchone()['cnt']}")

    except Exception as e:
        conn.rollback()
        import traceback; traceback.print_exc()
        print("❌ Error:", e)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_extra()
