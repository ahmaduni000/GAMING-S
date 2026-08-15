import os

admin_dir = 'gaming_store/app/templates/admin'
files = [f for f in os.listdir(admin_dir) if f.endswith('.html')]
print('Total templates:', len(files))
for f in sorted(files):
    path = os.path.join(admin_dir, f)
    with open(path) as fh:
        content = fh.read()
    has_wrapper = 'col-lg-3 admin-sidebar' in content
    print(f'{f}: {"HAS wrapper" if has_wrapper else "NO wrapper"}')