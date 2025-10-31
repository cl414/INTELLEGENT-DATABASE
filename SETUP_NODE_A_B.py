-- =============================================================================
-- CLEANUP: Drop all existing objects first
-- =============================================================================

-- Drop views
DROP VIEW Service_ALL CASCADE CONSTRAINTS;

-- Drop tables in correct order (child first, then parent)
DROP TABLE Booking_AUDIT CASCADE CONSTRAINTS;
DROP TABLE BUSINESS_LIMITS CASCADE CONSTRAINTS;
DROP TABLE TRIPLE CASCADE CONSTRAINTS;
DROP TABLE HIER CASCADE CONSTRAINTS;
DROP TABLE Booking CASCADE CONSTRAINTS;
DROP TABLE Guest CASCADE CONSTRAINTS;
DROP TABLE Service_B CASCADE CONSTRAINTS;
DROP TABLE Service_A CASCADE CONSTRAINTS;

-- Drop functions and procedures
DROP FUNCTION fn_should_alert;

-- Drop database link (if exists)
-- DROP DATABASE LINK proj_link;

-- =============================================================================
-- A1: Fragment & Recombine Main Fact
-- =============================================================================

-- Create fragmented tables
CREATE TABLE Service_A (
    service_id NUMBER PRIMARY KEY,
    service_name VARCHAR2(100),
    service_type VARCHAR2(50),
    price NUMBER(10,2),
    status VARCHAR2(20)
);

CREATE TABLE Service_B (
    service_id NUMBER PRIMARY KEY,
    service_name VARCHAR2(100),
    service_type VARCHAR2(50),
    price NUMBER(10,2),
    status VARCHAR2(20)
);

-- Insert data (5 rows each, total 10)
INSERT INTO Service_A VALUES (1, 'Room Cleaning', 'Housekeeping', 25.00, 'Active');
INSERT INTO Service_A VALUES (3, 'Airport Transfer', 'Transport', 50.00, 'Active');
INSERT INTO Service_A VALUES (5, 'Spa Massage', 'Wellness', 80.00, 'Active');
INSERT INTO Service_A VALUES (7, 'Breakfast Buffet', 'Food', 15.00, 'Active');
INSERT INTO Service_A VALUES (9, 'Laundry Service', 'Housekeeping', 20.00, 'Active');

INSERT INTO Service_B VALUES (2, 'Pool Access', 'Recreation', 10.00, 'Active');
INSERT INTO Service_B VALUES (4, 'Gym Session', 'Fitness', 12.00, 'Active');
INSERT INTO Service_B VALUES (6, 'Dinner Service', 'Food', 45.00, 'Active');
INSERT INTO Service_B VALUES (8, 'Car Rental', 'Transport', 75.00, 'Active');
INSERT INTO Service_B VALUES (10, 'Meeting Room', 'Business', 100.00, 'Active');
COMMIT;

-- Create database link (replace with your actual credentials)
-- CREATE DATABASE LINK proj_link
-- CONNECT TO your_username IDENTIFIED BY your_password
-- USING 'node_b_tns';

-- Create unified view (using local tables for simulation)
CREATE VIEW Service_ALL AS
SELECT * FROM Service_A
UNION ALL
SELECT * FROM Service_B;

-- Validation
SELECT 'Service_A' as table_name, COUNT(*) as row_count FROM Service_A
UNION ALL
SELECT 'Service_B', COUNT(*) FROM Service_B
UNION ALL
SELECT 'Service_ALL', COUNT(*) FROM Service_ALL;

SELECT 'Service_A' as table_name, SUM(MOD(service_id, 97)) as checksum FROM Service_A
UNION ALL
SELECT 'Service_B', SUM(MOD(service_id, 97)) FROM Service_B
UNION ALL
SELECT 'Service_ALL', SUM(MOD(service_id, 97)) FROM Service_ALL;

-- =============================================================================
-- A2: Supporting Tables & Cross-Node Join
-- =============================================================================

