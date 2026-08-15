from app import create_app, db
from app.models import User, Role, Category, Product, Order, Service

app = create_app('default')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Category=Category, Product=Product, Order=Order, Service=Service)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
