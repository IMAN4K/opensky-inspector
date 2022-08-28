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

INSERT INTO
    "AircraftsData" ("time", "aircraft_id", "flight_number", "position", "velocity", "vertrate", "callsign", "squawk")
SELECT
    "time", hex_to_int("icao24"), 0, ST_MakePoint("lon", "lat", "geoaltitude"), "velocity", "vertrate", "callsign", "squawk"::SMALLINT
FROM
    "StateVectors"

INSERT INTO "FlightsSummary"("aircraft_id", "start_time", "end_time")
SELECT
    "aircraft_id",
    "start_time",
    "end_time"
FROM
    (
        SELECT
            "aircraft_id",
            MIN("time") AS "start_time",
            MAX("time") AS "end_time",
            ROW_NUMBER() OVER (PARTITION BY "aircraft_id" ORDER BY DELTA_T) AS "route_id"
        FROM
            (
                SELECT
                    "aircraft_id",
                    "time",
                    ABS("time" - ((((ROW_NUMBER() over W) - 1) * 10) + (FIRST_VALUE("time") OVER W))) AS "delta_t"
                FROM
                    "AircraftsData"
                WINDOW W AS (PARTITION BY "aircraft_id" ORDER BY "time")
            ) T
        GROUP BY
            "aircraft_id", "delta_t"
    ) A
WHERE
    A.start_time != A.end_time


INSERT INTO "FlightsRoutes" ("time", "flight_number", "position");
SELECT
    B.time,
    A.flight_number,
    B.position
FROM
    "FlightsSummary" A
JOIN
    public."AircraftsData" B
ON
    A.aircraft_id = B.aircraft_id
    AND
   B.time BETWEEN A.start_time AND A.end_time
ORDER BY
    A.aircraft_id, B.time


UPDATE public."AircraftsData" AS FD
SET "flight_number" = FS.flight_number
FROM "FlightsSummary" AS FS
WHERE
    FD.aircraft_id = FS.aircraft_id
    AND
    FD.time BETWEEN FS.start_time AND FS.end_time
