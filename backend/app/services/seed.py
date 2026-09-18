from datetime import datetime, timedelta, timezone
from random import Random
from sqlalchemy import select
from app.db.session import Base, engine, SessionLocal
from app.models import Product, ProductPrice, PriceHistory, Wishlist, CartItem, PriceAlert

MARKETPLACES = ["Amazon", "Flipkart", "Croma", "Reliance Digital", "Vijay Sales", "Tata Neu", "Apple Store", "Samsung Shop"]

# Portfolio/demo catalog. Marketplace prices are simulated reference data, not live quotes.
PRODUCTS = [
("Pixel Pro 10", "Google", "Smartphones", "Flagship Android smartphone with advanced camera and clean software.", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=1000", 4.7, 12, 69999),
("Galaxy S26", "Samsung", "Smartphones", "Premium AMOLED smartphone designed for productivity and photography.", "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=1000", 4.6, 18, 74999),
("iPhone 17 Pro", "Apple", "Smartphones", "Pro camera system, high-performance silicon and premium titanium design.", "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=1000", 4.8, 16, 134999),
("OnePlus 14", "OnePlus", "Smartphones", "Fast flagship phone with a fluid display, strong cameras and all-day battery.", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=1000", 4.6, 20, 69999),
("Nothing Phone 4", "Nothing", "Smartphones", "Distinctive transparent-inspired design with a smooth high-refresh display.", "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=1000", 4.5, 22, 49999),
("Xiaomi 15 Ultra", "Xiaomi", "Smartphones", "Camera-first flagship with a bright AMOLED display and fast charging.", "https://images.unsplash.com/photo-1512499617640-c2f999098c01?w=1000", 4.5, 19, 79999),
("MacBook Air M5", "Apple", "Laptops", "Lightweight performance laptop for development, study and creative work.", "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=1000", 4.8, 8, 114999),
("IdeaPad Pro", "Lenovo", "Laptops", "Developer-friendly laptop with high-resolution display and long battery life.", "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=1000", 4.4, 24, 74990),
("Dell XPS 14", "Dell", "Laptops", "Premium Windows laptop for development, productivity and creative workflows.", "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=1000", 4.6, 17, 129990),
("ASUS ROG Zephyrus G16", "ASUS", "Laptops", "Slim gaming laptop with high-refresh OLED display and dedicated graphics.", "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=1000", 4.7, 10, 159990),
("HP Spectre x360", "HP", "Laptops", "Premium convertible laptop built for mobility, creativity and office work.", "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=1000", 4.5, 13, 124990),
("Acer Swift Go", "Acer", "Laptops", "Thin and light productivity notebook with a vivid display and efficient processor.", "https://images.unsplash.com/photo-1484788984921-03950022c9ef?w=1000", 4.3, 26, 69990),
("iPad Air M3", "Apple", "Tablets", "Versatile tablet for notes, creative work, entertainment and study.", "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=1000", 4.7, 15, 59900),
("Galaxy Tab S11", "Samsung", "Tablets", "Large AMOLED tablet with stylus support for work and entertainment.", "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=1000", 4.6, 18, 79999),
("OnePlus Pad 3", "OnePlus", "Tablets", "High-refresh productivity tablet with desktop-class multitasking.", "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=1000", 4.5, 20, 54999),
("Sony WH-1000XM6", "Sony", "Audio", "Premium noise-cancelling wireless headphones for focused work and travel.", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=1000", 4.8, 31, 32990),
("AirPods Pro 3", "Apple", "Audio", "Wireless earbuds with active noise cancellation and adaptive audio.", "https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=1000", 4.7, 45, 24999),
("Bose QuietComfort Ultra", "Bose", "Audio", "Immersive noise-cancelling headphones with spatial audio and comfort-focused design.", "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=1000", 4.7, 23, 34990),
("JBL Live Beam", "JBL", "Audio", "Everyday true wireless earbuds with punchy sound and adaptive noise cancellation.", "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=1000", 4.4, 38, 8999),
("Sonos Era 300", "Sonos", "Audio", "Premium smart speaker with spatial audio and multi-room connectivity.", "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=1000", 4.6, 14, 45990),
("Apple Watch Ultra X", "Apple", "Wearables", "Premium smartwatch with advanced fitness, outdoor and safety features.", "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=1000", 4.5, 14, 79999),
("Galaxy Watch 8 Pro", "Samsung", "Wearables", "Rugged smartwatch with health tracking, GPS and long battery life.", "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=1000", 4.5, 21, 54999),
("Garmin Venu 4", "Garmin", "Wearables", "Fitness-focused smartwatch with GPS, training insights and wellness tracking.", "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=1000", 4.6, 12, 42990),
("LG UltraFine 4K", "LG", "Monitors", "Sharp 4K monitor for coding, design and content creation with USB-C connectivity.", "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=1000", 4.5, 20, 32990),
("Samsung Odyssey G7", "Samsung", "Monitors", "High-refresh gaming monitor with immersive curved display technology.", "https://images.unsplash.com/photo-1616588589676-62b3bd4ff6d2?w=1000", 4.7, 11, 59990),
("Dell UltraSharp 32", "Dell", "Monitors", "Large color-accurate 4K monitor for professionals and creators.", "https://images.unsplash.com/photo-1585792180666-f7347c490ee2?w=1000", 4.6, 16, 64990),
("Sony Bravia XR 65", "Sony", "Televisions", "Premium 4K OLED television with cinematic processing and smart features.", "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=1000", 4.7, 9, 159990),
("LG OLED C5 55", "LG", "Televisions", "OLED smart TV designed for movies, streaming and console gaming.", "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=1000", 4.7, 12, 119990),
("Samsung Neo QLED 65", "Samsung", "Televisions", "Bright Mini LED television with rich contrast and smart TV platform.", "https://images.unsplash.com/photo-1601944179066-29786cb9d32a?w=1000", 4.6, 15, 139990),
("Sony Alpha A7 IV", "Sony", "Cameras", "Full-frame mirrorless camera for creators, photography and hybrid video.", "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=1000", 4.8, 7, 174990),
("Canon EOS R8", "Canon", "Cameras", "Compact full-frame mirrorless camera for travel, portraits and video.", "https://images.unsplash.com/photo-1606986628253-7e5c8b6a1e16?w=1000", 4.7, 8, 124990),
("GoPro Hero", "GoPro", "Cameras", "Rugged action camera for travel, sports and high-resolution video.", "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=1000", 4.5, 25, 44990),
("PlayStation 5 Slim", "Sony", "Gaming", "Current-generation console for high-fidelity gaming and fast SSD loading.", "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=1000", 4.8, 13, 54990),
("Xbox Series X", "Microsoft", "Gaming", "Powerful console built for 4K gaming, Game Pass and quick resume.", "https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=1000", 4.7, 11, 52990),
("Nintendo Switch OLED", "Nintendo", "Gaming", "Hybrid console with vivid OLED display for handheld and docked play.", "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=1000", 4.7, 18, 34990),
("Samsung T7 Shield 2TB", "Samsung", "Storage", "Portable high-speed SSD with rugged protection for files and creative projects.", "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=1000", 4.7, 33, 12999),
("WD Black SN850X 2TB", "Western Digital", "Storage", "High-performance NVMe SSD designed for gaming and demanding workloads.", "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=1000", 4.8, 28, 14999),
("TP-Link Archer AXE75", "TP-Link", "Networking", "Tri-band Wi-Fi 6E router for fast and reliable home networking.", "https://images.unsplash.com/photo-1647427060118-4911c9821b82?w=1000", 4.5, 24, 12990),
("Logitech MX Master 4", "Logitech", "Accessories", "Premium ergonomic mouse for multi-device productivity and precision work.", "https://images.unsplash.com/photo-1527814050087-3793815479db?w=1000", 4.7, 40, 9999),
("Keychron Q1 Max", "Keychron", "Accessories", "Premium mechanical keyboard with wireless connectivity and hot-swappable switches.", "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=1000", 4.6, 19, 16990),
("iPhone 17", "Apple", "Smartphones", "Premium iPhone with a high-performance chip and advanced camera system.", "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=1000", 4.7, 14, 89900),
("iPhone 17 Air", "Apple", "Smartphones", "Slim iPhone designed around a lightweight premium form factor.", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=1000", 4.6, 16, 99900),
("Galaxy S26 Ultra", "Samsung", "Smartphones", "Large flagship Galaxy phone with pro camera and productivity features.", "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=1000", 4.8, 12, 139999),
("Pixel 10 Pro XL", "Google", "Smartphones", "Large-screen Google flagship focused on computational photography and AI features.", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=1000", 4.7, 15, 109999),
("OnePlus 14R", "OnePlus", "Smartphones", "Performance-focused smartphone with fast charging and high-refresh display.", "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=1000", 4.5, 22, 44999),
("Redmi Note 15 Pro", "Xiaomi", "Smartphones", "Value-oriented smartphone with AMOLED display and versatile camera setup.", "https://images.unsplash.com/photo-1512499617640-c2f999098c01?w=1000", 4.4, 30, 29999),
("Vivo X300 Pro", "Vivo", "Smartphones", "Camera-centric premium smartphone with portrait and imaging features.", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=1000", 4.6, 20, 89999),
("OPPO Find X9 Pro", "OPPO", "Smartphones", "Premium Android phone with high-end imaging and fast charging.", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=1000", 4.5, 19, 84999),
("Lenovo Yoga Pro 9i", "Lenovo", "Laptops", "Creator laptop with high-resolution display and strong performance.", "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=1000", 4.6, 13, 139990),
("Lenovo LOQ 15", "Lenovo", "Laptops", "Gaming laptop balancing graphics performance, cooling and value.", "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=1000", 4.5, 20, 89990),
("ASUS Vivobook S 16", "ASUS", "Laptops", "Slim productivity laptop with a large display and modern processor.", "https://images.unsplash.com/photo-1484788984921-03950022c9ef?w=1000", 4.4, 24, 79990),
("ASUS TUF Gaming A15", "ASUS", "Laptops", "Durable gaming notebook with dedicated graphics and high-refresh display.", "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=1000", 4.5, 21, 84990),
("HP Pavilion Plus 14", "HP", "Laptops", "Compact premium productivity notebook for study and office work.", "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=1000", 4.4, 28, 74990),
("Dell Inspiron 14", "Dell", "Laptops", "Everyday Windows laptop for productivity and learning.", "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=1000", 4.3, 25, 62990),
("Acer Nitro V", "Acer", "Laptops", "Affordable gaming laptop with dedicated graphics and fast display.", "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=1000", 4.4, 18, 69990),
("Samsung Galaxy Book6", "Samsung", "Laptops", "Thin Galaxy laptop designed for productivity and connected-device workflows.", "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=1000", 4.5, 15, 99990),
("iPad Pro M4", "Apple", "Tablets", "High-performance tablet for creative workflows, development and media.", "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=1000", 4.8, 12, 99900),
("Galaxy Tab S11 Ultra", "Samsung", "Tablets", "Large premium Android tablet with AMOLED display and S Pen support.", "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=1000", 4.7, 14, 109999),
("Xiaomi Pad 7", "Xiaomi", "Tablets", "High-refresh Android tablet for productivity and entertainment.", "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=1000", 4.5, 25, 32999),
("Lenovo Tab P12", "Lenovo", "Tablets", "Large-screen tablet suited to study, streaming and light productivity.", "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=1000", 4.3, 27, 29999),
("Sony WF-1000XM6", "Sony", "Audio", "Premium true wireless earbuds with advanced noise cancellation.", "https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=1000", 4.7, 30, 24990),
("JBL Tune 770NC", "JBL", "Audio", "Wireless over-ear headphones with active noise cancellation.", "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=1000", 4.4, 35, 7999),
("boAt Nirvana Ion", "boAt", "Audio", "Affordable true wireless earbuds focused on battery life and everyday listening.", "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=1000", 4.2, 45, 2499),
("Marshall Major V", "Marshall", "Audio", "Portable wireless headphones with signature styling and long battery life.", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=1000", 4.6, 20, 14990),
("Sennheiser Momentum 4", "Sennheiser", "Audio", "Premium wireless headphones with detailed sound and long battery life.", "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=1000", 4.7, 17, 29990),
("Apple Watch Series 11", "Apple", "Wearables", "Everyday Apple Watch with fitness, health and smart features.", "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=1000", 4.6, 18, 46900),
("Samsung Galaxy Watch8", "Samsung", "Wearables", "Smartwatch with health tracking, fitness features and Galaxy integration.", "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=1000", 4.5, 22, 42999),
("OnePlus Watch 3", "OnePlus", "Wearables", "Smartwatch focused on fitness, battery life and Android integration.", "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=1000", 4.4, 24, 32999),
("Amazfit Balance 2", "Amazfit", "Wearables", "Fitness smartwatch with AMOLED display, GPS and training metrics.", "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=1000", 4.3, 26, 24999),
("LG OLED C4 65", "LG", "Televisions", "Premium OLED television with cinematic picture quality and gaming support.", "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=1000", 4.7, 10, 149990),
("Samsung QN90D 65", "Samsung", "Televisions", "Neo QLED television with high brightness and gaming features.", "https://images.unsplash.com/photo-1601944179066-29786cb9d32a?w=1000", 4.6, 13, 154990),
("TCL C755 55", "TCL", "Televisions", "Mini LED 4K smart TV aimed at strong value and gaming performance.", "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=1000", 4.4, 18, 69990),
("Hisense U7K 55", "Hisense", "Televisions", "4K Mini LED television with high refresh and smart TV features.", "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=1000", 4.3, 19, 64990),
("Canon EOS R6 Mark II", "Canon", "Cameras", "Full-frame mirrorless camera for photography and hybrid video.", "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=1000", 4.8, 8, 199990),
("Nikon Z6 III", "Nikon", "Cameras", "Full-frame mirrorless camera built for creators and demanding video work.", "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=1000", 4.7, 7, 209990),
("Fujifilm X-T5", "Fujifilm", "Cameras", "High-resolution APS-C mirrorless camera with classic controls.", "https://images.unsplash.com/photo-1606986628253-7e5c8b6a1e16?w=1000", 4.7, 9, 149990),
("DJI Osmo Action", "DJI", "Cameras", "Rugged action camera for travel, sports and creator workflows.", "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=1000", 4.6, 16, 39990),
("Steam Deck OLED", "Valve", "Gaming", "Portable gaming PC with OLED display and handheld controls.", "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=1000", 4.6, 12, 54990),
("PlayStation Portal", "Sony", "Gaming", "Remote-play handheld for PlayStation 5 gaming around the home.", "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=1000", 4.4, 18, 19990),
("Xbox Series S", "Microsoft", "Gaming", "Compact current-generation console designed for digital gaming.", "https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=1000", 4.5, 24, 34990),
("Samsung 990 Pro 2TB", "Samsung", "Storage", "High-performance PCIe NVMe SSD for gaming and professional workloads.", "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=1000", 4.8, 25, 15999),
("Crucial P3 Plus 2TB", "Crucial", "Storage", "Affordable PCIe NVMe storage for desktop and laptop upgrades.", "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=1000", 4.5, 30, 10999),
("SanDisk Extreme Portable 2TB", "SanDisk", "Storage", "Portable SSD for creators, travel and fast file transfers.", "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=1000", 4.7, 32, 13999),
("TP-Link Archer AX73", "TP-Link", "Networking", "Wi-Fi 6 router for fast multi-device home networking.", "https://images.unsplash.com/photo-1647427060118-4911c9821b82?w=1000", 4.5, 28, 9990),
("ASUS RT-AX86U", "ASUS", "Networking", "Gaming-oriented Wi-Fi 6 router with strong coverage and controls.", "https://images.unsplash.com/photo-1647427060118-4911c9821b82?w=1000", 4.6, 19, 18990),
("Logitech G Pro X Superlight 2", "Logitech", "Accessories", "Lightweight gaming mouse designed for competitive play.", "https://images.unsplash.com/photo-1527814050087-3793815479db?w=1000", 4.7, 21, 13999),
("Razer BlackWidow V4", "Razer", "Accessories", "Mechanical gaming keyboard with programmable controls and RGB lighting.", "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=1000", 4.6, 16, 15999),
("Anker 737 Power Bank", "Anker", "Power Banks", "High-capacity USB-C power bank for laptops, tablets and phones.", "https://images.unsplash.com/photo-1609592424365-8e3f4c13b0e9?w=1000", 4.6, 25, 9999),
("Belkin 3-in-1 MagSafe Charger", "Belkin", "Accessories", "Multi-device wireless charging station for compatible devices.", "https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=1000", 4.5, 20, 10999),
("Amazon Echo Show 8", "Amazon", "Smart Home", "Smart display for voice control, media and connected-home routines.", "https://images.unsplash.com/photo-1558089687-f282ffcbc126?w=1000", 4.4, 20, 13999),
("Google Nest Hub", "Google", "Smart Home", "Compact smart display for routines, media and connected-home control.", "https://images.unsplash.com/photo-1558089687-f282ffcbc126?w=1000", 4.3, 22, 7999),
("Epson CO-FH02", "Epson", "Projectors", "Compact home projector for entertainment and presentations.", "https://images.unsplash.com/photo-1603481546238-487240415921?w=1000", 4.4, 11, 69990),
("BenQ TK700", "BenQ", "Projectors", "4K gaming projector with low-latency features and HDR support.", "https://images.unsplash.com/photo-1603481546238-487240415921?w=1000", 4.6, 9, 119990),
("HP LaserJet MFP 136w", "HP", "Printers", "Compact wireless multifunction printer for home and small office use.", "https://images.unsplash.com/photo-1612815154858-60aa4c59eaa6?w=1000", 4.3, 18, 15999),
("Canon PIXMA G3770", "Canon", "Printers", "Wireless ink-tank multifunction printer for home and student workflows.", "https://images.unsplash.com/photo-1612815154858-60aa4c59eaa6?w=1000", 4.5, 20, 16999),
("LG 1.5 Ton 5 Star AC", "LG", "Air Conditioners", "Energy-efficient split air conditioner for residential cooling.", "https://images.unsplash.com/photo-1631545806609-0f3a7b9b6b9f?w=1000", 4.5, 12, 44990),
("Samsung 1.5 Ton WindFree AC", "Samsung", "Air Conditioners", "WindFree split air conditioner with smart connectivity.", "https://images.unsplash.com/photo-1631545806609-0f3a7b9b6b9f?w=1000", 4.4, 13, 47990),
("Daikin 1.5 Ton Inverter AC", "Daikin", "Air Conditioners", "Inverter split air conditioner focused on efficient cooling.", "https://images.unsplash.com/photo-1631545806609-0f3a7b9b6b9f?w=1000", 4.6, 15, 45990),
("LG 655 L Side-by-Side Refrigerator", "LG", "Refrigerators", "Large-capacity refrigerator with modern cooling and storage features.", "https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?w=1000", 4.5, 8, 84990),
("Samsung 653 L Side-by-Side Refrigerator", "Samsung", "Refrigerators", "Large smart refrigerator with flexible storage and cooling.", "https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?w=1000", 4.5, 9, 89990),
]

def price_set(base: float, brand: str, rng: Random, variant: int = 0):
    """Create realistic demo comparison offers with a rotating cheapest retailer.

    These are reference/demo prices, not live retailer quotes.  The rotation is
    intentional so the UI demonstrates genuine cross-marketplace comparison
    rather than making one retailer win every product.
    """
    # Each row has a different cheapest marketplace.  Small jitter prevents
    # identical percentage gaps while keeping the spread plausible.
    patterns = [
        [-0.030, -0.008, 0.012, 0.020, 0.030, 0.042, 0.016, 0.024],  # Amazon
        [-0.010, -0.032, 0.008, 0.018, 0.028, 0.041, 0.015, 0.023],  # Flipkart
        [0.010, -0.006, -0.034, 0.014, 0.026, 0.038, 0.017, 0.022],  # Croma
        [0.012, -0.004, 0.010, -0.036, 0.022, 0.035, 0.016, 0.020],  # Reliance
        [0.014, -0.003, 0.009, 0.017, -0.038, 0.031, 0.015, 0.019],  # Vijay
        [0.016, -0.002, 0.011, 0.019, 0.025, -0.040, 0.013, 0.021],  # Tata
        [0.012, -0.004, 0.010, 0.018, 0.024, 0.034, -0.037, 0.020],  # Apple
        [0.011, -0.005, 0.009, 0.017, 0.023, 0.033, 0.014, -0.039],  # Samsung
    ]
    offsets = patterns[variant % len(patterns)]
    prices = []
    for market, off in zip(MARKETPLACES, offsets):
        if brand == "Apple" and market == "Samsung Shop":
            continue
        if brand == "Samsung" and market == "Apple Store":
            continue
        # Brand-owned stores get a modest advantage on their own products,
        # while general retailers remain competitive.
        if brand == "Apple" and market == "Apple Store":
            off -= 0.008
        if brand == "Samsung" and market == "Samsung Shop":
            off -= 0.008
        price = round(base * (1 + off + rng.uniform(-0.003, 0.003)) / 10) * 10
        discount = max(2.0, round(rng.uniform(4, 17), 1))
        prices.append((market, float(price), discount))
    return prices

def seed():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    rng = Random(42)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    # Remove aliases from the first prototype so the upgraded catalog does not
    # show visually duplicated legacy products. This is demo-data cleanup only.
    legacy_names = {"GalaxyS26", "WH-1000XM6", "Watch Ultra X", "Smart Monitor 4K"}
    legacy_products = db.scalars(select(Product).where(Product.name.in_(legacy_names))).all()
    for legacy in legacy_products:
        db.query(Wishlist).filter(Wishlist.product_id == legacy.id).delete(synchronize_session=False)
        db.query(CartItem).filter(CartItem.product_id == legacy.id).delete(synchronize_session=False)
        db.query(PriceAlert).filter(PriceAlert.product_id == legacy.id).delete(synchronize_session=False)
        db.query(ProductPrice).filter(ProductPrice.product_id == legacy.id).delete(synchronize_session=False)
        db.query(PriceHistory).filter(PriceHistory.product_id == legacy.id).delete(synchronize_session=False)
        db.delete(legacy)
    db.flush()

    for product_index, row in enumerate(PRODUCTS):
        name, brand, cat, desc, img, rating, stock, base = row
        p = db.scalar(select(Product).where(Product.name == name))
        if not p:
            p = Product(name=name, brand=brand, category=cat, description=desc, image_url=img, rating=rating, stock=stock)
            db.add(p); db.flush()
        else:
            p.brand, p.category, p.description, p.image_url, p.rating, p.stock = brand, cat, desc, img, rating, stock

        existing_by_market = {x.marketplace: x for x in p.prices}
        current = price_set(base, brand, rng, product_index)
        current_markets = {market for market, _, _ in current}
        # Remove stale/legacy marketplace aliases so every product has a clean,
        # consistent comparison matrix after repeated seed runs.
        for market, row in list(existing_by_market.items()):
            if market not in current_markets:
                db.delete(row)
        for market, price, disc in current:
            row = existing_by_market.get(market)
            if row:
                row.price, row.discount_pct, row.recorded_at = price, disc, now
            else:
                db.add(ProductPrice(product_id=p.id, marketplace=market, price=price, discount_pct=disc, recorded_at=now))
        # Remove history records for stores that are no longer valid for this product.
        db.query(PriceHistory).filter(PriceHistory.product_id == p.id, ~PriceHistory.marketplace.in_(current_markets)).delete(synchronize_session=False)

        # 21-day historical series for a smooth price chart.
        hist_count = db.query(PriceHistory).filter(PriceHistory.product_id == p.id).count()
        if hist_count < 40:
            for day in range(20, -1, -1):
                recorded = now - timedelta(days=day)
                for market, current_price, _ in current:
                    drift = 1 + (rng.uniform(-0.055, 0.055) * (day / 20))
                    price = round(current_price * drift / 10) * 10
                    db.add(PriceHistory(product_id=p.id, marketplace=market, price=float(price), recorded_at=recorded))

    db.commit(); db.close()

if __name__ == "__main__": seed()
