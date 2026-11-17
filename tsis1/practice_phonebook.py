
import csv
import json
import re
from datetime import date
from pathlib import Path

import psycopg2

BASE_DIR = Path(__file__).resolve().parent
DB = dict(host='localhost', database='PhoneBook', user='postgres',
          password='250145535776', port='5433')
PHONE_TYPES = {'mobile', 'home', 'work'}


def get_group_id(cur, name):
    name = (name or '').strip()
    if not name:
        return None
    cur.execute('INSERT INTO groups(name) VALUES (%s) ON CONFLICT (name) DO NOTHING', (name,))
    cur.execute('SELECT id FROM groups WHERE name=%s', (name,))
    return cur.fetchone()[0]


def select_contact(cur, name):
    cur.execute('SELECT id FROM contacts WHERE first_name=%s ORDER BY id', (name,))
    rows = [r[0] for r in cur.fetchall()]
    if not rows:
        print('Contact not found')
        return None
    if len(rows) == 1:
        return rows[0]
    print('Matching IDs:', rows)
    try:
        picked = int(input('Select contact ID: '))
        if picked in rows:
            return picked
    except ValueError:
        pass
    print('Invalid ID')
    return None


def new_contact(cur, item):
    name = str(item.get('first_name') or '').strip()
    if not name:
        raise ValueError('Contact name is required')
    birthday = item.get('birthday') or None
    if birthday:
        date.fromisoformat(birthday)
    group_id = get_group_id(cur, item.get('group'))
    cur.execute('''INSERT INTO contacts(first_name,email,birthday,group_id)
                   VALUES (%s,%s,%s,%s) RETURNING id''',
                (name, item.get('email') or None, birthday, group_id))
    contact_id = cur.fetchone()[0]
    put_phones(cur, contact_id, item.get('phones', []))
    return contact_id


def put_phones(cur, contact_id, phones):
    if not isinstance(phones, list):
        raise ValueError('phones must be a list')
    for entry in phones:
        if not isinstance(entry, dict):
            raise ValueError('Invalid phone entry')
        number = str(entry.get('phone') or '').strip()
        kind = entry.get('type') or 'mobile'
        if not number or kind not in PHONE_TYPES:
            raise ValueError(f'Invalid phone or type: {entry}')
        cur.execute('INSERT INTO phones(contact_id,phone,type) VALUES (%s,%s,%s)',
                    (contact_id, number, kind))




def add_contact(conn):
    name = input('Name: ').strip()
    phone = input('Phone: ').strip()
    kind = (input('Type (mobile/home/work) [mobile]: ').strip().lower() or 'mobile')
    email = input('Email (optional): ').strip() or None
    birthday = input('Birthday YYYY-MM-DD (optional): ').strip() or None
    group = input('Group (optional): ').strip()

    if not name or not phone or kind not in PHONE_TYPES:
        print('Invalid name, phone or phone type')
        return
    if birthday:
        date.fromisoformat(birthday)

    with conn:
        with conn.cursor() as cur:
            new_contact(cur, {
                'first_name': name,
                'email': email,
                'birthday': birthday,
                'group': group,
                'phones': [{'phone': phone, 'type': kind}]
            })
    print('Contact added successfully')


def update_phone(conn):
    name = input('Existing contact name: ').strip()
    with conn.cursor() as cur:
        contact_id = select_contact(cur, name)
        if contact_id is None:
            return
        cur.execute('SELECT id,phone,type FROM phones WHERE contact_id=%s ORDER BY id', (contact_id,))
        rows = cur.fetchall()
    print('Phones:', rows)
    if not rows:
        print('No phones to update. Use Add phone instead.')
        return
    phone_id = int(input('Phone ID to update: '))
    if phone_id not in [r[0] for r in rows]:
        print('Invalid phone ID')
        return
    new_phone = input('New phone: ').strip()
    new_type = input('Type (mobile/home/work) [mobile]: ').strip() or 'mobile'
    if not new_phone or new_type not in PHONE_TYPES:
        print('Invalid phone/type')
        return
    with conn:
        with conn.cursor() as cur:
            cur.execute('UPDATE phones SET phone=%s,type=%s WHERE id=%s AND contact_id=%s',
                        (new_phone, new_type, phone_id, contact_id))
    print('Phone updated')


def delete_contact(conn):
    choice = input('Delete by 1=name / 2=phone: ').strip()
    with conn.cursor() as cur:
        if choice == '1':
            contact_id = select_contact(cur, input('Name: ').strip())
        elif choice == '2':
            number = input('Phone: ').strip()
            cur.execute('SELECT DISTINCT contact_id FROM phones WHERE phone=%s', (number,))
            ids = [r[0] for r in cur.fetchall()]
            if len(ids) != 1:
                print('No unique contact matches this number')
                return
            contact_id = ids[0]
        else:
            return
    if contact_id is None or input(f'Delete contact ID {contact_id}? yes/no: ').strip().lower() != 'yes':
        return
    with conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM contacts WHERE id=%s', (contact_id,))
    print('Deleted')


