import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def migrate():
    # Try PostgreSQL first (same logic as database.py)
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:myskin123@localhost:5432/myskin')
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            print(f"Connecting to PostgreSQL: {db_url}")
            # Add columns to users table
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
                print("Added column password_hash to users")
            except Exception as e:
                print(f"Column password_hash might already exist: {e}")
            
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN gender VARCHAR(20)"))
                print("Added column gender to users")
            except Exception as e:
                print(f"Column gender might already exist: {e}")

            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP"))
                print("Added column last_login_at to users")
            except Exception as e:
                print(f"Column last_login_at might already exist: {e}")
            
            conn.commit()
    except Exception as e:
        print(f"PostgreSQL migration failed or not used: {e}")
        
    # Also try SQLite just in case
    sqlite_url = "sqlite:///./myskin.db"
    if os.path.exists("./myskin.db"):
        try:
            engine = create_engine(sqlite_url)
            with engine.connect() as conn:
                print(f"Connecting to SQLite: {sqlite_url}")
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
                    print("Added column password_hash to SQLite users")
                except Exception as e:
                    print(f"SQLite password_hash error: {e}")

                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN gender VARCHAR(20)"))
                    print("Added column gender to SQLite users")
                except Exception as e:
                    print(f"SQLite gender error: {e}")

                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN last_login_at DATETIME"))
                    print("Added column last_login_at to SQLite users")
                except Exception as e:
                    print(f"SQLite last_login_at error: {e}")
                
                conn.commit()
        except Exception as e:
            print(f"SQLite migration failed: {e}")

if __name__ == "__main__":
    migrate()
    print("Migration finished.")
