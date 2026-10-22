from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    # 1. Show what file SQLAlchemy is actually using
    print("Engine URL:", db.engine.url)

    # 2. Ask SQLAlchemy what tables it sees
    insp = db.inspect(db.engine)
    print("Tables via SQLAlchemy:", insp.get_table_names())

    # 3. Try a raw connection through SQLAlchemy’s engine
    with db.engine.connect() as conn:
        rows = conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        print("Tables via exec_driver_sql:")
        for (name,) in rows:
            print("-", name)
