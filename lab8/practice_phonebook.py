import psycopg2
import csv

conn = psycopg2.connect(
    host="localhost",
    database="PhoneBook",
    user="postgres",
    password="250145535776",
    port="5433"
)


def add_contact(conn):
    name = input("Input Name: ")
    phone = input("Input Phone Number: ")
    with conn:
        with conn.cursor() as cur:
            cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
    print("Contact added or updated successfully")


def update_contact(conn):
    name = input("Input existing name: ")
    new_phone = input("Input new phone number: ")
    with conn:
        with conn.cursor() as cur:
            cur.execute("CALL upsert_contact(%s, %s)", (name, new_phone))
    print("Contact added or updated successfully")


def delete_contact(conn):
    print("1. Delete by name")
    print("2. Delete by phone")
    choice = input("Choose: ")
    if choice == "1":
        name = input("Enter name: ")
        args = (name, None)
    elif choice == "2":
        phone = input("Enter phone: ")
        args = (None, phone)
    else:
        print("Invalid choice")
        return
    with conn:
        with conn.cursor() as cur:
            cur.execute("CALL delete_contact(%s, %s)", args)
    print("Delete procedure executed")


def import_csv(conn):
    with open("contacts.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        with conn:
            with conn.cursor() as cur:
                for row in reader:
                    cur.execute(
                        "INSERT INTO phonebook (first_name, phone) VALUES (%s, %s) "
                        "ON CONFLICT (phone) DO NOTHING",
                        (row["first_name"], row["phone"])
                    )
                    print("Added" if cur.rowcount else "Phone already exists")


def show_contacts(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id, first_name, phone FROM phonebook ORDER BY id")
        contacts = cur.fetchall()
    if not contacts:
        print("No contacts")
    for contact in contacts:
        print(*contact)


def search_contact(conn):
    pattern = input("Enter part of name or phone: ")
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
        contacts = cur.fetchall()
    if not contacts:
        print("No contacts found")
    for contact in contacts:
        print(*contact)


def bulk_insert(conn):
    names = [x.strip() for x in input("Names (through comma): ").split(",")]
    phones = [x.strip() for x in input("Phones (through comma): ").split(",")]
    with conn:
        with conn.cursor() as cur:
            cur.execute("CALL bulk_insert_contacts(%s, %s, NULL)", (names, phones))
            invalid_data = cur.fetchone()[0]
    print("Bulk insert completed")
    print("Invalid data:", invalid_data)


def pagination(conn):
    try:
        limit = int(input("Limit: "))
        offset = int(input("Offset: "))
    except ValueError:
        print("Limit and offset must be integers")
        return
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM get_contacts_page(%s, %s)", (limit, offset))
        contacts = cur.fetchall()
    if not contacts:
        print("No contacts on this page")
    for contact in contacts:
        print(*contact)


try:
    while True:
        print("\n1. Add contact")
        print("2. Update contact phone")
        print("3. Delete contact")
        print("4. Import CSV")
        print("5. Show contacts")
        print("6. Search contacts")
        print("7. Bulk insert")
        print("8. Pagination")
        print("0. Exit")
        choice = input("Choose: ")
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
                search_contact(conn)
            elif choice == "7":
                bulk_insert(conn)
            elif choice == "8":
                pagination(conn)
            elif choice == "0":
                print("Peace")
                break
            else:
                print("Invalid choice")
        except psycopg2.Error as error:
            print("Database error:", error)
        except (OSError, KeyError) as error:
            print("Error:", error)
finally:
    conn.close()
