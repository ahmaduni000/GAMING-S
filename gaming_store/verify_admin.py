import sys, re
sys.path.insert(0, '.')
from app import create_app

app = create_app()
c = app.test_client()

def login(email, pw):
    c.get('/auth/logout')
    r = c.get('/auth/login')
    csrf = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', r.get_data(as_text=True)).group(1)
    return c.post('/auth/login', data={'email': email, 'password': pw, 'csrf_token': csrf}, follow_redirects=False)

def check(label, url, email, pw):
    login(email, pw)
    r = c.get(url)
    print(f'{label:35s} -> {r.status_code}')

check('admin dashboard', '/admin/dashboard', 'admin@gamezone.com', 'admin123')
check('admin orders', '/admin/orders', 'admin@gamezone.com', 'admin123')
check('admin appointments', '/admin/appointments', 'admin@gamezone.com', 'admin123')
check('admin reviews', '/admin/reviews', 'admin@gamezone.com', 'admin123')
check('admin payments', '/admin/payments', 'admin@gamezone.com', 'admin123')
check('admin customer_detail', '/admin/customers/1', 'admin@gamezone.com', 'admin123')
check('admin order_detail', '/admin/orders/1', 'admin@gamezone.com', 'admin123')
check('staff dashboard', '/staff/dashboard', 'staff@gamezone.com', 'staff123')
check('staff orders', '/staff/orders', 'staff@gamezone.com', 'staff123')
check('staff appointments', '/staff/appointments', 'staff@gamezone.com', 'staff123')
check('staff order_detail', '/staff/orders/1', 'staff@gamezone.com', 'staff123')
