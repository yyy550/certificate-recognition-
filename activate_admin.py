#!/usr/bin/env python3
"""
激活管理员账号
"""

import sqlite3
import datetime

def activate_admin_account():
    """激活管理员账号"""
    conn = sqlite3.connect('certificate_system.db')
    cursor = conn.cursor()
    
    try:
        # 管理员账号
        admin_account_id = "admin"
        
        # 更新管理员账号状态和创建时间
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        cursor.execute("""
            UPDATE users 
            SET is_active = ?, created_at = ? 
            WHERE account_id = ?
        """, (1, current_time, admin_account_id))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            print("管理员账号已激活")
        else:
            print("管理员账号不存在")
            
    except Exception as e:
        print(f"激活管理员账号失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    activate_admin_account()
