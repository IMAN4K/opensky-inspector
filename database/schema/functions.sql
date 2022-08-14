-- MIT License
--
-- Copyright (c) 2022 Iman Ahmadvand
--
-- Permission is hereby granted, free of charge, to any person obtaining a copy
-- of this software and associated documentation files (the "Software"), to deal
-- in the Software without restriction, including without limitation the rights
-- to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
-- copies of the Software, and to permit persons to whom the Software is
-- furnished to do so, subject to the following conditions:
--
-- The above copyright notice and this permission notice shall be included in all
-- copies or substantial portions of the Software.
--
-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-- IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
-- OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
-- SOFTWARE.

SET search_path = public;

DROP FUNCTION IF EXISTS hex_to_int(TEXT);
CREATE OR REPLACE FUNCTION hex_to_int(hexval TEXT)
RETURNS INTEGER
AS $BODY$
DECLARE
    result INTEGER;
BEGIN
    EXECUTE 'SELECT x' || quote_literal(hexval) || '::INTEGER' INTO result;
    RETURN result;
END;
$BODY$ LANGUAGE plpgsql IMMUTABLE PARALLEL SAFE;

DROP FUNCTION IF EXISTS get_max_flight_duration();
CREATE OR REPLACE FUNCTION get_max_flight_duration()
RETURNS INTEGER
AS $BODY$
    SELECT "max_flight_duration" FROM "Statistics" LIMIT 1;
$BODY$ LANGUAGE sql IMMUTABLE PARALLEL SAFE;

DROP FUNCTION IF EXISTS get_abs_min_flight_time(BIGINT);
CREATE OR REPLACE FUNCTION get_abs_min_flight_time(time_point BIGINT)
RETURNS INTEGER
AS $BODY$
    SELECT
        MIN("start_time")
    FROM
        "Flights"
    WHERE
        "start_time" BETWEEN time_point - get_max_flight_duration() AND time_point
        AND
        "end_time" BETWEEN time_point + 1 AND time_point + get_max_flight_duration();
$BODY$ LANGUAGE sql IMMUTABLE PARALLEL SAFE;
