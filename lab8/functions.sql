CREATE FUNCTION search_contacts(p_pattern TEXT)
RETURNS TABLE (
    contact_id INTEGER,
    contact_name VARCHAR,
    contact_phone VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.first_name, p.phone
    FROM phonebook p
    WHERE p.first_name ILIKE '%' || p_pattern || '%'
       OR p.phone ILIKE '%' || p_pattern || '%';
END;
$$ LANGUAGE plpgsql;


CREATE FUNCTION get_contacts_page(
    p_limit INTEGER,
    p_offset INTEGER
)
RETURNS TABLE (
    contact_id INTEGER,
    contact_name VARCHAR,
    contact_phone VARCHAR
)
AS $$
BEGIN
    IF p_limit <= 0 OR p_offset < 0
       OR p_limit IS NULL OR p_offset IS NULL THEN
        RAISE EXCEPTION 'Invalid limit or offset';
    END IF;

    RETURN QUERY
    SELECT p.id, p.first_name, p.phone
    FROM phonebook p
    ORDER BY p.id
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;