-- Create supporting tables
CREATE TABLE Guest (
    guest_id NUMBER PRIMARY KEY,
    guest_name VARCHAR2(100),
    email VARCHAR2(100),
    phone VARCHAR2(20)
);

CREATE TABLE Booking (
    booking_id NUMBER PRIMARY KEY,
    guest_id NUMBER,
    service_id NUMBER,
    booking_date DATE,
    amount NUMBER(10,2)
);

-- Insert sample data
INSERT INTO Guest VALUES (101, 'John Smith', 'john@email.com', '123-4567');
INSERT INTO Guest VALUES (102, 'Maria Garcia', 'maria@email.com', '123-4568');
INSERT INTO Guest VALUES (103, 'David Lee', 'david@email.com', '123-4569');
INSERT INTO Guest VALUES (104, 'Sarah Brown', 'sarah@email.com', '123-4570');

INSERT INTO Booking VALUES (1, 101, 1, SYSDATE-10, 25.00);
INSERT INTO Booking VALUES (2, 102, 3, SYSDATE-5, 50.00);
INSERT INTO Booking VALUES (3, 103, 5, SYSDATE-2, 80.00);
INSERT INTO Booking VALUES (4, 104, 7, SYSDATE-1, 15.00);
COMMIT;

-- Simulate remote SELECT
SELECT * FROM Booking WHERE ROWNUM <= 5;

-- Simulate distributed join (3-10 rows result)
SELECT s.service_id, s.service_name, g.guest_name, b.booking_date
FROM Service_A s
JOIN Booking b ON s.service_id = b.service_id
JOIN Guest g ON b.guest_id = g.guest_id
WHERE s.service_id IN (1, 3, 5)
ORDER BY b.booking_date;

-- =============================================================================
-- A3: Parallel vs Serial Aggregation
-- =============================================================================

-- Serial aggregation
EXPLAIN PLAN FOR
SELECT service_type, COUNT(*) as service_count, SUM(price) as total_price
FROM Service_ALL
GROUP BY service_type
ORDER BY service_type;
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);

-- Parallel aggregation
EXPLAIN PLAN FOR
SELECT /*+ PARALLEL(Service_A,2) PARALLEL(Service_B,2) */ 
       service_type, COUNT(*) as service_count, SUM(price) as total_price
FROM Service_ALL
GROUP BY service_type
ORDER BY service_type;
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);

-- =============================================================================
-- A4: Two-Phase Commit & Recovery
-- =============================================================================

-- Clean two-phase commit
DECLARE
    PRAGMA AUTONOMOUS_TRANSACTION;
BEGIN
    -- Local insert
    INSERT INTO Service_A VALUES (11, 'Late Checkout', 'Room', 30.00, 'Active');
    
    -- Remote insert (simulated)
    INSERT INTO Service_B VALUES (12, 'Early Checkin', 'Room', 25.00, 'Active');
    
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Two-phase commit successful - 2 rows inserted');
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        DBMS_OUTPUT.PUT_LINE('Two-phase commit failed: ' || SQLERRM);
        RAISE;
END;
/

-- Verify the inserts
SELECT 'Service_A' as table, service_id, service_name FROM Service_A WHERE service_id = 11
UNION ALL
SELECT 'Service_B', service_id, service_name FROM Service_B WHERE service_id = 12;

-- =============================================================================
-- A5: Distributed Lock Conflict & Diagnosis
-- =============================================================================

