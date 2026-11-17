
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE v_contact_id INTEGER;
BEGIN
    IF p_phone IS NULL OR btrim(p_phone) = '' THEN
        RAISE EXCEPTION 'Phone cannot be empty';
    END IF;
    IF p_type IS NULL OR p_type NOT IN ('mobile', 'home', 'work') THEN
        RAISE EXCEPTION 'Invalid phone type: %', p_type;
    END IF;
    SELECT id INTO STRICT v_contact_id
    FROM contacts WHERE first_name = p_contact_name;
    INSERT INTO phones(contact_id, phone, type)
    VALUES(v_contact_id, p_phone, p_type);
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE EXCEPTION 'Contact not found: %', p_contact_name;
    WHEN TOO_MANY_ROWS THEN
        RAISE EXCEPTION 'Multiple contacts with name: %', p_contact_name;
END;
$$;

CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE v_contact_id INTEGER;
DECLARE v_group_id INTEGER;
BEGIN
    IF p_group_name IS NULL OR btrim(p_group_name) = '' THEN
        RAISE EXCEPTION 'Group name cannot be empty';
    END IF;
    SELECT id INTO STRICT v_contact_id
    FROM contacts WHERE first_name = p_contact_name;
    INSERT INTO groups(name) VALUES(btrim(p_group_name))
    ON CONFLICT (name) DO NOTHING;
    SELECT id INTO STRICT v_group_id FROM groups
    WHERE name = btrim(p_group_name);
    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE EXCEPTION 'Contact or group not found';
    WHEN TOO_MANY_ROWS THEN
        RAISE EXCEPTION 'Multiple contacts with name: %', p_contact_name;
END;
$$;

DROP FUNCTION IF EXISTS search_contacts(TEXT);
CREATE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    contact_id INTEGER,
    contact_name VARCHAR,
    contact_email VARCHAR,
    contact_birthday DATE,
    group_name VARCHAR
)
LANGUAGE sql AS $$
    SELECT c.id, c.first_name, c.email, c.birthday, g.name
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    WHERE c.first_name ILIKE '%' || COALESCE(p_query, '') || '%'
       OR c.email ILIKE '%' || COALESCE(p_query, '') || '%'
       OR EXISTS (
           SELECT 1 FROM phones p
           WHERE p.contact_id = c.id
             AND p.phone ILIKE '%' || COALESCE(p_query, '') || '%'
       )
    ORDER BY c.id;
$$;


DROP FUNCTION IF EXISTS get_contacts_page(INTEGER, INTEGER);
CREATE FUNCTION get_contacts_page(p_limit INTEGER, p_offset INTEGER)
RETURNS TABLE (
    contact_id INTEGER,
    contact_name VARCHAR,
    contact_email VARCHAR,
    group_name VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_limit IS NULL OR p_offset IS NULL OR p_limit <= 0 OR p_offset < 0 THEN
        RAISE EXCEPTION 'Invalid limit or offset';
    END IF;
    RETURN QUERY
    SELECT c.id, c.first_name, c.email, g.name
    FROM contacts c LEFT JOIN groups g ON c.group_id = g.id
    ORDER BY c.id LIMIT p_limit OFFSET p_offset;
END;
$$;
