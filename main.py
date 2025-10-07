import sqlite3
import datetime

DB_NAME = 'cit_gate_log.db'

def setup_database():
    """Initializes the database and creates tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        roll_no TEXT PRIMARY KEY, name TEXT NOT NULL, phone_no TEXT
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gate_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT, roll_no TEXT NOT NULL,
        name TEXT NOT NULL, status TEXT NOT NULL, timestamp TEXT NOT NULL,
        FOREIGN KEY (roll_no) REFERENCES students (roll_no)
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS outing_permissions (
        permission_id INTEGER PRIMARY KEY AUTOINCREMENT, roll_no TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'PENDING', request_timestamp TEXT NOT NULL,
        FOREIGN KEY (roll_no) REFERENCES students (roll_no)
    )''')
    students_to_add = [
        ('2403717624321055', 'Thirumaran S L', '9363915238'),
        ('2403717624322024', 'Kiruthika K', '7200239667'),
        ('2403717624321007','Bala Dharunesh','7458961245'),
        ('2403717624322008', 'Bharathy K','945187452'),
        ('2403717624321033', 'Nirmal Raj','7272239426')
    ]
    cursor.executemany('INSERT OR IGNORE INTO students (roll_no, name, phone_no) VALUES (?, ?, ?)', students_to_add)
    conn.commit()
    conn.close()
    print("Database setup complete. System is ready.")

# --- NEW DIAGNOSTIC FUNCTION ---
def check_status(roll_no):
    """Prints the current status and all permissions for a student."""
    print(f"\n🔎 Checking status for Roll No: {roll_no}...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Check last movement
    cursor.execute("SELECT status, timestamp FROM gate_logs WHERE roll_no = ? ORDER BY timestamp DESC LIMIT 1", (roll_no,))
    last_log = cursor.fetchone()
    if last_log:
        print(f"   Last known status: '{last_log[0]}' at {last_log[1]}")
    else:
        print("   Last known status: 'IN' (No logs found)")
        
    # Check permissions
    cursor.execute("SELECT permission_id, status, request_timestamp FROM outing_permissions WHERE roll_no = ?", (roll_no,))
    permissions = cursor.fetchall()
    if permissions:
        print("   Current Permissions:")
        for p in permissions:
            print(f"     - ID: {p[0]}, Status: '{p[1]}', Requested at: {p[2]}")
    else:
        print("   Current Permissions: None")
    
    conn.close()
    print("-" * 40)

def request_permission(roll_no):
    """Simulates a student requesting an outing permission."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        "INSERT INTO outing_permissions (roll_no, request_timestamp) VALUES (?, ?)",
        (roll_no, timestamp)
    )
    conn.commit()
    conn.close()
    print(f"✅ Permission requested for Roll No: {roll_no}. Status: PENDING.")

def approve_permission(roll_no):
    """Simulates a warden approving the latest pending request for a student."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT permission_id FROM outing_permissions WHERE roll_no = ? AND status = 'PENDING' ORDER BY request_timestamp DESC LIMIT 1",
        (roll_no,)
    )
    permission_to_approve = cursor.fetchone()
    if permission_to_approve:
        permission_id = permission_to_approve[0]
        cursor.execute("UPDATE outing_permissions SET status = 'APPROVED' WHERE permission_id = ?", (permission_id,))
        print(f"✅ Permission ID {permission_id} has been APPROVED for Roll No: {roll_no}.")
    else:
        print(f"⚠️ No pending permission found to approve for Roll No: {roll_no}.")
    conn.commit()
    conn.close()

def get_last_status(roll_no):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM gate_logs WHERE roll_no = ? ORDER BY timestamp DESC LIMIT 1", (roll_no,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'IN'

def log_student_movement(roll_no):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM students WHERE roll_no = ?", (roll_no,))
    student = cursor.fetchone()
    if not student:
        print(f"--- ALERT: Invalid ID card. Roll No: {roll_no} not found. ---")
        conn.close()
        return

    student_name = student[0]
    last_status = get_last_status(roll_no)
    new_status = 'OUT' if last_status == 'IN' else 'IN'

    if new_status == 'OUT':
        print(f"➡️  Student {student_name} is trying to exit. Checking for permission...")
        cursor.execute("SELECT permission_id FROM outing_permissions WHERE roll_no = ? AND status = 'APPROVED'", (roll_no,))
        permission = cursor.fetchone()
        if not permission:
            print(f"❌ EXIT DENIED for {student_name}. Reason: No approved permission found.")
            conn.close()
            return
        else:
            permission_id = permission[0]
            print(f"🔑 Permission ID {permission_id} verified. Deleting permission to prevent reuse.")
            cursor.execute("DELETE FROM outing_permissions WHERE permission_id = ?", (permission_id,))
    
    current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        "INSERT INTO gate_logs (roll_no, name, status, timestamp) VALUES (?, ?, ?, ?)",
        (roll_no, student_name, new_status, current_timestamp)
    )
    print(f"\n✅ Scan Successful!")
    print(f"   Name: {student_name} | Status: {new_status} | Timestamp: {current_timestamp}")
    print("-" * 60)
    conn.commit()
    conn.close()
def view_database():
    """Displays all records from students, gate_logs, and outing_permissions tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print("\n--- Students Table ---")
    for row in cursor.execute("SELECT * FROM students"):
        print(row)

    print("\n--- Gate Logs Table ---")
    for row in cursor.execute("SELECT * FROM gate_logs"):
        print(row)

    print("\n--- Outing Permissions Table ---")
    for row in cursor.execute("SELECT * FROM outing_permissions"):
        print(row)

    conn.close()
    print("-" * 40)

def main():
    """Main function to run the gate pass system."""
    setup_database()
    print("\n--- CIT Smart Gate Pass System ---")
    print("Commands:")
    print("  'request <roll_no>' - Student requests permission")
    print("  'approve <roll_no>' - Warden approves permission")
    print("  'status <roll_no>'  - Check student's current status")
    print("  'viewdb'            - View all database tables")
    print("  '<roll_no>'         - Student scans ID at the gate")
    print("  'exit'              - Close the system\n")

    while True:
        user_input = input("Enter command or Scan ID: ").strip()
        
        # --- ROBUST FIX: IGNORE ANY EXECUTION COMMAND ---
        # This more general check works for main.py, tempCodeRunnerFile.py, etc.
        if '.py' in user_input and 'python' in user_input:
            continue # Skips the rest of the loop and asks for input again

        parts = user_input.split()
        if not parts: continue
        command = parts[0].lower()

        if command == 'exit':
            print("Shutting down system."); break
        if command == 'viewdb':
            view_database()
        elif command in ['request', 'approve', 'status'] and len(parts) == 2:
            roll_no = parts[1]
            if command == 'request': request_permission(roll_no)
            elif command == 'approve': approve_permission(roll_no)
            elif command == 'status': check_status(roll_no)
        elif len(parts) == 1:
            log_student_movement(command)
        else:
            print("Invalid input format. Please try again.")

if __name__ == "__main__":
    main()