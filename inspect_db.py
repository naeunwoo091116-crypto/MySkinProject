from sqlalchemy import create_engine, inspect
import os

def check_columns():
    db_url = 'postgresql://postgres:myskin123@localhost:5432/myskin'
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            inspector = inspect(engine)
            columns = inspector.get_columns('users')
            print("Columns in 'users' table:")
            col_names = [c['name'] for c in columns]
            for col in col_names:
                print(f"- {col}")
            
            if 'password_hash' in col_names:
                print("\nSUCCESS: password_hash exists.")
            else:
                print("\nFAILURE: password_hash MISSING.")

    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_columns()
