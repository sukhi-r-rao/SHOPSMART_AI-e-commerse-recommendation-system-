import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from database import get_db_connection

try:
    conn = get_db_connection()

    if conn.is_connected():
        print("Database Connected Successfully")

    conn.close()

except Exception as e:
    print("Error:", e)