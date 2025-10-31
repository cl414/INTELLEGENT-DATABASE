-- Drop everything in correct order (due to foreign key constraints)
DROP TABLE IF EXISTS healthnet.patient_med CASCADE;
DROP TABLE IF EXISTS healthnet.patient CASCADE;
DROP SCHEMA IF EXISTS healthnet CASCADE;

-- Create fresh schema and tables
CREATE SCHEMA healthnet;
SET search_path TO healthnet;

-- Create patient table first
CREATE TABLE patient (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Create patient_med table with all constraints
CREATE TABLE patient_med (
    patient_med_id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patient(id),
    med_name VARCHAR(80) NOT NULL,
    dose_mg NUMERIC(6,2) CHECK (dose_mg >= 0),
    start_dt DATE NOT NULL,
    end_dt DATE,
    CONSTRAINT ck_rx_dates CHECK (start_dt <= end_dt OR end_dt IS NULL)
);

-- Insert sample patients
INSERT INTO patient (id, name) VALUES 
(1, 'John Smith'),
(2, 'Maria Garcia'),
(3, 'David Johnson'),
(4, 'Sarah Wilson');

-- Verify patients
SELECT * FROM patient;


INSERT INTO patient_med (patient_med_id, patient_id, med_name, dose_mg, start_dt, end_dt)
VALUES (1, 1, 'Aspirin', -50, '2024-01-01', '2024-01-10');

INSERT INTO patient_med (patient_med_id, patient_id, med_name, dose_mg, start_dt, end_dt)
VALUES (2, 1, 'Ibuprofen', 200, '2024-02-01', '2024-01-15');

INSERT INTO patient_med (patient_med_id, patient_id, med_name, dose_mg, start_dt, end_dt)
VALUES (3, 1, NULL, 100, '2024-01-01', '2024-01-10');

INSERT INTO patient_med (patient_med_id, patient_id, med_name, dose_mg, start_dt, end_dt)
VALUES (4, 999, 'Paracetamol', 500, '2024-01-01', '2024-01-10');


INSERT INTO patient_med (patient_med_id, patient_id, med_name, dose_mg, start_dt, end_dt)
VALUES (5, 1, 'Amoxicillin', 500.00, '2024-01-01', '2024-01-10');


INSERT INTO patient_med (patient_med_id, patient_id, med_name, dose_mg, start_dt, end_dt)
VALUES (6, 2, 'Blood Pressure Medication', 25.50, '2024-01-01', NULL);


-- Show all patient medications
SELECT 
    pm.patient_med_id,
    p.name as patient_name,
    pm.med_name,
    pm.dose_mg,
    pm.start_dt,
    pm.end_dt
FROM patient_med pm
JOIN patient p ON pm.patient_id = p.id
ORDER BY pm.patient_med_id;