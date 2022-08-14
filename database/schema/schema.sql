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

CREATE EXTENSION IF NOT EXISTS POSTGIS;

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

CREATE TABLE IF NOT EXISTS "FlightsData"
(
    "time" BIGINT,
    "aircraft_id" INTEGER,
    "flight_id" BIGINT,
    "position" GEOMETRY(PointZ, 4326),
    "velocity" REAL,
    "vertrate" REAL,
    "callsign" TEXT,
    "squawk" SMALLINT
) PARTITION BY RANGE("time");

CREATE TABLE IF NOT EXISTS "Flights"
(
    "flight_id" SERIAL,
    "start_time" BIGINT,
    "end_time" BIGINT
);

CREATE TABLE IF NOT EXISTS "Routes"
(
    "flight_id" BIGINT,
    "time" BIGINT,
    "position" GEOMETRY(PointZ, 4326)
);

CREATE TABLE IF NOT EXISTS "Statistics"
(
    "max_flight_duration" INTEGER
);

INSERT INTO "Statistics" ("max_flight_duration") VALUES(1);
