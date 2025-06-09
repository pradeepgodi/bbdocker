CREATE EXTENSION IF NOT EXISTS postgis;


-- vishram ghar outlets
CREATE TABLE vishram_ghar (
    omc TEXT,
    code TEXT,
    name TEXT,
    area TEXT,
    latitude FLOAT,
    longitude FLOAT  
);


COPY vishram_ghar(omc, code, name, area, latitude, longitude)
FROM '/docker-entrypoint-initdb.d/vishram_ghar_data.csv'
DELIMITER ','
CSV HEADER;

ALTER TABLE vishram_ghar
ADD COLUMN location GEOMETRY(Point, 4326);

UPDATE vishram_ghar
SET location = ST_SetSRID(
                  ST_MakePoint(
                      longitude::DOUBLE PRECISION,
                      latitude::DOUBLE PRECISION
                  ),
                  4326
              );


-- fuel table sql queries
CREATE TABLE bunksbuddyproducts(id integer,product TEXT, city varchar(100),latitude float,longitude float,price float);

COPY bunksbuddyproducts(id,product,city, latitude, longitude, price)
FROM '/docker-entrypoint-initdb.d/fuel_data_updated.csv'
DELIMITER ','
CSV HEADER;


ALTER TABLE bunksbuddyproducts
ADD COLUMN location GEOMETRY(Point, 4326);

UPDATE bunksbuddyproducts
SET location = ST_SetSRID(ST_MakePoint(longitude::DOUBLE PRECISION,latitude::DOUBLE PRECISION ),4326);
----------------------------------

-- create hsitroy new table
CREATE TABLE history_new (
    id integer,
    phone TEXT,
    price FLOAT,
    litres FLOAT,
    saved FLOAT,
    creationdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    petrolbunkid TEXT,
    product TEXT);

COPY history_new(id, phone, price, litres, saved, creationdate, petrolbunkid, product)
FROM '/docker-entrypoint-initdb.d/history_new.csv'
DELIMITER ','
CSV HEADER;

--"id","phone","price","litres","saved","creationdate","petrolbunkid","product"
------------------------------------



----------users_new table sql queries
CREATE TABLE users_new (
    id integer,
    name TEXT,
    phone TEXT,
    vehicle_number TEXT,
    dob TEXT,
    createdat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedat TIMESTAMP DEFAULT CURRENT_TIMESTAMP ) ;

COPY users_new(id,name, phone, vehicle_number, dob,createdat, updatedat)
FROM '/docker-entrypoint-initdb.d/users_new.csv'
DELIMITER ','
CSV HEADER;   
--------------------------------------

----- weigh bridge table sql queries
CREATE TABLE weigh_bridge_statewise (
    name TEXT,
    phone TEXT,
    city TEXT,
    state TEXT,
    pincode TEXT,
    business_status TEXT,
    latitude FLOAT,
    longitude FLOAT,
    formatted_address TEXT,
    place_id TEXT,
    rating TEXT,
    user_ratings_total TEXT
);

ALTER TABLE weigh_bridge_statewise
ADD COLUMN location GEOMETRY(Point, 4326),
ADD COLUMN capacity TEXT,
ADD COLUMN length TEXT;



UPDATE weigh_bridge_statewise
SET location = ST_SetSRID(
                  ST_MakePoint(
                      longitude::DOUBLE PRECISION,
                      latitude::DOUBLE PRECISION
                  ),
                  4326
              );
----------------------------------

-- ev data 
CREATE TABLE ev_stations (
    name TEXT,
    latitude FLOAT,
    longitude FLOAT,
    phone TEXT,
    address TEXT
);

COPY ev_stations(name, latitude, longitude, phone, address)
FROM '/docker-entrypoint-initdb.d/ev_data.csv'
DELIMITER ','
CSV HEADER;

ALTER TABLE ev_stations
ADD COLUMN location GEOMETRY(Point, 4326);

UPDATE ev_stations
SET location = ST_SetSRID(
                  ST_MakePoint(
                      longitude::DOUBLE PRECISION,
                      latitude::DOUBLE PRECISION
                  ),
                  4326
              );


-------- CNG table sql queries
CREATE TABLE cng_stations (
    name TEXT,
    latitude FLOAT,
    longitude FLOAT,
    phone TEXT,
    address TEXT
);

ALTER TABLE cng_stations
ADD COLUMN location GEOMETRY(Point, 4326);

UPDATE cng_stations
SET location = ST_SetSRID(ST_MakePoint(longitude::DOUBLE PRECISION,latitude::DOUBLE PRECISION ),4326);

COPY cng_stations(name, latitude, longitude, phone, address)
FROM '/docker-entrypoint-initdb.d/cng_data.csv'
DELIMITER ','
CSV HEADER;

-- Toll plaza sql queries

