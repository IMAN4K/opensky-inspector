# -> Time:650 Cost:29848
SELECT
    "aircraft_id",
    "time",
    "position",
    ARRAY
    (
        SELECT
            "position"
        FROM
            "FlightsRoutes"
        WHERE
            "flight_number" = A."flight_number"
        AND
            "time" BETWEEN get_abs_min_flight_time(1607366101) AND 1607366101
        ORDER
            BY time DESC
        LIMIT  254
    ) AS trajectory
FROM
    (
        SELECT
            DISTINCT ON ("flight_number") "flight_number",
            "time",
            "position",
            "aircraft_id"
        FROM
            "AircraftsData"
        WHERE
            "time" BETWEEN get_abs_min_flight_time(1607366101) AND 1607366101
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
                "start_time" BETWEEN 1607366101 - get_max_flight_duration() AND 1607366101
                AND
                "end_time" BETWEEN 1607366101 AND 1607366101 + get_max_flight_duration()
        )
    )
    AND
    ST_Contains(ST_MakeEnvelope(-1.1426, 63.3127, 86.8359, 11.8674, 4326), "position")

# ?
SELECT
    AD."aircraft_id",
    AD."time",
    AD."position",
    ARRAY
    (
        SELECT
            "position"
        FROM
            "FlightsRoutes"
        WHERE
            "flight_number" = A."flight_number"
        AND
            "time" BETWEEN get_abs_min_flight_time(1607366101) AND 1607366101
        ORDER
            BY time DESC
        LIMIT  254
    ) AS trajectory
FROM
    (
        SELECT
            DISTINCT ON ("flight_number") "flight_number",
            "time"
        FROM
            "AircraftsData"
        WHERE
            "time" BETWEEN get_abs_min_flight_time(1607366101) AND 1607366101
        ORDER BY
            "flight_number", "time" DESC
    ) A,
    "AircraftsData" AD
WHERE
    A."flight_number" = AD."flight_number"
    AND
    A."time" = AD."time"
    AND
    A."flight_number" = ANY
    (
        ARRAY
        (
            SELECT
                "flight_number"
            FROM
                "FlightsSummary"
            WHERE
                "start_time" BETWEEN 1607366101 - get_max_flight_duration() AND 1607366101
                AND
                "end_time" BETWEEN 1607366101 AND 1607366101 + get_max_flight_duration()
        )
    )
--    AND
--    ST_Contains(ST_MakeEnvelope(-1.1426, 63.3127, 86.8359, 11.8674, 4326), AD."position")
