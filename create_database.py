# create_database.py
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from decouple import config

# Configuración
db_name = config('DB_NAME', default='esenciakr_db')
db_user = config('DB_USER', default='postgres')
db_password = config('DB_PASSWORD')
db_host = config('DB_HOST', default='localhost')
db_port = config('DB_PORT', default='5432')

try:
    # Conectar a PostgreSQL (base de datos postgres por defecto)
    conn = psycopg2.connect(
        dbname='postgres',
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Verificar si la base de datos ya existe
    cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
    exists = cursor.fetchone()
    
    if not exists:
        # Crear la base de datos
        cursor.execute(f'CREATE DATABASE {db_name} ENCODING "UTF8"')
        print(f"✅ Base de datos '{db_name}' creada exitosamente!")
    else:
        print(f"⚠️  La base de datos '{db_name}' ya existe.")
    
    cursor.close()
    conn.close()
    
    print(f"\n📊 Información de conexión:")
    print(f"   Host: {db_host}")
    print(f"   Puerto: {db_port}")
    print(f"   Base de datos: {db_name}")
    print(f"   Usuario: {db_user}")
    
except Exception as e:
    print(f"❌ Error al crear la base de datos: {e}")
    print(f"\n💡 Verifica:")
    print(f"   1. PostgreSQL está corriendo")
    print(f"   2. La contraseña en el archivo .env es correcta")
    print(f"   3. El puerto {db_port} es el correcto")

    