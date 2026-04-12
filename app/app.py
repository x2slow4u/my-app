from flask import Flask
import os
import psycopg2
import redis
app = Flask(__name__)


# Подключение к Redis
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'postgres'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password')
    )
@app.route('/')
def hello():
    # Проверяем кэш
    cache_key = 'hello_message'
    cached = redis_client.get(cache_key)

    if cached:
        return f"{cached} (from cache)"

    # Если нет в кэше — создаем и сохраняем
    message = f"Hello from my-app! Environment: {os.getenv('ENV', 'development')}"
    redis_client.setex(cache_key, 30, message)  # кэш на 30 секунд
    return f"{message} (fresh)"


@app.route('/health')
def health():
    return "OK"

@app.route('/db')
def db_test():
    try:
        conn = get_db_connection()
        conn.close()
        return "Database connection OK"
    except Exception as e:
        return f"Database connection FAILED: {e}"

@app.route('/redis')
def redis_test():
    """Проверка подключения к Redis"""
    try:
        redis_client.set('test_key', 'test_value')
        value = redis_client.get('test_key')
        return f"Redis connection OK. Test value: {value}"
    except Exception as e:
        return f"Redis connection FAILED: {e}"

@app.route('/stats')
def stats():
    """Статистика Redis"""
    try:
        info = redis_client.info('stats')
        return jsonify({
            'total_commands_processed': info['total_commands_processed'],
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0)
        })
    except Exception as e:
        return f"Stats error: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)