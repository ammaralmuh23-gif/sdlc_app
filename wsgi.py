import os
import sys
import sqlite3

path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

from app import create_app

application = create_app()

# إنشاء الجداول إذا لم تكن موجودة
db_path = os.path.join(path, 'sdlc_manager.db')
sql_path = os.path.join(path, 'database.sql')

if not os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.executescript(open(sql_path, 'r', encoding='utf-8').read())
    conn.commit()
    conn.close()
    print("✅ Tables created")
# إضافة عمود كلمة المرور العادية وتحديث جدول المستخدمين
try:
    from models.db import execute_query
    execute_query("ALTER TABLE users ADD COLUMN plain_password TEXT")
    print("✅ Added plain_password column")
except Exception:
    pass
