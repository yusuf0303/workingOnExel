from handlers.users.admin import get_db_connection

# Add Contractor function
def add_contractor(contractor_id, full_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select telegram_id from users")
    users_ids = cursor.fetchall()
    users = []
    for user in users_ids:
        users.append(user[0])

    if int(contractor_id) not in users:
        cursor.execute("INSERT INTO users (telegram_id, name, role) VALUES (%s, %s, 'contractor')",
                    (contractor_id, full_name))
        conn.commit()
        return True
    else:
        return False

def delete_contractor(contractor_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select telegram_id from users")
    users_ids = cursor.fetchall()
    users = []
    for user in users_ids:
        users.append(user[0])

    if int(contractor_id) in users:
        cursor.execute("delete from users where telegram_id = %s", (contractor_id,))
        conn.commit()
        return True
    else:
        return False



# Function to check if the given text is a valid Telegram ID
def is_valid_telegram_id(telegram_id: str) -> bool:
    # Check if the text is a numeric string (i.e., only digits)
    if telegram_id.isdigit():
        # Convert to integer
        user_id = int(telegram_id)
        
        # Check if it's a valid Telegram ID
        # Telegram ID is a positive integer and typically less than 2^31-1 (2147483647) for users
        # Chat IDs can also be negative (for groups, channels, etc.), so allow negative values
        if -2**63 <= user_id <= 2**63-1:  # Using a wide range, suitable for user/chat IDs
            return True
    return False