CREATE TABLE toll_plaza (
    sr_no FLOAT,
    state TEXT,
    nh_no TEXT,
    toll_plaza_name TEXT,
    toll_plaza_location TEXT,
    section_stretch TEXT,
    tollplazaid FLOAT,
    latitude FLOAT,
    longitude FLOAT,
    place_id TEXT,
    address_partial_match TEXT,
    toll_plaza_id FLOAT,
    stretch TEXT,
    tollable_length TEXT,
    fee_effective_date TEXT,
    due_date_of_toll_revision TEXT,
    concessions TEXT,
    rest_areas TEXT,
    truck_lay_byes TEXT,
    static_weigh_bridge TEXT,
    announcement TEXT,
    helpline_no TEXT,
    emergency_services TEXT,
    nearest_police_station TEXT,
    highway_administrator_project_director TEXT,
    project_implementation_unit_piu TEXT,
    regional_office_ro TEXT,
    representative_of_consultant TEXT,
    representative_of_concessionaire TEXT,
    nearest_hospital_s TEXT,
    date_of_fee_notification TEXT,
    commercial_operation_date TEXT,
    fee_rule TEXT,
    capital_cost_of_project_in_rs_cr TEXT,
    cumulative_toll_revenue_in_rs_cr TEXT,
    concessions_period TEXT,
    design_capacity_pcu TEXT,
    traffic_pcu_day TEXT,
    target_traffic_pcu_day TEXT,
    name_of_concessionaire_omt_contractor TEXT,
    name_contact_details_of_incharge TEXT,
    car_jeep_van_single_journey FLOAT,
    car_jeep_van_return_journey FLOAT,
    car_jeep_van_monthly_pass FLOAT,
    car_jeep_van_commercial_vehicle_reg_in_district FLOAT,
    lcv_single_journey FLOAT,
    lcv_return_journey FLOAT,
    lcv_monthly_pass FLOAT,
    lcv_commercial_vehicle_reg_in_district FLOAT,
    bus_truck_single_journey FLOAT,
    bus_truck_return_journey FLOAT,
    bus_truck_monthly_pass FLOAT,
    bus_truck_commercial_vehicle_reg_in_district FLOAT,
    upto_3_axle_vehicle_single_journey FLOAT,
    upto_3_axle_vehicle_return_journey FLOAT,
    upto_3_axle_vehicle_monthly_pass FLOAT,
    upto_3_axle_vehicle_commercial_vehicle_rreg_in_district FLOAT,
    _4_to_6_axle_single_journey FLOAT,
    _4_to_6_axle_return_journey FLOAT,
    _4_to_6_axle_monthly_pass FLOAT,
    _4_to_6_axle_commercial_vehicle_reg_in_district FLOAT,
    hcm_eme_single_journey FLOAT,
    hcm_eme_return_journey FLOAT,
    hcm_eme_monthly_pass FLOAT,
    hcm_eme_commercial_vehicle_reg_in_district FLOAT,
    _7_or_more_axle_single_journey FLOAT,
    _7_or_more_axle_return_journey FLOAT,
    _7_or_more_axle_monthly_pass FLOAT,
    _7_or_more_axle_commercial_reg_in_district FLOAT
);

COPY toll_plaza(sr_no,state,nh_no,toll_plaza_name,toll_plaza_location,section_stretch,tollplazaid,latitude,longitude,place_id,address_partial_match,toll_plaza_id,stretch,tollable_length,fee_effective_date,due_date_of_toll_revision,concessions,rest_areas,truck_lay_byes,static_weigh_bridge,announcement,helpline_no,emergency_services,nearest_police_station,highway_administrator_project_director,project_implementation_unit_piu,regional_office_ro,representative_of_consultant,representative_of_concessionaire,nearest_hospital_s,date_of_fee_notification,commercial_operation_date,fee_rule,capital_cost_of_project_in_rs_cr,cumulative_toll_revenue_in_rs_cr,concessions_period,design_capacity_pcu,traffic_pcu_day,target_traffic_pcu_day,name_of_concessionaire_omt_contractor,name_contact_details_of_incharge,car_jeep_van_single_journey,car_jeep_van_return_journey,car_jeep_van_monthly_pass,car_jeep_van_commercial_vehicle_reg_in_district,lcv_single_journey,lcv_return_journey,lcv_monthly_pass,lcv_commercial_vehicle_reg_in_district,bus_truck_single_journey,bus_truck_return_journey,bus_truck_monthly_pass,bus_truck_commercial_vehicle_reg_in_district,upto_3_axle_vehicle_single_journey,upto_3_axle_vehicle_return_journey,upto_3_axle_vehicle_monthly_pass,upto_3_axle_vehicle_commercial_vehicle_rreg_in_district,_4_to_6_axle_single_journey,_4_to_6_axle_return_journey,_4_to_6_axle_monthly_pass,_4_to_6_axle_commercial_vehicle_reg_in_district,hcm_eme_single_journey,hcm_eme_return_journey,hcm_eme_monthly_pass,hcm_eme_commercial_vehicle_reg_in_district,_7_or_more_axle_single_journey,_7_or_more_axle_return_journey,_7_or_more_axle_monthly_pass,_7_or_more_axle_commercial_reg_in_district)
FROM '/docker-entrypoint-initdb.d/toll_plaza_data.csv'
DELIMITER ','
CSV HEADER;

ALTER TABLE toll_plaza
ADD COLUMN location GEOMETRY(Point, 4326);

UPDATE toll_plaza
SET location = ST_SetSRID(ST_MakePoint(longitude::DOUBLE PRECISION,latitude::DOUBLE PRECISION ),4326);


------------------------------------------







