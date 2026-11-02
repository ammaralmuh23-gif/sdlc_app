"""
wsgi.py — نقطة تشغيل SDLC Manager على Render
"""
import os
import sys

# إضافة مسار المشروع إلى النظام
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# استيراد التطبيق من app.py
from app import create_app

# إنشاء نسخة التطبيق
application = create_app()

# إنشاء الجداول تلقائياً إذا لم تكن موجودة (لـ SQLite)
try:
    import sqlite3
    db_path = os.path.join(path, 'sdlc_manager.db')
    sql_path = os.path.join(path, 'database.sql')
    
    if not os.path.exists(db_path) and os.path.exists(sql_path):
        conn = sqlite3.connect(db_path)
        with open(sql_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        print("✅ Tables created successfully")
    else:
        print("✅ Database already exists or SQL file not found")
except Exception as e:
    print(f"⚠️ Error creating tables: {e}")
