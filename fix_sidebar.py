import os

files = [
    'verify_payment.html',
    'technician_form.html',
    'staff_form.html',
    'service_form.html',
    'product_form.html',
    'order_detail.html',
    'category_form.html',
    'banner_form.html',
    'banners.html',
    'appointment_detail.html',
    'appointments.html',
    'announcement_form.html',
]

base_dir = os.path.join(os.path.dirname(__file__), 'gaming_store', 'app', 'templates', 'admin')

for fname in files:
    path = os.path.join(base_dir, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old = "        {% include 'admin/sidebar.html' %}\n"
    new = "        <div class=\"col-lg-3 admin-sidebar\">\n            {% include 'admin/sidebar.html' %}\n        </div>\n"
    
    if old in content:
        content = content.replace(old, new, 1)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"FIXED: {fname}")
    else:
        print(f"SKIP (pattern not found): {fname}")