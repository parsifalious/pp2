
import csv
from connect import conn


def add_contact(conn):
    name = input("Enter name: ")
    phone = input("Enter phone: ")

    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO phonebook (first_name, phone)
                VALUES (%s, %s)
                ON CONFLICT (phone) DO NOTHING
                """,
                (name, phone)
            )

            if cur.rowcount == 0:
                print("Phone number already exists!")
            else:
                print("Contact added!")


def update_contact(conn):
    old_phone = input("Enter current phone: ")

    print("1. Update name")
    print("2. Update phone")
    choice = input("Choose: ")

    if choice == "1":
        new_value = input("Enter new name: ")
        query = "UPDATE phonebook SET first_name = %s WHERE phone = %s"

    elif choice == "2":
        new_value = input("Enter new phone: ")
        query = "UPDATE phonebook SET phone = %s WHERE phone = %s"

    else:
        print("Invalid option!")
        return

    with conn:
        with conn.cursor() as cur:
            cur.execute(query, (new_value, old_phone))

            if cur.rowcount == 0:
                print("Contact not found!")
            else:
                print("Contact updated!")


def delete_contact(conn):
    print("1. Delete by name")
    print("2. Delete by phone")
    choice = input("Choose: ")

    if choice == "1":
        value = input("Enter name: ")
        query = "DELETE FROM phonebook WHERE first_name = %s"

    elif choice == "2":
        value = input("Enter phone: ")
        query = "DELETE FROM phonebook WHERE phone = %s"

    else:
        print("Invalid option!")
        return

    with conn:
        with conn.cursor() as cur:
            cur.execute(query, (value,))

            print("Deleted contacts:", cur.rowcount)


def import_csv(conn):
    with open("contacts.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        with conn:
            with conn.cursor() as cur:
                for row in reader:
                    cur.execute(
                        """
                        INSERT INTO phonebook (first_name, phone)
                        VALUES (%s, %s)
                        ON CONFLICT (phone) DO NOTHING
                        """,
                        (row["first_name"], row["phone"])
                    )

    print("CSV import completed!")


def show_contacts(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, first_name, phone FROM phonebook ORDER BY id"
        )
        contacts = cur.fetchall()

        if not contacts:
            print("PhoneBook is empty!")
            return

        print("\n" + "=" * 49)
        print(f"{'ID':<6} {'NAME':<20} {'PHONE':<20}")
        print("=" * 49)

        for contact in contacts:
            id, name, phone = contact
            print(f"{id:<6} {name:<20} {phone:<20}")

        print("=" * 49)


def search_contacts(conn):
    print("\n===== SEARCH CONTACTS =====")
    print("1. Search by name")
    print("2. Search by phone prefix")
    print("3. Show all contacts")

    choice = input("Choose an option: ")

    if choice == "1":
        name = input("Enter name: ")
        query = """
            SELECT id, first_name, phone
            FROM phonebook
            WHERE first_name ILIKE %s
            ORDER BY id
        """
        params = (f"%{name}%",)

    elif choice == "2":
        prefix = input("Enter phone prefix: ")
        query = """
            SELECT id, first_name, phone
            FROM phonebook
            WHERE phone LIKE %s
            ORDER BY id
        """
        params = (f"{prefix}%",)

    elif choice == "3":
        query = """
            SELECT id, first_name, phone
            FROM phonebook
            ORDER BY id
        """
        params = ()

    else:
        print("Invalid option!")
        return

    with conn.cursor() as cur:
        cur.execute(query, params)
        contacts = cur.fetchall()

    if not contacts:
        print("No contacts found!")
        return

    print("\n" + "-" * 52)
    print(f"{'ID':<6} {'NAME':<20} {'PHONE':<20}")
    print("-" * 52)

    for id, name, phone in contacts:
        print(f"{id:<6} {name:<20} {phone:<20}")

    print("-" * 52)



try:
    while True:
        print("\n===== PHONEBOOK =====")
        print("1 Add contact")
        print("2 Update contact")
        print("3 Delete contact")
        print("4 Import CSV")
        print("5 Show all contacts")
        print("6 Search contacts")
        print("0 Exit")
        print("Enter the digit to ")
        print("===== PHONEBOOK =====")

        choice = input("Choose an option: ")

        try:
            if choice == "1":
                add_contact(conn)

            elif choice == "2":
                update_contact(conn)

            elif choice == "3":
                delete_contact(conn)

            elif choice == "4":
                import_csv(conn)

            elif choice == "5":
                show_contacts(conn)

            elif choice == "6":
                search_contacts(conn)

            elif choice == "0":
                print("Goodbye!")
                break

            else:
                print("Invalid option!")

        except Exception as e:
            conn.rollback()
            print("Error:", e)

finally:
    conn.close()
