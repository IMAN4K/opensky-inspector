-- MIT License

-- Copyright (c) 2022 Iman Ahmadvand

-- Permission is hereby granted, free of charge, to any person obtaining a copy
-- of this software and associated documentation files (the "Software"), to deal
-- in the Software without restriction, including without limitation the rights
-- to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
-- copies of the Software, and to permit persons to whom the Software is
-- furnished to do so, subject to the following conditions:

-- The above copyright notice and this permission notice shall be included in all
-- copies or substantial portions of the Software.

-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-- IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
-- OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
-- SOFTWARE.

SET search_path = public;

CREATE EXTENSION IF NOT EXISTS POSTGIS;

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

DROP FUNCTION IF EXISTS hex(TEXT);
CREATE OR REPLACE FUNCTION hex(val TEXT)
RETURNS TEXT
AS $BODY$
    SELECT encode($1::bytea, 'hex');
$BODY$ LANGUAGE sql IMMUTABLE STRICT;

DROP FUNCTION IF EXISTS hex(INTEGER);
CREATE OR REPLACE FUNCTION hex(val INTEGER)
RETURNS TEXT
AS $BODY$
    SELECT to_hex($1);
$BODY$ LANGUAGE sql IMMUTABLE STRICT;

CREATE TABLE IF NOT EXISTS "StateVectors"
(
    "time" BIGINT,
    "icao24" TEXT,
    "lat" REAL,
    "lon" REAL,
    "velocity" REAL,
    "heading" REAL,
    "vertrate" REAL,
    "callsign" TEXT,
    "onground" BOOL,
    "alert" BOOL,
    "spi" BOOL,
    "squawk" BIGINT,
    "baroaltitude" REAL,
    "geoaltitude" REAL,
    "lastposupdate" REAL,
    "lastcontact" REAL
);

CREATE TABLE IF NOT EXISTS "FlightsSummary"
(
    "flight_number" SERIAL,
    "start_time" BIGINT,
    "end_time" BIGINT,
    "aircraft_id" INTEGER NOT NULL,
    CHECK("end_time" > "start_time")
);

CREATE INDEX IF NOT EXISTS "flights_summary_composite_time_idx" ON "FlightsSummary" ("start_time", "end_time") INCLUDE("flight_number", "aircraft_id");

CREATE TABLE IF NOT EXISTS "FlightsRoutes"
(
    "flight_number" BIGINT,
    "time" BIGINT,
    "position" GEOMETRY(PointZ, 4326),
    CHECK("position" IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS "flights_routes_flight_number_time_idx" ON "FlightsRoutes" ("flight_number", "time" DESC) INCLUDE("position");

CREATE TABLE IF NOT EXISTS "AircraftsData"
(
    "time" BIGINT,
    "aircraft_id" INTEGER,
    "flight_number" BIGINT,
    "position" GEOMETRY(PointZ, 4326),
    "velocity" REAL,
    "vertrate" REAL,
    "callsign" TEXT,
    "squawk" SMALLINT
);

CREATE INDEX IF NOT EXISTS "aircrafts_data_composite_time_idx" ON "AircraftsData" ("flight_number", "time" DESC);
CREATE INDEX IF NOT EXISTS "aircrafts_data_position_idx" ON "AircraftsData" USING GIST ("position");

CREATE TABLE IF NOT EXISTS "GlobalStatistics"
(
    "max_flight_duration" INTEGER
);

INSERT INTO "GlobalStatistics" ("max_flight_duration") VALUES(1);

DROP FUNCTION IF EXISTS get_max_flight_duration();
CREATE OR REPLACE FUNCTION get_max_flight_duration()
RETURNS INTEGER
AS $BODY$
    SELECT "max_flight_duration" FROM "GlobalStatistics" LIMIT 1;
$BODY$ LANGUAGE sql IMMUTABLE PARALLEL SAFE;

DROP FUNCTION IF EXISTS get_abs_min_flight_time(BIGINT);
CREATE OR REPLACE FUNCTION get_abs_min_flight_time(time_point BIGINT)
RETURNS BIGINT
AS $BODY$
    SELECT
        MIN("start_time")
    FROM
        "FlightsSummary"
    WHERE
        "start_time" BETWEEN time_point - get_max_flight_duration() AND time_point
        AND
        "end_time" BETWEEN time_point AND time_point + get_max_flight_duration();
$BODY$ LANGUAGE sql IMMUTABLE PARALLEL SAFE;

DROP FUNCTION IF EXISTS get_snapshot(BIGINT);
CREATE OR REPLACE FUNCTION get_snapshot(time_point BIGINT)
RETURNS TABLE (foo JSON)
AS $BODY$
BEGIN
    RETURN QUERY
    SELECT
        json_build_object
        (
            'kAircraftId', hex("aircraft_id"),
            'kTime', TO_TIMESTAMP("time"),
            'kPosition', ST_AsGeoJSON("position"),
            'kVelocity', "velocity",
            'kVertrate', "vertrate",
            'kCallsign', "callsign",
            'kSquawk', "squawk",
            'kTrajectory', ST_AsGeoJSON (
                ST_Collect
                (
                    ARRAY
                            (
                                SELECT
                                    "position"
                                FROM
                                    "FlightsRoutes"
                                WHERE
                                    "flight_number" = A."flight_number"
                                AND
                                    "time" BETWEEN get_abs_min_flight_time(time_point) AND time_point
                                ORDER
                                    BY time DESC
                            )
                )
            )
        )
    FROM
        (
            SELECT
                DISTINCT ON ("flight_number") "flight_number",
                "time",
                "position",
                "aircraft_id",
                "velocity",
                "vertrate",
                "callsign",
                "squawk"
            FROM
                "AircraftsData"
            WHERE
                "time" BETWEEN get_abs_min_flight_time(time_point) AND time_point
            ORDER BY
                "flight_number", "time" DESC
        ) A
    WHERE
        "flight_number" = ANY
        (
            ARRAY
            (
                SELECT
                    "flight_number"
                FROM
                    "FlightsSummary"
                WHERE
                    "start_time" BETWEEN time_point - get_max_flight_duration() AND time_point
                    AND
                    "end_time" BETWEEN time_point AND time_point + get_max_flight_duration()
            )
        );
END
$BODY$ LANGUAGE plpgsql IMMUTABLE PARALLEL SAFE;

