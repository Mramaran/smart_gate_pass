import sqlite3
import datetime

# --- DATABASE SETUP ---
# Corresponds to the "Local Database & Storage" module
DB_NAME = 'cit_gate_log.db'

def setup_database():
    """Initializes the database and creates tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create a table for student details
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        roll_no TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        phone_no TEXT
    )''')

    # Create the main log table for entry/exit records
    # This schema correctly includes the 'status' column. Deleting the old .db file
    # ensures this new, correct table is created.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gate_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT NOT NULL,
        name TEXT NOT NULL,
        status TEXT NOT NULL, -- 'IN' or 'OUT'
        timestamp TEXT NOT NULL,
        FOREIGN KEY (roll_no) REFERENCES students (roll_no)
    )''')

    # --- Add Sample Student Data from the document ---
    students_to_add = [
        ('2403717624321055', 'Thirumaran S L', '9363915238'),
        ('2403717624322024', 'Kiruthika K', '7200239667')
    ]
    
    # Use IGNORE to prevent errors if students already exist
    cursor.executemany('INSERT OR IGNORE INTO students (roll_no, name, phone_no) VALUES (?, ?, ?)', students_to_add)

    conn.commit()
    conn.close()
    print("Database setup complete. System is ready.")

# --- CORE LOGIC ---
# Corresponds to the "Data Processing" and "Entry/Exit Logging System" modules

def get_last_status(roll_no):
    """Checks the database for the last recorded status of a student."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # This query will now work because the 'status' column will exist
    cursor.execute("SELECT status FROM gate_logs WHERE roll_no = ? ORDER BY timestamp DESC LIMIT 1", (roll_no,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result[0]
    else:
        # If no record exists, the student is assumed to be 'IN'
        return 'IN'

def log_student_movement(roll_no):
    """Logs a student's entry or exit."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # First, check if the student exists in the students table
    cursor.execute("SELECT name FROM students WHERE roll_no = ?", (roll_no,))
    student = cursor.fetchone()

    if not student:
        print(f"--- ALERT: Invalid ID card scanned. Roll No: {roll_no} not found. ---")
        conn.close()
        return

    student_name = student[0]
    last_status = get_last_status(roll_no)
    
    # Automatic toggling between IN and OUT
    new_status = 'OUT' if last_status == 'IN' else 'IN'
    
    current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert the new log into the database
    cursor.execute(
        "INSERT INTO gate_logs (roll_no, name, status, timestamp) VALUES (?, ?, ?, ?)",
        (roll_no, student_name, new_status, current_timestamp)
    )
    
    conn.commit()
    conn.close()

    # This print statement simulates the "real-time log" for security
    print(f"\n✅ Scan Successful!")
    print(f"   Name: {student_name}")
    print(f"   Roll No: {roll_no}")
    print(f"   Status Updated to: {new_status}")
    print(f"   Timestamp: {current_timestamp}")
    print("-" * 30)


# --- MAIN APPLICATION LOOP ---
def main():
    """Main function to run the gate pass system."""
    setup_database()
    print("\n--- CIT Smart Gate Pass System ---")
    print("--- Ready to scan student IDs ---")
    print("(Enter a Roll No. to simulate a scan, or type 'exit' to quit)\n")

    while True:
        # Simulate the barcode scanner reading the Student ID
        scanned_id = input("Scan ID Card (Enter Roll No.): ")

        if scanned_id.lower() == 'exit':
            print("Shutting down system.")
            break
        
        if scanned_id:
            # The system automatically records the entry/exit upon scan
            log_student_movement(scanned_id.strip())
        else:
            print("Invalid input. Please enter a Roll No.")

if __name__ == "__main__":
    main()