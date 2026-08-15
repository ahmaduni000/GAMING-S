"""
GameZone Hub - Database Seed Script
Run: python seed.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date, timedelta
from app import create_app, db
from app.models.user import User, Role, Technician
from app.models.product import Category, Product, ProductImage
from app.models.service import Service
from app.models.communication import Announcement, Banner, ContactMessage
from app.models.settings import PaymentSettings
from app.models.order import Order, OrderItem, Payment, BillingDetail
from app.models.review import Review
from app.models.cart import Cart, Wishlist
from app.utils.helpers import slugify


def seed_database():
    app = create_app()
    with app.app_context():
        print("ðŸ—‘ï¸  Dropping all tables...")
        db.drop_all()
        print("ðŸ“¦ Creating all tables...")
        db.create_all()

        # === ROLES ===
        print("ðŸ‘¤ Creating roles...")
        admin_role = Role(name='admin', description='Administrator')
        staff_role = Role(name='staff', description='Staff Member')
        tech_role = Role(name='technician', description='Technician')
        customer_role = Role(name='customer', description='Customer')
        db.session.add_all([admin_role, staff_role, tech_role, customer_role])
        db.session.flush()

        # === USERS ===
        print("ðŸ‘¤ Creating users...")
        admin = User(username='admin', email='admin@gamezone.com', first_name='Admin', last_name='User', phone='1234567890')
        admin.set_password('admin123')
        admin.roles.append(admin_role)
        admin.is_active = True

        staff1 = User(username='staff1', email='staff@gamezone.com', first_name='John', last_name='Staff', phone='1234567891')
        staff1.set_password('staff123')
        staff1.roles.append(staff_role)
        staff1.is_active = True

        staff2 = User(username='staff2', email='sarah@gamezone.com', first_name='Sarah', last_name='Wilson', phone='1234567892')
        staff2.set_password('staff123')
        staff2.roles.append(staff_role)
        staff2.is_active = True

        tech_user1 = User(username='tech1', email='tech@gamezone.com', first_name='Mike', last_name='Tech', phone='1234567893')
        tech_user1.set_password('tech123')
        tech_user1.roles.append(tech_role)
        tech_user1.is_active = True

        tech_user2 = User(username='tech2', email='alex@gamezone.com', first_name='Alex', last_name='Repair', phone='1234567894')
        tech_user2.set_password('tech123')
        tech_user2.roles.append(tech_role)
        tech_user2.is_active = True

        customer1 = User(username='gamer1', email='gamer1@example.com', first_name='Chris', last_name='Gaming', phone='1234567895')
        customer1.set_password('customer123')
        customer1.roles.append(customer_role)
        customer1.is_active = True

        customer2 = User(username='gamer2', email='gamer2@example.com', first_name='Emma', last_name='Player', phone='1234567896')
        customer2.set_password('customer123')
        customer2.roles.append(customer_role)
        customer2.is_active = True

        customer3 = User(username='gamer3', email='gamer3@example.com', first_name='David', last_name='Pro', phone='1234567897')
        customer3.set_password('customer123')
        customer3.roles.append(customer_role)
        customer3.is_active = True

        db.session.add_all([admin, staff1, staff2, tech_user1, tech_user2, customer1, customer2, customer3])
        db.session.flush()

        # === TECHNICIANS ===
        print("ðŸ”§ Creating technicians...")
        tech1 = Technician(user_id=tech_user1.id, skills='PC Building, Console Repair, Software Installation', experience_years=5, hourly_rate=25.00, is_available=True, bio='Expert in PC building and gaming console repairs with 5 years of experience.')
        tech2 = Technician(user_id=tech_user2.id, skills='Network Setup, Hardware Upgrades, Console Modding', experience_years=3, hourly_rate=20.00, is_available=True, bio='Specialist in network configuration and hardware upgrades.')
        db.session.add_all([tech1, tech2])
        db.session.flush()

        # === CARTS & WISHLISTS ===
        print("ðŸ›’ Creating carts and wishlists...")
        for user in [customer1, customer2, customer3]:
            cart = Cart(user_id=user.id)
            wishlist = Wishlist(user_id=user.id)
            db.session.add_all([cart, wishlist])
        db.session.flush()

        # === CATEGORIES ===
        print("ðŸ“‚ Creating categories...")
        cat_gaming = Category(name='Gaming Consoles', slug='gaming-consoles', description='Latest gaming consoles and accessories', is_active=True, sort_order=1)
        cat_pc = Category(name='Gaming PCs', slug='gaming-pcs', description='Custom and pre-built gaming PCs', is_active=True, sort_order=2)
        cat_accessories = Category(name='Accessories', slug='accessories', description='Gaming accessories and peripherals', is_active=True, sort_order=3)
        cat_components = Category(name='PC Components', slug='pc-components', description='Graphics cards, processors, RAM, and more', is_active=True, sort_order=4)
        cat_merch = Category(name='Gaming Merchandise', slug='gaming-merchandise', description='Gaming apparel and collectibles', is_active=True, sort_order=5)

        # Subcategories
        cat_keyboards = Category(name='Keyboards', slug='keyboards', description='Mechanical and gaming keyboards', parent_id=cat_accessories.id, is_active=True, sort_order=1)
        cat_mice = Category(name='Mice', slug='mice', description='Gaming mice and mousepads', parent_id=cat_accessories.id, is_active=True, sort_order=2)
        cat_headsets = Category(name='Headsets', slug='headsets', description='Gaming headsets and audio', parent_id=cat_accessories.id, is_active=True, sort_order=3)

        db.session.add_all([cat_gaming, cat_pc, cat_accessories, cat_components, cat_merch, cat_keyboards, cat_mice, cat_headsets])
        db.session.flush()

        # === PRODUCTS ===
        print("ðŸ“¦ Creating products...")
        products_data = [
            {
                'name': 'PlayStation 5 Console',
                'slug': 'playstation-5-console',
                'description': 'Experience lightning-fast loading with an ultra-high speed SSD, deeper immersion with haptic feedback, adaptive triggers, and 3D Audio.',
                'features': '8K Support, Ray Tracing, 120fps, 825GB SSD, DualSense Controller',
                'price': 499.99,
                'discount_price': 449.99,
                'discount_percent': 10.0,
                'sku': 'PS5-CONSOLE-001',
                'brand': 'Sony',
                'category_id': cat_gaming.id,
                'stock_quantity': 25,
                'low_stock_threshold': 5,
                'is_active': True,
                'is_featured': True,
                'is_bestseller': True,
            },
            {
                'name': 'Xbox Series X',
                'slug': 'xbox-series-x',
                'description': 'The fastest, most powerful Xbox ever. Play thousands of games from four generations with backward compatibility.',
                'features': '4K at 120fps, 12TB SSD, Quick Resume, Smart Delivery, Dolby Atmos',
                'price': 499.99,
                'sku': 'XBOX-SX-001',
                'brand': 'Microsoft',
                'category_id': cat_gaming.id,
                'stock_quantity': 20,
                'low_stock_threshold': 5,
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': 'Nintendo Switch OLED',
                'slug': 'nintendo-switch-oled',
                'description': 'Play anywhere with the vibrant 7-inch OLED screen. Perfect for gaming on the go and at home.',
                'features': '7-inch OLED, Enhanced Audio, Wide Adjustable Stand, Wired LAN Port',
                'price': 349.99,
                'sku': 'NSW-OLED-001',
                'brand': 'Nintendo',
                'category_id': cat_gaming.id,
                'stock_quantity': 30,
                'low_stock_threshold': 5,
                'is_active': True,
                'is_new_arrival': True,
            },
            {
                'name': 'RTX 4070 Ti Graphics Card',
                'slug': 'rtx-4070-ti',
                'description': 'NVIDIA GeForce RTX 4070 Ti with 12GB GDDR6X memory for incredible gaming performance.',
                'features': '12GB GDDR6X, DLSS 3, Ray Tracing, 4K Gaming',
                'price': 799.99,
                'discount_price': 749.99,
                'discount_percent': 6.3,
                'sku': 'GPU-RTX4070TI',
                'brand': 'NVIDIA',
                'category_id': cat_components.id,
                'stock_quantity': 15,
                'low_stock_threshold': 3,
                'is_active': True,
                'is_featured': True,
                'is_bestseller': True,
            },
            {
                'name': 'Gaming Mechanical Keyboard RGB',
                'slug': 'gaming-mechanical-keyboard',
                'description': 'Premium mechanical gaming keyboard with RGB backlighting, hot-swappable switches, and aluminum frame.',
                'features': 'Cherry MX Switches, RGB Lighting, Hot-Swap, USB-C, N-Key Rollover',
                'price': 129.99,
                'sku': 'KB-MECH-RGB',
                'brand': 'HyperX',
                'category_id': cat_keyboards.id,
                'stock_quantity': 50,
                'low_stock_threshold': 10,
                'is_active': True,
                'is_bestseller': True,
            },
            {
                'name': 'Wireless Gaming Mouse',
                'slug': 'wireless-gaming-mouse',
                'description': 'Ultra-lightweight wireless gaming mouse with 25K DPI sensor and 70-hour battery life.',
                'features': '25K DPI, 70hr Battery, 63g Weight, Wireless Charging',
                'price': 89.99,
                'sku': 'MOUSE-WL-001',
                'brand': 'Logitech',
                'category_id': cat_mice.id,
                'stock_quantity': 40,
                'low_stock_threshold': 10,
                'is_active': True,
            },
            {
                'name': 'Gaming Headset 7.1 Surround',
                'slug': 'gaming-headset-71',
                'description': 'Premium gaming headset with 7.1 virtual surround sound, noise-cancelling mic, and memory foam ear cups.',
                'features': '7.1 Surround, Noise-Cancelling Mic, Memory Foam, RGB',
                'price': 149.99,
                'discount_price': 119.99,
                'discount_percent': 20.0,
                'sku': 'HS-71-SURR',
                'brand': 'SteelSeries',
                'category_id': cat_headsets.id,
                'stock_quantity': 35,
                'low_stock_threshold': 8,
                'is_active': True,
                'is_new_arrival': True,
            },
            {
                'name': 'Ryzen 9 7900X Processor',
                'slug': 'ryzen-9-7900x',
                'description': 'AMD Ryzen 9 7900X 12-core desktop processor for ultimate gaming and content creation.',
                'features': '12 Cores, 24 Threads, 4.7GHz Base, 5.6GHz Boost, 170W TDP',
                'price': 449.99,
                'sku': 'CPU-R9-7900X',
                'brand': 'AMD',
                'category_id': cat_components.id,
                'stock_quantity': 18,
                'low_stock_threshold': 5,
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': 'Custom Gaming PC Build',
                'slug': 'custom-gaming-pc',
                'description': 'Pre-built custom gaming PC with RTX 4070, Ryzen 7 7800X3D, 32GB DDR5, 1TB NVMe SSD.',
                'features': 'RTX 4070, Ryzen 7 7800X3D, 32GB DDR5, 1TB NVMe, RGB Case',
                'price': 1599.99,
                'discount_price': 1449.99,
                'discount_percent': 9.4,
                'sku': 'PC-CUSTOM-001',
                'brand': 'GameZone',
                'category_id': cat_pc.id,
                'stock_quantity': 8,
                'low_stock_threshold': 3,
                'is_active': True,
                'is_featured': True,
                'is_bestseller': True,
            },
            {
                'name': 'Gaming T-Shirt - Pro Player',
                'slug': 'gaming-tshirt-pro',
                'description': 'Premium cotton gaming t-shirt with exclusive GameZone Pro Player design.',
                'features': '100% Cotton, Machine Washable, Unisex Fit, Multiple Sizes',
                'price': 29.99,
                'sku': 'TSHIRT-PRO-001',
                'brand': 'GameZone',
                'category_id': cat_merch.id,
                'stock_quantity': 100,
                'low_stock_threshold': 20,
                'is_active': True,
            },
            {
                'name': 'PS5 DualSense Wireless Controller',
                'slug': 'ps5-dualsense-controller',
                'description': 'Official Sony DualSense wireless controller with haptic feedback and adaptive triggers.',
                'features': 'Haptic Feedback, Adaptive Triggers, USB-C, Built-in Microphone, 12hr Battery',
                'price': 69.99,
                'discount_price': 59.99,
                'discount_percent': 14.3,
                'sku': 'CTRL-DS-001',
                'brand': 'Sony',
                'category_id': cat_accessories.id,
                'stock_quantity': 60,
                'low_stock_threshold': 15,
                'is_active': True,
                'is_bestseller': True,
            },
            {
                'name': '27" 165Hz Gaming Monitor',
                'slug': 'gaming-monitor-27',
                'description': '27-inch IPS gaming monitor with 165Hz refresh rate, 1ms response time, and AMD FreeSync.',
                'features': '27" IPS, 165Hz, 1ms, FreeSync Premium, HDR400, 1080p',
                'price': 299.99,
                'discount_price': 269.99,
                'discount_percent': 10.0,
                'sku': 'MON-27-165',
                'brand': 'ASUS',
                'category_id': cat_accessories.id,
                'stock_quantity': 22,
                'low_stock_threshold': 5,
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': 'Ergonomic Gaming Chair',
                'slug': 'ergonomic-gaming-chair',
                'description': 'Premium ergonomic gaming chair with lumbar support, adjustable armrests, and reclining backrest.',
                'features': 'Lumbar Support, Adjustable Armrests, 180 Recline, PU Leather, 150kg Capacity',
                'price': 199.99,
                'sku': 'CHAIR-ERG-001',
                'brand': 'GameZone',
                'category_id': cat_accessories.id,
                'stock_quantity': 15,
                'low_stock_threshold': 3,
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': '1TB NVMe M.2 SSD',
                'slug': '1tb-nvme-ssd',
                'description': 'High-speed 1TB NVMe M.2 SSD with read speeds up to 7000MB/s for blazing fast load times.',
                'features': '1TB Capacity, 7000MB/s Read, 5500MB/s Write, PCIe Gen4, TLC NAND',
                'price': 89.99,
                'discount_price': 79.99,
                'discount_percent': 11.1,
                'sku': 'SSD-1TB-NVME',
                'brand': 'Samsung',
                'category_id': cat_components.id,
                'stock_quantity': 45,
                'low_stock_threshold': 10,
                'is_active': True,
                'is_bestseller': True,
            },
            {
                'name': 'DDR5 RAM 32GB (2x16GB)',
                'slug': 'ddr5-ram-32gb',
                'description': '32GB DDR5 RAM kit running at 6000MHz with RGB lighting and AMD EXPO support.',
                'features': '32GB (2x16GB), 6000MHz, CL30, RGB, AMD EXPO, XMP 3.0',
                'price': 119.99,
                'sku': 'RAM-DDR5-32',
                'brand': 'Corsair',
                'category_id': cat_components.id,
                'stock_quantity': 35,
                'low_stock_threshold': 8,
                'is_active': True,
                'is_new_arrival': True,
            },
            {
                'name': '15.6" Gaming Laptop RTX 4060',
                'slug': 'gaming-laptop-rtx4060',
                'description': 'Powerful gaming laptop with RTX 4060, Intel i7-13700H, 16GB DDR5, 512GB NVMe SSD.',
                'features': 'RTX 4060, i7-13700H, 16GB DDR5, 512GB SSD, 15.6" 144Hz, RGB Keyboard',
                'price': 1299.99,
                'discount_price': 1199.99,
                'discount_percent': 7.7,
                'sku': 'LAP-RTX4060',
                'brand': 'ASUS',
                'category_id': cat_pc.id,
                'stock_quantity': 10,
                'low_stock_threshold': 3,
                'is_active': True,
                'is_featured': True,
                'is_bestseller': True,
            },
            {
                'name': 'PS5 Digital Edition',
                'slug': 'ps5-digital-edition',
                'description': 'PlayStation 5 Digital Edition - slimmer, lighter, and disc-free gaming at its best.',
                'features': '825GB SSD, 4K Gaming, 120fps, Ray Tracing, DualSense Included',
                'price': 399.99,
                'sku': 'PS5-DIG-001',
                'brand': 'Sony',
                'category_id': cat_gaming.id,
                'stock_quantity': 18,
                'low_stock_threshold': 5,
                'is_active': True,
                'is_new_arrival': True,
            },
            {
                'name': 'XL Extended RGB Mousepad',
                'slug': 'xl-rgb-mousepad',
                'description': 'Extra-large extended gaming mousepad with customizable RGB lighting and stitched edges.',
                'features': '900x400mm, RGB 16.8M Colors, Waterproof, Stitched Edges, USB Powered',
                'price': 34.99,
                'sku': 'MPAD-XL-RGB',
                'brand': 'HyperX',
                'category_id': cat_mice.id,
                'stock_quantity': 55,
                'low_stock_threshold': 15,
                'is_active': True,
            },
            {
                'name': 'Gaming Hoodie - Elite Edition',
                'slug': 'gaming-hoodie-elite',
                'description': 'Premium gaming hoodie with GameZone Elite Edition design. Perfect for gaming sessions.',
                'features': '80% Cotton, 20% Polyester, Kangaroo Pocket, Adjustable Hood, Unisex',
                'price': 49.99,
                'sku': 'HOOD-ELITE-001',
                'brand': 'GameZone',
                'category_id': cat_merch.id,
                'stock_quantity': 75,
                'low_stock_threshold': 15,
                'is_active': True,
                'is_new_arrival': True,
            },
            {
                'name': '1080p 60fps Streaming Webcam',
                'slug': 'streaming-webcam-1080p',
                'description': 'Full HD 1080p webcam with auto-focus, built-in microphone, and low-light correction.',
                'features': '1080p 60fps, Auto-Focus, Built-in Mic, Low-Light Correction, Clip Mount',
                'price': 59.99,
                'discount_price': 49.99,
                'discount_percent': 16.7,
                'sku': 'CAM-1080-60',
                'brand': 'Logitech',
                'category_id': cat_accessories.id,
                'stock_quantity': 40,
                'low_stock_threshold': 10,
                'is_active': True,
                'is_bestseller': True,
            },
            {
                'name': 'Gaming Mouse - RGB Ultra Lightweight',
                'slug': 'gaming-mouse-rgb',
                'description': 'Ergonomic gaming mouse with RGB lighting and adjustable DPI settings up to 16000.',
                'features': 'RGB Lighting, Adjustable DPI up to 16000, Ergonomic Design, 80g Weight, Programmable Buttons',
                'price': 64.99,
                'sku': 'MOUSE-RGB-001',
                'brand': 'Razer',
                'category_id': cat_mice.id,
                'stock_quantity': 60,
                'low_stock_threshold': 10,
                'is_active': True,
                'is_new_arrival': True,
            },
            {
                'name': 'Mechanical Gaming Keyboard - TKL',
                'slug': 'mechanical-gaming-keyboard-tkl',
                'description': 'Tenkeyless mechanical gaming keyboard with RGB backlighting and brown switches.',
                'features': 'RGB Backlighting, Brown Switches, TKL Layout, USB-C, Macro Support',
                'price': 99.99,
                'sku': 'KB-MECH-TKL',
                'brand': 'Corsair',
                'category_id': cat_keyboards.id,
                'stock_quantity': 35,
                'low_stock_threshold': 8,
                'is_active': True,
                'is_bestseller': True,
            },
            {
                'name': 'Wireless Gaming Keyboard',
                'slug': 'wireless-gaming-keyboard',
                'description': 'Low-latency wireless mechanical keyboard with RGB and long battery life.',
                'features': '2.4GHz Wireless, RGB Lighting, 200hr Battery, Hot-Swap, Aluminum Frame',
                'price': 119.99,
                'discount_price': 99.99,
                'discount_percent': 16.7,
                'sku': 'KB-WL-001',
                'brand': 'Logitech',
                'category_id': cat_keyboards.id,
                'stock_quantity': 25,
                'low_stock_threshold': 5,
                'is_active': True,
                'is_new_arrival': True,
            },
            {
                'name': 'Gaming Mousepad - XXL Desk Mat',
                'slug': 'gaming-mousepad-xxl',
                'description': 'Extra-extra-large desk mat covering your entire desk with smooth surface for gaming.',
                'features': '900x400mm, Smooth Surface, Non-slip Base, Water Resistant, Stitched Edges',
                'price': 29.99,
                'sku': 'MPAD-XXL-001',
                'brand': 'SteelSeries',
                'category_id': cat_mice.id,
                'stock_quantity': 80,
                'low_stock_threshold': 15,
                'is_active': True,
            },
            {
                'name': 'Gaming Headset - Wireless 2.4GHz',
                'slug': 'gaming-headset-wireless',
                'description': 'Wireless gaming headset with 2.4GHz connection, 50mm drivers, and 30-hour battery.',
                'features': '2.4GHz Wireless, 50mm Drivers, 30hr Battery, Detachable Mic, 7.1 Surround',
                'price': 129.99,
                'sku': 'HS-WL-001',
                'brand': 'HyperX',
                'category_id': cat_headsets.id,
                'stock_quantity': 40,
                'low_stock_threshold': 8,
                'is_active': True,
                'is_bestseller': True,
            },
            {
                'name': 'Gaming Chair - Racing Style',
                'slug': 'gaming-chair-racing',
                'description': 'Racing style gaming chair with lumbar support, adjustable armrests, and reclining backrest.',
                'features': 'Lumbar Support, Adjustable Armrests, Reclining up to 180°, Metal Base, Neck Pillow',
                'price': 159.99,
                'discount_price': 139.99,
                'discount_percent': 12.5,
                'sku': 'CHAIR-RACING-001',
                'brand': 'GameZone',
                'category_id': cat_accessories.id,
                'stock_quantity': 20,
                'low_stock_threshold': 5,
                'is_active': True,
                'is_new_arrival': True,
            },
            {
                'name': '144Hz Gaming Monitor - 27 inch',
                'slug': 'gaming-monitor-144hz',
                'description': '27-inch IPS gaming monitor with 144Hz refresh rate and 1ms response time for smooth gameplay.',
                'features': '27" IPS, 144Hz, 1ms Response Time, FreeSync Premium, HDR400, Height Adjustable',
                'price': 279.99,
                'sku': 'MON-144HZ-001',
                'brand': 'ASUS',
                'category_id': cat_accessories.id,
                'stock_quantity': 18,
                'low_stock_threshold': 5,
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': 'Gaming Controller - Elite Series',
                'slug': 'gaming-controller-elite',
                'description': 'Premium gaming controller with customizable paddles, hair triggers, and interchangeable thumbsticks.',
                'features': 'Customizable Paddles, Hair Triggers, Interchangeable Sticks, Bluetooth, USB-C',
                'price': 149.99,
                'sku': 'CTRL-ELITE-001',
                'brand': 'Microsoft',
                'category_id': cat_accessories.id,
                'stock_quantity': 30,
                'low_stock_threshold': 8,
                'is_active': True,
                'is_bestseller': True,
            },
            {
                'name': 'Gaming Microphone - USB Condenser',
                'slug': 'gaming-microphone-usb',
                'description': 'USB condenser microphone with cardioid pattern, perfect for streaming and gaming communication.',
                'features': 'Cardioid Pattern, Zero-Latency Monitoring, RGB Ring, Pop Filter, Desk Stand',
                'price': 89.99,
                'discount_price': 74.99,
                'discount_percent': 16.7,
                'sku': 'MIC-USB-001',
                'brand': 'Blue',
                'category_id': cat_accessories.id,
                'stock_quantity': 45,
                'low_stock_threshold': 10,
                'is_active': True,
                'is_new_arrival': True,
            },
            {
                'name': 'Gaming Desk - RGB LED',
                'slug': 'gaming-desk-rgb',
                'description': 'Spacious gaming desk with RGB LED lighting, cable management, and carbon fiber texture.',
                'features': 'RGB LED Strip, Cable Management, Carbon Fiber Top, Cup Holder, Headphone Hook',
                'price': 199.99,
                'sku': 'DESK-RGB-001',
                'brand': 'GameZone',
                'category_id': cat_accessories.id,
                'stock_quantity': 12,
                'low_stock_threshold': 3,
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': 'Gaming Capture Card - 4K',
                'slug': 'gaming-capture-card-4k',
                'description': '4K capture card for streaming and recording gameplay from consoles and PC.',
                'features': '4K Passthrough, 1080p 60fps Capture, USB 3.0, HDMI 2.0, Low Latency',
                'price': 179.99,
                'sku': 'CAP-4K-001',
                'brand': 'Elgato',
                'category_id': cat_accessories.id,
                'stock_quantity': 22,
                'low_stock_threshold': 5,
                'is_active': True,
                'is_new_arrival': True,
            },
            {
                'name': 'Gaming Router - WiFi 6',
                'slug': 'gaming-router-wifi6',
                'description': 'Tri-band WiFi 6 gaming router with dedicated gaming port and low latency optimization.',
                'features': 'WiFi 6, Tri-Band, Gaming Port, QoS, 2.5G WAN, RGB',
                'price': 249.99,
                'discount_price': 219.99,
                'discount_percent': 12.0,
                'sku': 'ROUTER-WIFI6',
                'brand': 'ASUS',
                'category_id': cat_accessories.id,
                'stock_quantity': 15,
                'low_stock_threshold': 3,
                'is_active': True,
                'is_bestseller': True,
            },
        ]

        for pdata in products_data:
            product = Product(**pdata)
            db.session.add(product)
        db.session.flush()

        # === PRODUCT IMAGES ===
        print("ðŸ–¼ï¸  Creating product images...")
        image_map = {
            'playstation-5-console': 'ps5.svg',
            'xbox-series-x': 'xbox.svg',
            'nintendo-switch-oled': 'switch.svg',
            'rtx-4070-ti': 'gpu.svg',
            'gaming-mechanical-keyboard': 'keyboard.svg',
            'wireless-gaming-mouse': 'mouse.svg',
            'gaming-headset-71': 'headset.svg',
            'ryzen-9-7900x': 'cpu.svg',
            'custom-gaming-pc': 'pc.svg',
            'gaming-tshirt-pro': 'tshirt.svg',
            'ps5-dualsense-controller': 'controller.svg',
            'gaming-monitor-27': 'monitor.svg',
            'ergonomic-gaming-chair': 'chair.svg',
            '1tb-nvme-ssd': 'ssd.svg',
            'ddr5-ram-32gb': 'ram.svg',
            'gaming-laptop-rtx4060': 'laptop.svg',
            'ps5-digital-edition': 'ps5d.svg',
            'xl-rgb-mousepad': 'mousepad.svg',
            'gaming-hoodie-elite': 'hoodie.svg',
            'streaming-webcam-1080p': 'webcam.svg',
            'gaming-mouse-rgb': 'mouse.svg',
            'mechanical-gaming-keyboard-tkl': 'keyboard.svg',
            'wireless-gaming-keyboard': 'keyboard.svg',
            'gaming-mousepad-xxl': 'mousepad.svg',
            'gaming-headset-wireless': 'headset.svg',
            'gaming-chair-racing': 'chair.svg',
            'gaming-monitor-144hz': 'monitor.svg',
            'gaming-controller-elite': 'controller.svg',
            'gaming-microphone-usb': 'webcam.svg',
            'gaming-desk-rgb': 'chair.svg',
            'gaming-capture-card-4k': 'pc.svg',
            'gaming-router-wifi6': 'cpu.svg',
        }
        for pdata in products_data:
            product = Product.query.filter_by(slug=pdata['slug']).first()
            if product:
                img_name = image_map.get(pdata['slug'], 'default_product.svg')
                img = ProductImage(
                    product_id=product.id,
                    image_url=f'/static/images/{img_name}',
                    alt_text=pdata['name'],
                    is_primary=True,
                    sort_order=1
                )
                db.session.add(img)
        db.session.flush()

        # === SERVICES ===
        print("ðŸ› ï¸  Creating services...")
        services_data = [
            {
                'name': 'PC Building Service',
                'slug': 'pc-building-service',
                'description': 'Professional custom PC building service. We assemble your dream gaming rig with expert cable management and testing.',
                'features': 'Expert Assembly, Cable Management, Stress Testing, BIOS Optimization, 30-Day Warranty',
                'fee': 75.00,
                'estimated_duration': '2-3 hours',
                'is_active': True,
                'sort_order': 1,
            },
            {
                'name': 'Console Repair',
                'slug': 'console-repair',
                'description': 'Professional repair service for PlayStation, Xbox, and Nintendo consoles. Hardware and software fixes.',
                'features': 'Diagnostic, Hardware Repair, Software Fix, Cleaning, Thermal Paste Replacement',
                'fee': 50.00,
                'estimated_duration': '1-3 days',
                'is_active': True,
                'sort_order': 2,
            },
            {
                'name': 'Software Installation',
                'slug': 'software-installation',
                'description': 'Complete software setup including OS installation, drivers, essential software, and security configuration.',
                'features': 'OS Installation, Driver Setup, Antivirus, Essential Apps, Performance Optimization',
                'fee': 30.00,
                'estimated_duration': '1-2 hours',
                'is_active': True,
                'sort_order': 3,
            },
            {
                'name': 'Network Setup & WiFi',
                'slug': 'network-setup',
                'description': 'Professional network and WiFi setup for optimal gaming performance. Includes router configuration and optimization.',
                'features': 'Router Setup, WiFi Optimization, Port Forwarding, QoS Configuration, Speed Testing',
                'fee': 40.00,
                'estimated_duration': '1-2 hours',
                'is_active': True,
                'sort_order': 4,
            },
            {
                'name': 'Hardware Upgrade',
                'slug': 'hardware-upgrade',
                'description': 'Upgrade your gaming PC with new components. GPU, RAM, SSD, CPU upgrades and installations.',
                'features': 'Component Installation, Compatibility Check, Driver Setup, Performance Testing',
                'fee': 35.00,
                'estimated_duration': '1-2 hours',
                'is_active': True,
                'sort_order': 5,
            },
            {
                'name': 'Data Recovery Service',
                'slug': 'data-recovery-service',
                'description': 'Professional data recovery from failed hard drives, SSDs, and storage devices.',
                'features': 'HDD Recovery, SSD Recovery, RAID Recovery, Logical Recovery, Free Diagnostic',
                'fee': 80.00,
                'estimated_duration': '2-5 days',
                'is_active': True,
                'sort_order': 6,
            },
            {
                'name': 'Virus & Malware Removal',
                'slug': 'virus-malware-removal',
                'description': 'Complete virus, malware, and ransomware removal with system cleanup and protection setup.',
                'features': 'Malware Scan, Ransomware Removal, System Cleanup, Antivirus Setup, Performance Tune',
                'fee': 45.00,
                'estimated_duration': '2-4 hours',
                'is_active': True,
                'sort_order': 7,
            },
            {
                'name': 'Custom Water Cooling Setup',
                'slug': 'custom-water-cooling',
                'description': 'Custom liquid cooling loop installation for maximum overclocking and silent operation.',
                'features': 'Custom Loop Design, Radiator Install, Pump Setup, Coolant Fill, Leak Testing',
                'fee': 150.00,
                'estimated_duration': '1-2 days',
                'is_active': True,
                'sort_order': 8,
            },
            {
                'name': 'Gaming Console Modding',
                'slug': 'console-modding',
                'description': 'Professional console modification services including storage upgrades and cooling improvements.',
                'features': 'Storage Upgrade, Cooling Mod, Shell Swap, LED Mod, Performance Tune',
                'fee': 60.00,
                'estimated_duration': '1-2 days',
                'is_active': True,
                'sort_order': 9,
            },
            {
                'name': 'Laptop Repair Service',
                'slug': 'laptop-repair',
                'description': 'Expert laptop repair including screen replacement, keyboard fix, and battery replacement.',
                'features': 'Screen Replacement, Keyboard Repair, Battery Swap, Hinge Fix, Thermal Repaste',
                'fee': 55.00,
                'estimated_duration': '1-3 days',
                'is_active': True,
                'sort_order': 10,
            },
            {
                'name': 'Game Controller Repair',
                'slug': 'controller-repair',
                'description': 'Repair services for gaming controllers including stick drift fix and button replacement.',
                'features': 'Stick Drift Fix, Button Replacement, Shell Repair, Trigger Fix, Recalibration',
                'fee': 25.00,
                'estimated_duration': '1-2 hours',
                'is_active': True,
                'sort_order': 11,
            },
            {
                'name': 'PC Optimization & Tuning',
                'slug': 'pc-optimization',
                'description': 'System optimization service to boost gaming performance with BIOS tuning and cleanup.',
                'features': 'BIOS Tuning, Startup Cleanup, Driver Update, Overclock Setup, Benchmark Test',
                'fee': 40.00,
                'estimated_duration': '1-2 hours',
                'is_active': True,
                'sort_order': 12,
            },
            {
                'name': 'RGB Lighting Installation',
                'slug': 'rgb-lighting-install',
                'description': 'Professional RGB lighting setup for your PC case, desk, and gaming setup.',
                'features': 'Case Lighting, Strip Installation, Sync Setup, Controller Config, Cable Management',
                'fee': 35.00,
                'estimated_duration': '1-2 hours',
                'is_active': True,
                'sort_order': 13,
            },
        ]

        for sdata in services_data:
            service = Service(**sdata)
            db.session.add(service)
        db.session.flush()

        # === ANNOUNCEMENTS ===
        print("ðŸ“¢ Creating announcements...")
        ann1 = Announcement(title='Summer Sale is LIVE!', content='Get up to 30% off on all gaming accessories! Limited time offer. Use code SUMMER30 at checkout.', announcement_type='promo', is_active=True, is_pinned=True, target_audience='all', created_by=admin.id)
        ann2 = Announcement(title='New PS5 Stock Available', content='Fresh batch of PlayStation 5 consoles just arrived! Order now before they sell out.', announcement_type='info', is_active=True, is_pinned=False, target_audience='all', created_by=admin.id)
        ann3 = Announcement(title='Maintenance Notice', content='Our website will be undergoing maintenance on Sunday from 2 AM to 6 AM. We apologize for any inconvenience.', announcement_type='info', is_active=True, is_pinned=False, target_audience='all', created_by=admin.id)
        db.session.add_all([ann1, ann2, ann3])
        db.session.flush()

        # === BANNERS ===
        print("ðŸ–¼ï¸  Creating banners...")
        banner1 = Banner(title='Level Up Your Game', description='Discover the latest gaming gear and accessories', button_text='Shop Now', button_url='/products', position='hero', is_active=True, sort_order=1)
        banner2 = Banner(title='Expert Repair Services', description='Professional PC and console repair services', button_text='Book Now', button_url='/services', position='home', is_active=True, sort_order=2)
        db.session.add_all([banner1, banner2])
        db.session.flush()

        # === PAYMENT SETTINGS ===
        print("ðŸ’³ Creating payment settings...")
        ps = PaymentSettings(
            bank_name='Habib Bank Limited (HBL)',
            account_title='GameZone Hub Store',
            account_number='1234-5678-9012-3456',
            iban='PK09SCBL0000001234567890',
            mobile_wallet_name='JazzCash',
            mobile_wallet_number='+92-300-1234567',
            instructions='''Step 1: Transfer the exact amount to the account below.
Step 2: Take a screenshot of the payment confirmation.
Step 3: Upload the screenshot in the order payment section.
Step 4: Wait for admin verification (usually within 24 hours).

Bank Transfer:
Bank: HBL
Account Title: GameZone Hub Store
Account Number: 1234-5678-9012-3456
IBAN: PK09SCBL0000001234567890

JazzCash:
Number: +92-300-1234567'''
        )
        db.session.add(ps)

        # === SAMPLE ORDERS ===
        print("ðŸ“‹ Creating sample orders...")
        from app.utils.helpers import generate_order_number

        order1 = Order(
            order_number=generate_order_number(),
            user_id=customer1.id,
            subtotal=449.99,
            total=449.99,
            payment_method='online',
            payment_status='WAITING_FOR_VERIFICATION',
            status='PENDING'
        )
        db.session.add(order1)
        db.session.flush()

        oi1 = OrderItem(order_id=order1.id, product_id=1, product_name='PlayStation 5 Console', product_price=449.99, quantity=1, subtotal=449.99)
        db.session.add(oi1)

        bill1 = BillingDetail(
            order_id=order1.id,
            full_name=customer1.full_name,
            email=customer1.email,
            phone=customer1.phone,
            address='123 Gaming Street',
            city='Lahore',
            postal_code='54000'
        )
        db.session.add(bill1)

        order2 = Order(
            order_number=generate_order_number(),
            user_id=customer2.id,
            subtotal=839.98,
            total=839.98,
            payment_method='cod',
            payment_status='PENDING',
            status='CONFIRMED'
        )
        db.session.add(order2)
        db.session.flush()

        oi2a = OrderItem(order_id=order2.id, product_id=4, product_name='RTX 4070 Ti Graphics Card', product_price=749.99, quantity=1, subtotal=749.99)
        oi2b = OrderItem(order_id=order2.id, product_id=6, product_name='Wireless Gaming Mouse', product_price=89.99, quantity=1, subtotal=89.99)
        db.session.add_all([oi2a, oi2b])

        bill2 = BillingDetail(
            order_id=order2.id,
            full_name=customer2.full_name,
            email=customer2.email,
            phone=customer2.phone,
            address='456 Esports Avenue',
            city='Karachi',
            postal_code='75500'
        )
        db.session.add(bill2)

        order3 = Order(
            order_number=generate_order_number(),
            user_id=customer3.id,
            subtotal=119.99,
            total=119.99,
            payment_method='online',
            payment_status='VERIFIED',
            status='DELIVERED'
        )
        db.session.add(order3)
        db.session.flush()

        oi3 = OrderItem(order_id=order3.id, product_id=7, product_name='Gaming Headset 7.1 Surround', product_price=119.99, quantity=1, subtotal=119.99)
        db.session.add(oi3)

        bill3 = BillingDetail(
            order_id=order3.id,
            full_name=customer3.full_name,
            email=customer3.email,
            phone=customer3.phone,
            address='789 Pro Street',
            city='Islamabad',
            postal_code='44000'
        )
        db.session.add(bill3)

        # === SAMPLE REVIEWS ===
        print("â­ Creating sample reviews...")
        r1 = Review(user_id=customer3.id, product_id=7, rating=5, comment='Amazing headset! The 7.1 surround sound is incredible for gaming. Very comfortable for long sessions.', is_approved=True)
        r2 = Review(user_id=customer1.id, product_id=1, rating=4, comment='Great console, fast loading times. Would be 5 stars if it had more storage.', is_approved=True)
        db.session.add_all([r1, r2])

        db.session.commit()
        print("\nâœ… Database seeded successfully!")
        print("\nðŸ“‹ Login Credentials:")
        print("   Admin:     admin@gamezone.com / admin123")
        print("   Staff:     staff@gamezone.com / staff123")
        print("   Technician: tech@gamezone.com / tech123")
        print("   Customer:  gamer1@example.com / customer123")
        print("   Customer:  gamer2@example.com / customer123")
        print("   Customer:  gamer3@example.com / customer123")


if __name__ == '__main__':
    seed_database()
