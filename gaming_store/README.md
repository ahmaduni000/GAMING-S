# 🎮 GameZone Hub - Gaming Store Management System

A complete full-stack Flask application for managing a gaming store with e-commerce, service booking, and multi-role administration.

## 🚀 Features

### Main Website
- **Home Page** — Hero section, featured products, latest arrivals, bestsellers, services
- **Product Store** — Browse, search, filter, and sort gaming products
- **Service Booking** — Book gaming services with technician selection
- **About & Contact** — Company info and contact form

### E-Commerce
- Shopping cart with quantity management
- Wishlist functionality
- Checkout with billing details
- **Payment Methods:** Cash on Delivery (COD) or Online Payment
- Online payment with screenshot verification workflow
- Order tracking with status timeline

### Customer Panel
- Dashboard with order/appointment stats
- Order history with detailed tracking
- Appointment management
- Wishlist and reviews
- Notifications

### Staff Panel
- Dashboard with assigned orders/appointments
- Order status management
- Appointment status and technician assignment

### Admin Panel
- **Dashboard** — Revenue charts, stats, recent orders
- **Customer Management** — View, activate/deactivate, delete
- **Product Management** — Full CRUD with images, categories, stock
- **Category Management** — Hierarchical categories
- **Order Management** — Status updates, history tracking
- **Payment Verification** — Review payment screenshots, approve/reject
- **Service Management** — CRUD for gaming services
- **Appointment Management** — Status updates, technician assignment
- **Technician Management** — Add/edit technicians with skills
- **Staff Management** — Add staff members
- **Review Moderation** — Approve/delete product reviews
- **Contact Messages** — View and mark as read
- **Announcements** — Create/manage announcements
- **Banner Management** — Hero and home page banners
- **Payment Settings** — Bank/wallet details for customers

## 🛠️ Tech Stack

- **Backend:** Python Flask 3.0
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Authentication:** Flask-Login with RBAC
- **Forms:** Flask-WTF with CSRF protection
- **Frontend:** Bootstrap 5, Font Awesome 6, Chart.js
- **Fonts:** Google Fonts (Inter + Orbitron)

## 📁 Project Structure

```
gaming_store/
├── app/
│   ├── __init__.py          # App factory
│   ├── models/              # SQLAlchemy models (8 files)
│   │   ├── user.py          # User, Role, Technician, ActivityLog
│   │   ├── product.py       # Category, Product, ProductImage
│   │   ├── cart.py          # Cart, Wishlist
│   │   ├── order.py         # Order, Payment, PaymentProof
│   │   ├── service.py       # Service, ServiceBooking
│   │   ├── review.py        # Review
│   │   ├── communication.py # Notification, Announcement, Banner
│   │   └── settings.py      # SiteSettings, PaymentSettings
│   ├── routes/              # Blueprint routes (10 files)
│   │   ├── main.py          # Home, About, Contact
│   │   ├── auth.py          # Login, Register, Profile
│   │   ├── products.py      # Product listing, Cart, Checkout
│   │   ├── services.py      # Service listing, Booking
│   │   ├── customer.py      # Customer panel
│   │   ├── staff.py         # Staff panel
│   │   ├── admin.py         # Admin panel (full CRUD)
│   │   ├── errors.py        # Error handlers
│   │   └── api.py           # JSON APIs
│   ├── forms/               # WTForms (17 form classes)
│   ├── utils/               # Helpers, decorators, file upload
│   ├── templates/           # Jinja2 templates (50+ files)
│   │   ├── base.html
│   │   ├── partials/        # Navbar, Footer
│   │   ├── main/            # Public pages
│   │   ├── auth/            # Login, Register, Profile
│   │   ├── customer/        # Customer panel
│   │   ├── staff/           # Staff panel
│   │   ├── admin/           # Admin panel (26 templates)
│   │   └── errors/          # 404, 403, 500
│   └── static/
│       ├── css/style.css    # Custom gaming-themed CSS
│       └── js/main.js       # Frontend JavaScript
├── config.py                # Configuration classes
├── run.py                   # Entry point
├── seed.py                  # Database seeder
├── requirements.txt         # Python dependencies
└── .env.example             # Environment variables template
```

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.9+
- PostgreSQL
- pip

### Installation

1. **Clone the repository:**
   ```bash
   cd gaming_store
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   copy .env.example .env
   ```
   Edit `.env` with your PostgreSQL credentials and settings.

5. **Initialize database:**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Seed database (optional):**
   ```bash
   python seed.py
   ```

7. **Run the application:**
   ```bash
   python run.py
   ```

8. **Open in browser:**
   ```
   http://127.0.0.1:5000
   ```

## 👤 Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@gamezone.com | admin123 |
| Staff | staff@gamezone.com | staff123 |
| Technician | tech@gamezone.com | tech123 |
| Customer | gamer1@example.com | customer123 |

## 📋 Order Workflow

```
PENDING → CONFIRMED → PROCESSING → PACKED → SHIPPED → OUT FOR DELIVERY → DELIVERED
```

## 🔧 Service Booking Workflow

```
PENDING → CONFIRMED → ASSIGNED → PROCESSING → READY → COMPLETED
```

## 💳 Payment Flow

1. Customer places order with **COD** or **Online Payment**
2. For online payment, customer uploads payment screenshot
3. Admin reviews and verifies/rejects the payment
4. Customer receives notification of verification status

## 📄 License

This project is for educational purposes.
