# run.py

from app import create_app, db
import sqlite3

app = create_app()

def init_db():
    with app.app_context():
        with open('setup.sql', 'r') as f:
            sql_script = f.read()
        # Connect to SQLite database
        conn = sqlite3.connect('dothucong.db')
        cursor = conn.cursor()
        cursor.executescript(sql_script)  # Execute the SQL script
        conn.commit()
        conn.close()

if __name__ == '__main__':
    #init_db()  # Initialize the database
    app.run(debug=True)