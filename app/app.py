from flask import Flask
import os
import psycopg2

app = Flask(__name__)

@app.route('/')
def hello():
    return f"Hello from my-app! Environment: {os.getenv('ENV', 'development')}"

@app.route('/health')
def health():
    return "OK"

@app.route('/db')
def db_test():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'postgres'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'password')
        )
        conn.close()
        return "Database connection OK"
    except Exception as e:
        return f"Database connection FAILED: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)