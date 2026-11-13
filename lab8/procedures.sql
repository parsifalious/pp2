CREATE OR REPLACE FUNCTION public.search_contacts(p_pattern text)
 RETURNS TABLE(contact_id integer, contact_name character varying, contact_phone character varying)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT p.id, p.first_name, p.phone
    FROM phonebook p
    WHERE p.first_name ILIKE '%' || p_pattern || '%'
       OR p.phone ILIKE '%' || p_pattern || '%';
END;
$function$


CREATE OR REPLACE PROCEDURE public.upsert_contact(IN p_name character varying, IN p_phone character varying)
 LANGUAGE plpgsql
AS $procedure$
BEGIN
    IF EXISTS (
        SELECT 1 FROM phonebook
        WHERE first_name = p_name
    ) THEN
        UPDATE phonebook
        SET phone = p_phone
        WHERE first_name = p_name;
    ELSE
        INSERT INTO phonebook (first_name, phone)
        VALUES (p_name, p_phone);
    END IF;
END;
$procedure$


CREATE OR REPLACE PROCEDURE public.bulk_insert_contacts(IN p_names text[], IN p_phones text[], OUT invalid_data text[])
 LANGUAGE plpgsql
AS $procedure$
DECLARE
    i INTEGER;
BEGIN
    invalid_data := ARRAY[]::TEXT[];

    IF array_length(p_names, 1) IS DISTINCT FROM
       array_length(p_phones, 1) THEN
        RAISE EXCEPTION 'Names and phones count must match';
    END IF;

    FOR i IN 1..COALESCE(array_length(p_names, 1), 0) LOOP
        IF p_phones[i] IS NULL
           OR p_phones[i] !~ '^87[0-9]{9}$' THEN

            invalid_data := array_append(
                invalid_data,
                p_names[i] || ': ' || COALESCE(p_phones[i], 'NULL')
            );
        ELSE
            INSERT INTO phonebook(first_name, phone)
            VALUES(p_names[i], p_phones[i])
            ON CONFLICT (phone) DO NOTHING;
        END IF;
    END LOOP;
END;
$procedure$


CREATE OR REPLACE FUNCTION public.get_contacts_page(p_limit integer, p_offset integer)
 RETURNS TABLE(contact_id integer, contact_name character varying, contact_phone character varying)
 LANGUAGE plpgsql
AS $function$
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
$function$



CREATE OR REPLACE PROCEDURE public.delete_contact(IN p_name character varying, IN p_phone character varying)
 LANGUAGE plpgsql
AS $procedure$
BEGIN
    DELETE FROM phonebook
    WHERE (p_name IS NOT NULL AND first_name = p_name)
       OR (p_phone IS NOT NULL AND phone = p_phone);
END;
$procedure$
