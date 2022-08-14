
INSERT INTO
    "AircraftsData" ("time", "icao24", "flight_number", "position", "velocity", "vertrate", "callsign", "squawk")
SELECT
    "time", hex_to_int("icao24"), 0, ST_MakePoint("lon", "lat", "geoaltitude"), "velocity", "vertrate", "callsign", "squawk"::SMALLINT
FROM
    "StateVectors"
ON CONFLICT ("time", "icao24")
DO NOTHING


INSERT INTO "FlightsSummary"("icao24", "start_time", "end_time")
SELECT
    "icao24",
    "start_time",
    "end_time"
FROM
    (
        SELECT
            "icao24",
            MIN("time") AS "start_time",
            MAX("time") AS "end_time",
            ROW_NUMBER() OVER (PARTITION BY "icao24" ORDER BY DELTA_T) AS "route_id"
        FROM
            (
                SELECT
                    "icao24",
                    "time",
                    ABS("time" - ((((ROW_NUMBER() over W) - 1) * 10) + (FIRST_VALUE("time") OVER W))) AS "delta_t"
                FROM
                    "AircraftsData"
                WINDOW W AS (PARTITION BY "icao24" ORDER BY "time")
            ) T
        GROUP BY
            "icao24", "delta_t"
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
    A.icao24 = B.icao24
    AND
   B.time BETWEEN A.start_time AND A.end_time
ORDER BY
    A.icao24, B.time


UPDATE public."AircraftsData" AS FD
SET "flight_number" = FS.flight_number
FROM "FlightsSummary" AS FS
WHERE
    FD.icao24 = FS.icao24
    AND
    FD.time BETWEEN FS.start_time AND FS.end_time
