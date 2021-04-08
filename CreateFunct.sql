DROP FUNCTION  IF EXISTS concat_lower_or_upper(text,text,bool);

CREATE FUNCTION concat_lower_or_upper(a text, b text, uppercase boolean DEFAULT false)
RETURNS text
AS
$$
 SELECT CASE
        WHEN uppercase THEN UPPER(a || ' ' || b)
        ELSE LOWER(a || ' ' || b)
        END;
$$
LANGUAGE SQL IMMUTABLE STRICT;

SELECT concat_lower_or_upper('Hello', 'World', true);
