/**
   by @paulpierre 06/26/2019

   Sqlite schema
 */

DROP TABLE IF EXISTS city;
DROP TABLE IF EXISTS venue;


CREATE TABLE city(
 city_id INTEGER PRIMARY KEY,
 city_name TEXT,
 state TEXT,
 country TEXT,
 status DATETIME,
 tripadvisor_id INTEGER,
 tripadvisor_name TEXT,
 tripadvisor_full_name TEXT,
 tripadvisor_parent_name TEXT,
 tripadvisor_parent_place_type TEXT,
 tripadvisor_grandparent_name TEXT,
 tripadvisor_place_type INTEGER,
 tripadvisor_parent_ids TEXT, -- JSON
 tripadvisor_grandparent_id INTEGER,
 tripadvisor_url TEXT,
 tripadvisor_geo_name TEXT,
 tripadvisor_document_id TEXT,
 city_tcreate DATETIME NOT NULL,
 UNIQUE (city_name,state,country,tripadvisor_id,tripadvisor_geo_name) ON CONFLICT IGNORE

);


CREATE TABLE venue(
 id INTEGER PRIMARY KEY,
 venue_name TEXT,
 city_id INTEGER,
 venue_url TEXT,
 venue_email TEXT,
 venue_phone TEXT,
 venue_address TEXT,
 venue_cost FLOAT,
 venue_rating FLOAT,
 venue_rating_count INTEGER,
 venue_tcreate DATETIME NOT NULL,
 tripadvisor_category TEXT,
 tripadvisor_id TEXT,
FOREIGN KEY (city_id) REFERENCES city(city_id),
UNIQUE (venue_name,tripadvisor_category,tripadvisor_id) ON CONFLICT IGNORE
);

