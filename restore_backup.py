"""
Restore database from backup
This script safely restores user data from the backup database
"""
import os
import sys
import sqlite3
import shutil
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BACKUP_DB = r"zzDumpfiles\SQLite Database Backup\users.db"
CURRENT_DB = r"instance\users.db"

def backup_current_db():
    """Backup the current database before restoration"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"instance/users.db.before_restore_{timestamp}"
    shutil.copy2(CURRENT_DB, backup_path)
    print(f"✓ Current database backed up to: {backup_path}")
    return backup_path

def restore_data():
    """Restore data from backup database"""

    # Check if backup exists
    if not os.path.exists(BACKUP_DB):
        print(f"✗ Backup database not found at: {BACKUP_DB}")
        return False

    print(f"Starting restoration from backup: {BACKUP_DB}")
    print(f"Target database: {CURRENT_DB}")

    # Backup current database first
    backup_current_db()

    # Connect to both databases
    backup_conn = sqlite3.connect(BACKUP_DB)
    current_conn = sqlite3.connect(CURRENT_DB)

    backup_cursor = backup_conn.cursor()
    current_cursor = current_conn.cursor()

    try:
        # 1. Restore Users
        print("\n[1/4] Restoring users...")
        backup_cursor.execute("SELECT * FROM users")
        users = backup_cursor.fetchall()

        # Get column names from backup
        backup_cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in backup_cursor.fetchall()]

        # Find indices for fname, lname, and name
        fname_idx = columns.index('fname')
        lname_idx = columns.index('lname')
        name_idx = columns.index('name')

        placeholders = ','.join(['?'] * len(columns))
        column_names = ','.join(columns)

        for user in users:
            # Convert to list so we can modify it
            user_list = list(user)

            # If name is NULL or empty, compute it from fname and lname
            if not user_list[name_idx]:
                user_list[name_idx] = f"{user_list[fname_idx]} {user_list[lname_idx]}"

            current_cursor.execute(f"INSERT OR REPLACE INTO users ({column_names}) VALUES ({placeholders})", user_list)

        print(f"  ✓ Restored {len(users)} users")

        # 2. Restore Admins (now using Single Table Inheritance)
        print("\n[2/4] Restoring admin references...")
        # In new schema, admins table only has id, not user_id
        # Admins are identified by role='admin' in users table, which was already restored
        # We need to create admin table entries matching user IDs where role='admin'

        current_cursor.execute("SELECT id FROM users WHERE role IN ('admin', 'super_admin')")
        admin_user_ids = [row[0] for row in current_cursor.fetchall()]

        for user_id in admin_user_ids:
            # Check if this is admin or super_admin
            current_cursor.execute("SELECT role FROM users WHERE id=?", (user_id,))
            role = current_cursor.fetchone()[0]

            if role == 'admin':
                # Insert into admins table (only id field exists now)
                current_cursor.execute("INSERT OR IGNORE INTO admins (id) VALUES (?)", (user_id,))
            elif role == 'super_admin':
                # Insert into both admins and super_admins
                current_cursor.execute("INSERT OR IGNORE INTO admins (id) VALUES (?)", (user_id,))
                current_cursor.execute("INSERT OR IGNORE INTO super_admins (id) VALUES (?)", (user_id,))

        print(f"  ✓ Created {len(admin_user_ids)} admin/super_admin table entries")

        # 3. No separate super admin restoration needed (handled above)

        # 4. Restore Tool Access (only if tool exists)
        print("\n[4/4] Restoring tool access...")

        # Get valid tool names from current DB
        current_cursor.execute("SELECT name FROM tools")
        valid_tools = {row[0] for row in current_cursor.fetchall()}

        backup_cursor.execute("SELECT user_id, tool_name FROM tool_access")
        tool_accesses = backup_cursor.fetchall()

        restored = 0
        skipped = 0

        for user_id, tool_name in tool_accesses:
            if tool_name in valid_tools:
                current_cursor.execute("INSERT OR REPLACE INTO tool_access (user_id, tool_name) VALUES (?, ?)",
                                     (user_id, tool_name))
                restored += 1
            else:
                skipped += 1

        print(f"  ✓ Restored {restored} tool access records")
        if skipped > 0:
            print(f"  ⚠ Skipped {skipped} records for deprecated tools")

        # 5. Restore Email Templates
        print("\n[5/5] Restoring email templates...")
        backup_cursor.execute("SELECT * FROM email_templates")
        templates = backup_cursor.fetchall()

        if templates:
            # Get column names from both databases
            backup_cursor.execute("PRAGMA table_info(email_templates)")
            backup_columns = [col[1] for col in backup_cursor.fetchall()]

            current_cursor.execute("PRAGMA table_info(email_templates)")
            current_columns = [col[1] for col in current_cursor.fetchall()]

            # Find common columns
            common_columns = [col for col in backup_columns if col in current_columns]

            # Get indices of common columns in backup
            backup_indices = [backup_columns.index(col) for col in common_columns]

            placeholders = ','.join(['?'] * len(common_columns))
            column_names = ','.join(common_columns)

            for template in templates:
                # Extract only the columns that exist in both schemas
                values = [template[idx] for idx in backup_indices]
                current_cursor.execute(f"INSERT OR REPLACE INTO email_templates ({column_names}) VALUES ({placeholders})", values)

            print(f"  ✓ Restored {len(templates)} email templates")
        else:
            print("  ℹ No email templates to restore")

        # Commit all changes
        current_conn.commit()

        print("\n" + "="*60)
        print("✓ RESTORATION COMPLETED SUCCESSFULLY!")
        print("="*60)

        # Show final counts
        current_cursor.execute("SELECT COUNT(*) FROM users")
        user_count = current_cursor.fetchone()[0]

        current_cursor.execute("SELECT COUNT(*) FROM tool_access")
        access_count = current_cursor.fetchone()[0]

        current_cursor.execute("SELECT COUNT(*) FROM email_templates")
        template_count = current_cursor.fetchone()[0]

        print(f"\nFinal database state:")
        print(f"  Users: {user_count}")
        print(f"  Tool Access: {access_count}")
        print(f"  Email Templates: {template_count}")

        return True

    except Exception as e:
        print(f"\n✗ Error during restoration: {e}")
        current_conn.rollback()
        return False

    finally:
        backup_conn.close()
        current_conn.close()

if __name__ == "__main__":
    print("="*60)
    print("DATABASE RESTORATION UTILITY")
    print("="*60)

    restore_data()
