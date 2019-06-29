/**
   by @paulpierre 06/26/2019

   Sqlite schema
 */

DROP TABLE IF EXISTS city;


CREATE TABLE city(
 city_id INTEGER PRIMARY KEY,
 city_geo_id INTEGER,
 country_geo_id INTEGER,
 city_name TEXT,
 region_name TEXT,
 country_name TEXT,
 listing_url TEXT,
 status INTEGER,
 city_tcreate DATETIME NOT NULL,
 city_tmodified DATETIME NOT NULL,
 UNIQUE (city_geo_id) ON CONFLICT IGNORE
);

DROP TABLE IF EXISTS venue;

CREATE TABLE venue(
 id INTEGER PRIMARY KEY,
 venue_name TEXT,
 venue_id INTEGER,
 venue_url TEXT,
 venue_img TEXT,
 venue_email TEXT,
 venue_phone TEXT,
 venue_website TEXT,
 city_name TEXT,
 country_name TEXT,
 country_geo_id INTEGER,
 city_geo_id INTEGER,
 venue_street_address TEXT,
 venue_locality TEXT,
 region_name TEXT,
 venue_postal_code TEXT,
 venue_cost FLOAT,
 venue_rating FLOAT,
 venue_review_count INTEGER,
 status INTEGER,
 venue_tcreate DATETIME NOT NULL,
 venue_long FLOAT,
 venue_lat FLOAT,
 venue_tmodified DATETIME NOT NULL,
FOREIGN KEY (city_geo_id) REFERENCES city(city_geo_id),
UNIQUE (venue_name,venue_id,city_geo_id,country_geo_id) ON CONFLICT IGNORE
);