def show_contacts(conn, group='', email='', sort_by='name'):
    columns = {'name': 'c.first_name', 'birthday': 'c.birthday', 'date': 'c.created_at'}
    order = columns.get(sort_by, 'c.first_name')
    sql = f'''SELECT c.id,c.first_name,c.email,c.birthday,g.name,
                     STRING_AGG(p.phone || ' (' || COALESCE(p.type,'mobile') || ')', ', ' ORDER BY p.id)
              FROM contacts c
              LEFT JOIN groups g ON c.group_id=g.id
              LEFT JOIN phones p ON c.id=p.contact_id
              WHERE (%s='' OR g.name ILIKE %s)
                AND (%s='' OR c.email ILIKE '%%' || %s || '%%')
              GROUP BY c.id,g.name
              ORDER BY {order} NULLS LAST,c.id'''
    with conn.cursor() as cur:
        cur.execute(sql, (group, group, email, email))
        rows = cur.fetchall()
    if not rows:
        print('No contacts found')
    for cid, name, mail, birthday, grp, phones in rows:
        print(f'[{cid}] {name} | email={mail or "-"} | birthday={birthday or "-"} '
              f'| group={grp or "-"} | phones={phones or "-"}')


def search_contacts(conn):
    query = input('Name / email / phone pattern: ')
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM search_contacts(%s)', (query,))
        rows = cur.fetchall()
    for row in rows:
        print(*row, sep=' | ')
    if not rows:
        print('No matches')


def pagination(conn):
    page = 0
    size = 5
    while True:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM contacts')
            total = cur.fetchone()[0]
            if not total:
                print('No contacts')
                return
            pages = (total + size - 1) // size
            page = min(page, pages - 1)
            cur.execute('SELECT * FROM get_contacts_page(%s,%s)', (size, page * size))
            rows = cur.fetchall()
        print(f'\n--- Page {page+1}/{pages} ---')
        for row in rows:
            print(*row, sep=' | ')
        action = input('next / prev / quit: ').strip().lower()
        if action == 'quit':
            return
        if action == 'next':
            if page < pages - 1:
                page += 1
            else:
                print('Last page')
        elif action == 'prev':
            if page:
                page -= 1
            else:
                print('First page')
        else:
            print('Unknown command')


def export_json(conn):
    filename = input('Filename [contacts.json]: ').strip() or 'contacts.json'
    with conn.cursor() as cur:
        cur.execute('''SELECT c.id,c.first_name,c.email,c.birthday,g.name,p.phone,p.type
                       FROM contacts c LEFT JOIN groups g ON g.id=c.group_id
                       LEFT JOIN phones p ON p.contact_id=c.id
                       ORDER BY c.id,p.id''')
        rows = cur.fetchall()
    contacts = {}
    for cid, name, mail, birthday, group, phone, kind in rows:
        if cid not in contacts:
            contacts[cid] = dict(first_name=name, email=mail,
                                 birthday=birthday.isoformat() if birthday else None,
                                 group=group, phones=[])
        if phone is not None:
            contacts[cid]['phones'].append(dict(phone=phone, type=kind or 'mobile'))
    path = BASE_DIR / filename
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(list(contacts.values()), f, indent=2, ensure_ascii=False)
    print(f'Exported {len(contacts)} contacts -> {path}')


def import_json(conn):
    filename = input('Filename [contacts.json]: ').strip() or 'contacts.json'
    with open(BASE_DIR / filename, encoding='utf-8') as f:
        items = json.load(f)
    if not isinstance(items, list):
        raise ValueError('JSON root must be an array')
    mode = input('On duplicate name: skip / overwrite: ').strip().lower()
    if mode not in ('skip', 'overwrite'):
        print('Invalid mode')
        return
    added = updated = skipped = 0
    with conn:
        with conn.cursor() as cur:
            for item in items:
                if not isinstance(item, dict) or not isinstance(item.get('first_name'), str):
                    raise ValueError('Each contact must have first_name')
                name = item['first_name'].strip()
                if not name:
                    raise ValueError('Empty contact name')
                # Validate before altering an existing record.
                birthday = item.get('birthday') or None
                if birthday:
                    date.fromisoformat(birthday)
                phone_items = item.get('phones', [])
                if not isinstance(phone_items, list):
                    raise ValueError('phones must be a list')
                for p in phone_items:
                    if not isinstance(p, dict) or not str(p.get('phone') or '').strip() or (p.get('type') or 'mobile') not in PHONE_TYPES:
                        raise ValueError(f'Invalid phone: {p}')
                cur.execute('SELECT id FROM contacts WHERE first_name=%s ORDER BY id', (name,))
                matches = [r[0] for r in cur.fetchall()]
                if matches and mode == 'skip':
                    skipped += 1
                    continue
                if len(matches) > 1:
                    print(f'Skipping ambiguous name {name!r}: {matches}')
                    skipped += 1
                    continue
                if matches:
                    cid = matches[0]
                    group_id = get_group_id(cur, item.get('group'))
                    cur.execute('''UPDATE contacts SET email=%s,birthday=%s,group_id=%s
                                   WHERE id=%s''',
                                (item.get('email') or None, birthday, group_id, cid))
                    cur.execute('DELETE FROM phones WHERE contact_id=%s', (cid,))
                    put_phones(cur, cid, phone_items)
                    updated += 1
                else:
                    new_contact(cur, item)
                    added += 1
    print(f'JSON import: added={added}, overwritten={updated}, skipped={skipped}')