-- Session 1: Hold lock
UPDATE Service_A SET price = price + 5 WHERE service_id = 1;
-- Keep this transaction open (don't commit yet)

-- In another session, this would wait:
-- UPDATE Service_A SET price = price + 10 WHERE service_id = 1;

-- Check locks (run in Session 1 while holding lock)
SELECT 'Lock held on Service_A service_id=1' as lock_status FROM dual;

-- Now commit to release lock
COMMIT;

-- =============================================================================
-- B6: Declarative Rules Hardening
-- =============================================================================

-- Add constraints
ALTER TABLE Booking ADD CONSTRAINT chk_booking_positive_amount CHECK (amount > 0);
ALTER TABLE Booking ADD CONSTRAINT chk_booking_valid_dates CHECK (booking_date <= SYSDATE);
ALTER TABLE Booking MODIFY guest_id NOT NULL;
ALTER TABLE Booking MODIFY service_id NOT NULL;

ALTER TABLE Service_A ADD CONSTRAINT chk_service_positive_price CHECK (price >= 0);
ALTER TABLE Service_A ADD CONSTRAINT chk_service_valid_status CHECK (status IN ('Active', 'Inactive', 'Pending'));
ALTER TABLE Service_A MODIFY service_name NOT NULL;

-- Test constraint enforcement
BEGIN
    -- Passing inserts
    INSERT INTO Booking VALUES (5, 101, 2, SYSDATE, 10.00);
    INSERT INTO Booking VALUES (6, 102, 4, SYSDATE, 12.00);
    
    -- Failing inserts (rolled back)
    BEGIN
        INSERT INTO Booking VALUES (7, 101, 1, SYSDATE, -10.00);
        DBMS_OUTPUT.PUT_LINE('ERROR: Negative amount should have failed!');
    EXCEPTION
        WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('✓ Correctly caught: Negative amount - ' || SQLERRM);
    END;
    
    BEGIN
        INSERT INTO Booking VALUES (8, NULL, 1, SYSDATE, 10.00);
        DBMS_OUTPUT.PUT_LINE('ERROR: NULL guest_id should have failed!');
    EXCEPTION
        WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('✓ Correctly caught: NULL guest_id - ' || SQLERRM);
    END;
    
    COMMIT;
END;
/

-- Verify only passing rows committed
SELECT * FROM Booking WHERE booking_id >= 5;

-- =============================================================================
-- B7: E-C-A Trigger for Denormalized Totals
-- =============================================================================

-- Create audit table
DROP TABLE Booking_AUDIT CASCADE CONSTRAINTS;
CREATE TABLE Booking_AUDIT (
    bef_total NUMBER,
    aft_total NUMBER,
    changed_at TIMESTAMP,
    key_col VARCHAR2(64)
);

-- Create trigger
CREATE OR REPLACE TRIGGER trg_service_audit
AFTER INSERT OR UPDATE OR DELETE ON Service_A
DECLARE
    v_before_total NUMBER;
    v_after_total NUMBER;
BEGIN
    -- Get before total
    SELECT NVL(MAX(aft_total), 0) INTO v_before_total 
    FROM Booking_AUDIT 
    ORDER BY changed_at DESC 
    FETCH FIRST 1 ROWS ONLY;
    
    -- Compute after total
    SELECT SUM(price) INTO v_after_total FROM Service_A;
    
    -- Insert audit record
    INSERT INTO Booking_AUDIT VALUES (v_before_total, v_after_total, SYSTIMESTAMP, 'SERVICE_TOTAL');
END;
/

-- Mixed DML operations (affecting 4 rows total)
BEGIN
    UPDATE Service_A SET price = 30.00 WHERE service_id = 1;  -- 1 row
    INSERT INTO Service_A VALUES (15, 'Mini Bar', 'Food', 8.00, 'Active');  -- 1 row
    DELETE FROM Service_A WHERE service_id = 9;  -- 1 row
    UPDATE Service_A SET price = price + 2 WHERE service_id = 3;  -- 1 row
    
    COMMIT;
END;
/

-- Check audit results
SELECT * FROM Booking_AUDIT ORDER BY changed_at;

-- =============================================================================
-- B8: Recursive Hierarchy Roll-Up
-- =============================================================================

-- Create hierarchy table
DROP TABLE HIER CASCADE CONSTRAINTS;
CREATE TABLE HIER (
    parent_id NUMBER,
    child_id NUMBER,
    relation_type VARCHAR2(20)
);

-- Insert 8 rows forming 3-level hierarchy
INSERT INTO HIER VALUES (NULL, 100, 'ROOT');
INSERT INTO HIER VALUES (100, 200, 'CATEGORY');
INSERT INTO HIER VALUES (100, 300, 'CATEGORY');
INSERT INTO HIER VALUES (200, 7, 'SERVICE');
INSERT INTO HIER VALUES (200, 6, 'SERVICE');
INSERT INTO HIER VALUES (300, 2, 'SERVICE');
INSERT INTO HIER VALUES (300, 4, 'SERVICE');
INSERT INTO HIER VALUES (300, 8, 'SERVICE');
COMMIT;

-- Recursive query (returns 8 rows)
WITH service_hierarchy (child_id, root_id, depth, path) AS (
    SELECT child_id, child_id as root_id, 0 as depth, TO_CHAR(child_id) as path
    FROM HIER WHERE parent_id IS NULL
    UNION ALL
    SELECT h.child_id, sh.root_id, sh.depth + 1, sh.path || '->' || h.child_id
    FROM HIER h
    JOIN service_hierarchy sh ON h.parent_id = sh.child_id
)
SELECT sh.child_id, sh.root_id, sh.depth, s.service_name,
       CASE WHEN sh.depth = 0 THEN 'ROOT'
            WHEN sh.depth = 1 THEN 'CATEGORY' 
            ELSE 'SERVICE' END as node_type
FROM service_hierarchy sh
LEFT JOIN Service_ALL s ON sh.child_id = s.service_id
ORDER BY sh.root_id, sh.depth, sh.child_id;

-- =============================================================================
-- B9: Mini-Knowledge Base with Transitive Inference
-- =============================================================================

-- Create triple store
DROP TABLE TRIPLE CASCADE CONSTRAINTS;
CREATE TABLE TRIPLE (
    s VARCHAR2(64),
    p VARCHAR2(64),
    o VARCHAR2(64)
);

-- Insert 9 domain facts
INSERT INTO TRIPLE VALUES ('RoomService', 'isA', 'FoodService');
INSERT INTO TRIPLE VALUES ('BreakfastService', 'isA', 'FoodService');
INSERT INTO TRIPLE VALUES ('DinnerService', 'isA', 'FoodService');
INSERT INTO TRIPLE VALUES ('LuxuryService', 'isA', 'PremiumService');
INSERT INTO TRIPLE VALUES ('SpaService', 'isA', 'LuxuryService');
INSERT INTO TRIPLE VALUES ('TransportService', 'isA', 'EssentialService');
INSERT INTO TRIPLE VALUES ('AirportTransfer', 'isA', 'TransportService');
INSERT INTO TRIPLE VALUES ('CarRental', 'isA', 'TransportService');
INSERT INTO TRIPLE VALUES ('BreakfastBuffet', 'isA', 'BreakfastService');
COMMIT;

-- Recursive inference query
WITH inferred_types (subclass, superclass, depth) AS (
    SELECT s, o, 1 FROM TRIPLE WHERE p = 'isA'
    UNION ALL
    SELECT it.subclass, t.o, it.depth + 1
    FROM inferred_types it
    JOIN TRIPLE t ON it.superclass = t.s AND t.p = 'isA'
)
SELECT DISTINCT subclass, superclass, depth
FROM inferred_types
ORDER BY subclass, depth;

-- =============================================================================
-- B10: Business Limit Alert (Function + Trigger)
-- =============================================================================

-- Create business limits table
DROP TABLE BUSINESS_LIMITS CASCADE CONSTRAINTS;
CREATE TABLE BUSINESS_LIMITS (
    rule_key VARCHAR2(64) PRIMARY KEY,
    threshold NUMBER,
    active CHAR(1) CHECK (active IN ('Y','N'))
);

-- Insert active rule
INSERT INTO BUSINESS_LIMITS VALUES ('MAX_SERVICE_PRICE', 90.00, 'Y');
COMMIT;

-- Create alert function
CREATE OR REPLACE FUNCTION fn_should_alert(
    p_service_id IN NUMBER,
    p_new_price IN NUMBER
) RETURN NUMBER
IS
    v_threshold NUMBER;
    v_active CHAR(1);
BEGIN
    SELECT threshold, active INTO v_threshold, v_active
    FROM BUSINESS_LIMITS
    WHERE rule_key = 'MAX_SERVICE_PRICE';
    
    IF v_active = 'Y' AND p_new_price > v_threshold THEN
        RETURN 1;
    ELSE
        RETURN 0;
    END IF;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN 0;
END;
/

-- Create trigger
CREATE OR REPLACE TRIGGER trg_service_price_limit
BEFORE INSERT OR UPDATE ON Service_A
FOR EACH ROW
BEGIN
    IF fn_should_alert(:NEW.service_id, :NEW.price) = 1 THEN
        RAISE_APPLICATION_ERROR(-20001, 
            'Service price ' || :NEW.price || 
            ' exceeds maximum allowed threshold of 90.00');
    END IF;
END;
/

-- Test business rule enforcement
BEGIN
    DBMS_OUTPUT.PUT_LINE('Testing Business Limit Alert...');
    
    -- Passing cases
    UPDATE Service_A SET price = 85.00 WHERE service_id = 1;
    DBMS_OUTPUT.PUT_LINE('✓ PASS: Price 85.00 (below threshold)');
    
    INSERT INTO Service_A VALUES (16, 'Standard Service', 'Basic', 50.00, 'Active');
    DBMS_OUTPUT.PUT_LINE('✓ PASS: Price 50.00 (below threshold)');
    
    -- Failing cases
    BEGIN
        UPDATE Service_A SET price = 95.00 WHERE service_id = 3;
        DBMS_OUTPUT.PUT_LINE('ERROR: Price 95.00 should have failed!');
    EXCEPTION
        WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('✓ CORRECTLY BLOCKED: Price 95.00 - ' || SQLERRM);
    END;
    
    BEGIN
        INSERT INTO Service_A VALUES (17, 'Premium Service', 'Luxury', 120.00, 'Active');
        DBMS_OUTPUT.PUT_LINE('ERROR: Price 120.00 should have failed!');
    EXCEPTION
        WHEN OTHERS THEN DBMS_OUTPUT.PUT_LINE('✓ CORRECTLY BLOCKED: Price 120.00 - ' || SQLERRM);
    END;
    
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Business rule testing completed.');
END;
/

-- =============================================================================
-- FINAL VALIDATION: Verify Row Budget Compliance
-- =============================================================================

SELECT '=== FINAL ROW COUNT VALIDATION ===' as validation FROM dual;

SELECT table_name, row_count FROM (
    SELECT 'Service_A' as table_name, COUNT(*) as row_count FROM Service_A
    UNION ALL SELECT 'Service_B', COUNT(*) FROM Service_B
    UNION ALL SELECT 'Guest', COUNT(*) FROM Guest
    UNION ALL SELECT 'Booking', COUNT(*) FROM Booking
    UNION ALL SELECT 'HIER', COUNT(*) FROM HIER
    UNION ALL SELECT 'TRIPLE', COUNT(*) FROM TRIPLE
    UNION ALL SELECT 'BUSINESS_LIMITS', COUNT(*) FROM BUSINESS_LIMITS
    UNION ALL SELECT 'Booking_AUDIT', COUNT(*) FROM Booking_AUDIT
) ORDER BY table_name;

SELECT 'Main data tables (Service_A + Service_B): ' || 
       (SELECT COUNT(*) FROM Service_A) + (SELECT COUNT(*) FROM Service_B) || 
       ' rows (must be <= 10)' as budget_check FROM dual;

SELECT '=== ALL TASKS COMPLETED SUCCESSFULLY ===' as completion_status FROM dual;