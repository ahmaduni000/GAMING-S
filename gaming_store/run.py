from app import create_app, db
from app.models import User, Role, Category, Product, Order, Service

app = create_app('default')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Category=Category, Product=Product, Order=Order, Service=Service)


def migrate_columns():
    """Add any columns present on models but missing from existing tables.

    db.create_all() only creates new tables; it does not alter existing ones.
    This keeps an existing SQLite database in sync with model changes.
    """
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    with app.app_context():
        for table in db.metadata.tables.values():
            if not inspector.has_table(table.name):
                continue
            existing = {c['name'] for c in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name not in existing:
                    col_type = column.type.compile(db.engine.dialect)
                    db.engine.execute(
                        f'ALTER TABLE {table.name} ADD COLUMN {column.name} {col_type}'
                    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        migrate_columns()
    app.run(debug=True, host='0.0.0.0', port=5000)