def import_csv(conn):
    filename = input('Filename [contacts.csv]: ').strip() or 'contacts.csv'
    with open(BASE_DIR / filename, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not {'first_name', 'phone'}.issubset(reader.fieldnames):
            raise ValueError('CSV requires first_name and phone columns')
        data = list(reader)
    count = 0
    with conn:
        with conn.cursor() as cur:
            for row in data:
                phone = (row.get('phone') or '').strip()
                name = (row.get('first_name') or '').strip()
                if not phone or not name:
                    print('Skipping empty name or phone')
                    continue
                cur.execute('SELECT 1 FROM phones WHERE phone=%s', (phone,))
                if cur.fetchone():
                    print('Skipping existing phone:', phone)
                    continue
                new_contact(cur, dict(first_name=name, email=row.get('email'),
                                      birthday=row.get('birthday'), group=row.get('group'),
                                      phones=[dict(phone=phone, type=row.get('type') or 'mobile')]))
                count += 1
    print(f'CSV imported: {count}')


def add_phone(conn):
    name = input('Existing contact name: ').strip()
    phone = input('New phone: ').strip()
    kind = input('Type (mobile/home/work): ').strip().lower()
    if not name or not phone or kind not in PHONE_TYPES:
        print('Invalid name, phone or type')
        return
    with conn:
        with conn.cursor() as cur:
            cur.execute('CALL add_phone(%s::varchar,%s::varchar,%s::varchar)', (name, phone, kind))
    print('Phone added via procedure')


def move_to_group(conn):
    name = input('Existing contact name: ').strip()
    group = input('New group name: ').strip()
    if not name or not group:
        print('Name and group cannot be empty')
        return
    with conn:
        with conn.cursor() as cur:
            cur.execute('CALL move_to_group(%s::varchar,%s::varchar)', (name, group))
    print('Group updated via procedure')


def bulk_insert(conn):
    names = [s.strip() for s in input('Names (comma-separated): ').split(',')]
    numbers = [s.strip() for s in input('Phones (comma-separated): ').split(',')]
    if len(names) != len(numbers):
        print('Unequal lengths')
        return
    invalid = []
    with conn:
        with conn.cursor() as cur:
            for name, number in zip(names, numbers):
                if not name or not re.fullmatch(r'87\d{9}', number):
                    invalid.append((name, number))
                    continue
                cur.execute('SELECT id FROM contacts WHERE first_name=%s', (name,))
                matches = [r[0] for r in cur.fetchall()]
                if len(matches) > 1:
                    invalid.append((name, number))
                    continue
                if matches:
                    cid = matches[0]
                else:
                    cur.execute('INSERT INTO contacts(first_name) VALUES (%s) RETURNING id', (name,))
                    cid = cur.fetchone()[0]
                cur.execute('SELECT 1 FROM phones WHERE contact_id=%s AND phone=%s', (cid, number))
                if not cur.fetchone():
                    put_phones(cur, cid, [dict(phone=number, type='mobile')])
    print('Bulk insert completed; invalid:', invalid)


def main():
    actions = {
        '1': ('Add contact', add_contact),
        '2': ('Update phone', update_phone),
        '3': ('Delete contact', delete_contact),
        '4': ('Import CSV', import_csv),
        '5': ('Show contacts', show_contacts),
        '6': ('Search name/email/phone', search_contacts),
        '7': ('Bulk insert', bulk_insert),
        '8': ('Pagination', pagination),
        '9': ('Filter by group', lambda conn: show_contacts(conn, group=input('Group: ').strip())),
        '10': ('Search by email', lambda conn: show_contacts(conn, email=input('Email pattern: ').strip())),
        '11': ('Sort contacts', lambda conn: show_contacts(conn, sort_by=input('name / birthday / date: ').strip().lower())),
        '12': ('Add phone (procedure)', add_phone),
        '13': ('Move to group (procedure)', move_to_group),
        '14': ('Export JSON', export_json),
        '15': ('Import JSON', import_json),
    }
    conn = psycopg2.connect(**DB)
    try:
        while True:
            print('\n====== TSIS 1 PHONEBOOK ======')
            for key, (label, _) in actions.items():
                print(f'{key}. {label}')
            print('0. Exit')
            choice = input('Choose: ').strip()
            if choice == '0':
                print('Peace')
                return
            if choice not in actions:
                print('Invalid choice')
                continue
            try:
                actions[choice][1](conn)
            except (psycopg2.Error, ValueError, KeyError, OSError, TypeError) as exc:
                conn.rollback()
                print('Error:', exc)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
