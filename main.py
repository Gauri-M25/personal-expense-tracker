import sqlite3
from datetime import datetime

# ==========================================
# 1. DATABASE LAYER
# ==========================================
class Database:
    def __init__(self, db_name="expenses.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT
            )
        """)
        self.conn.commit()

    def add_expense(self, date, category, amount, description):
        self.cursor.execute("""
            INSERT INTO expenses (date, category, amount, description)
            VALUES (?, ?, ?, ?)
        """, (date, category, amount, description))
        self.conn.commit()

    def fetch_all(self):
        self.cursor.execute("SELECT id, date, category, amount, description FROM expenses")
        return self.cursor.fetchall()

    def delete_expense(self, expense_id):
        self.cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def close(self):
        self.conn.close()


# ==========================================
# 2. BUSINESS LOGIC (TRACKER)
# ==========================================
class ExpenseTracker:
    def __init__(self, user_name, budget, db):
        self.user_name = user_name
        self.__budget = budget  # Encapsulated attribute
        self.db = db

    def add_expense(self, category, amount, description=""):
        if amount <= 0:
            raise ValueError("Amount must be a positive number.")
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.db.add_expense(current_date, category.strip().title(), amount, description.strip())

    def total_expense(self):
        records = self.db.fetch_all()
        return sum(row[3] for row in records)

    def get_category_summary(self):
        records = self.db.fetch_all()
        summary = {}
        for row in records:
            cat, amt = row[2], row[3]
            summary[cat] = summary.get(cat, 0.0) + amt
        return summary

    def get_budget_status(self):
        total = self.total_expense()
        remaining = self.__budget - total
        is_exceeded = total > self.__budget
        return total, remaining, is_exceeded, self.__budget


# ==========================================
# 3. USER INTERFACE (CLI LOOP)
# ==========================================
def display_menu():
    print("\n==========================================")
    print("         PERSONAL EXPENSE TRACKER        ")
    print("==========================================")
    print("1. Add an Expense")
    print("2. View All Recorded Expenses")
    print("3. View Category-wise Breakdown")
    print("4. Check Budget Status")
    print("5. Delete an Expense by ID")
    print("6. Exit")
    print("==========================================")

def main():
    db = Database()
    
    print("Welcome to Expense Tracker Setup")
    user_name = input("Enter your name: ").strip()
    if not user_name:
        user_name = "User"

    while True:
        try:
            budget_input = input("Set your total budget (₹): ").strip()
            budget = float(budget_input)
            if budget <= 0:
                print("Budget must be greater than 0.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a valid numerical value.")

    tracker = ExpenseTracker(user_name, budget, db)
    print(f"\nWelcome, {user_name}! Your tracker is ready.")

    while True:
        display_menu()
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            cat = input("Enter category (e.g., Food, Travel, Rent): ").strip()
            if not cat:
                print("Category cannot be empty.")
                continue

            try:
                amt = float(input("Enter amount (₹): ").strip())
                desc = input("Enter description/note (optional): ").strip()
                tracker.add_expense(cat, amt, desc)
                print(" Expense recorded successfully!")
            except ValueError as e:
                print(f" Error: {e}")

        elif choice == "2":
            records = db.fetch_all()
            if not records:
                print("\nNo expenses found in database.")
            else:
                print("\nID | Date & Time       | Category   | Amount (₹) | Note")
                print("-" * 60)
                for r in records:
                    print(f"{r[0]:<2} | {r[1]:<17} | {r[2]:<10} | {r[3]:<10.2f} | {r[4]}")

        elif choice == "3":
            summary = tracker.get_category_summary()
            if not summary:
                print("\nNo expenses to summarize.")
            else:
                print("\n--- Category Breakdown ---")
                for category, total in summary.items():
                    print(f"• {category:<12}: ₹{total:.2f}")

        elif choice == "4":
            total, remaining, exceeded, max_budget = tracker.get_budget_status()
            print(f"\nAllocated Budget : ₹{max_budget:.2f}")
            print(f"Total Spent      : ₹{total:.2f}")
            print(f"Remaining Balance: ₹{remaining:.2f}")
            if exceeded:
                print("⚠️  Warning: You have exceeded your budget!")
            else:
                print("✅ Status: You are within your budget.")

        elif choice == "5":
            try:
                exp_id = int(input("Enter the ID of the expense to delete: ").strip())
                if db.delete_expense(exp_id):
                    print(f" Expense ID {exp_id} deleted successfully.")
                else:
                    print(f" No expense found with ID {exp_id}.")
            except ValueError:
                print(" Please enter a valid numerical ID.")

        elif choice == "6":
            print(f"\nThank you for using Expense Tracker, {user_name}! Goodbye.")
            db.close()
            break

        else:
            print(" Invalid choice. Please enter a number from 1 to 6.")

if __name__ == "__main__":
    main()