-- ==========================
-- Hotel Management System
-- ==========================

-- 1️⃣ RoomType table
CREATE TABLE IF NOT EXISTS RoomType (
    RoomTypeID SERIAL PRIMARY KEY,
    TypeName VARCHAR(50) NOT NULL,
    PricePerNight NUMERIC(10,2) NOT NULL,
    Capacity INT NOT NULL
);

-- 2️⃣ Room table
CREATE TABLE IF NOT EXISTS Room (
    RoomID SERIAL PRIMARY KEY,
    RoomTypeID INT NOT NULL REFERENCES RoomType(RoomTypeID),
    Status VARCHAR(20) DEFAULT 'Available',
    Floor INT,
    Description TEXT
);

-- 3️⃣ Guest table
CREATE TABLE IF NOT EXISTS Guest (
    GuestID SERIAL PRIMARY KEY,
    FullName VARCHAR(100) NOT NULL,
    Phone VARCHAR(20),
    Email VARCHAR(100),
    NationalID VARCHAR(20)
);

-- 4️⃣ Booking table
CREATE TABLE IF NOT EXISTS Booking (
    BookingID SERIAL PRIMARY KEY,
    GuestID INT NOT NULL REFERENCES Guest(GuestID),
    RoomID INT NOT NULL REFERENCES Room(RoomID),
    CheckInDate DATE NOT NULL,
    CheckOutDate DATE NOT NULL,
    Status VARCHAR(20) DEFAULT 'Booked'
);

-- 5️⃣ Service table
CREATE TABLE IF NOT EXISTS Service (
    ServiceID SERIAL PRIMARY KEY,
    BookingID INT NOT NULL REFERENCES Booking(BookingID) ON DELETE CASCADE,
    Description VARCHAR(100) NOT NULL,
    Cost NUMERIC(10,2) NOT NULL,
    StaffID INT
);

-- 6️⃣ Payment table
CREATE TABLE IF NOT EXISTS Payment (
    PaymentID SERIAL PRIMARY KEY,
    BookingID INT NOT NULL REFERENCES Booking(BookingID) ON DELETE CASCADE,
    Amount NUMERIC(10,2) NOT NULL,
    PaymentDate DATE NOT NULL,
    Method VARCHAR(50)
);



-- Insert sample RoomTypes
INSERT INTO RoomType (TypeName, PricePerNight, Capacity)
VALUES
('Single', 50.00, 1),
('Double', 80.00, 2),
('Suite', 150.00, 4)
ON CONFLICT DO NOTHING;

-- Insert sample Rooms
INSERT INTO Room (RoomTypeID, Status, Floor, Description)
VALUES
(1, 'Available', 1, 'Single room 101'),
(1, 'Available', 1, 'Single room 102'),
(2, 'Available', 2, 'Double room 201'),
(2, 'Available', 2, 'Double room 202'),
(3, 'Available', 3, 'Suite room 301'),
(3, 'Available', 3, 'Suite room 302'),
(1, 'Available', 1, 'Single room 103'),
(2, 'Available', 2, 'Double room 203'),
(1, 'Available', 1, 'Single room 104'),
(2, 'Available', 2, 'Double room 204')
ON CONFLICT DO NOTHING;

-- Insert sample Guests
INSERT INTO Guest (FullName, Phone, Email, NationalID)
VALUES
('Jean Claude', '0788000001', 'jean@example.com', '10001'),
('Alice Mukamana', '0788000002', 'alice@example.com', '10002'),
('Eric Nsengiyumva', '0788000003', 'eric@example.com', '10003'),
('Marie Uwase', '0788000004', 'marie@example.com', '10004'),
('David Habimana', '0788000005', 'david@example.com', '10005')
ON CONFLICT DO NOTHING;

-- Insert sample Bookings
INSERT INTO Booking (GuestID, RoomID, CheckInDate, CheckOutDate, Status)
VALUES
(1, 1, '2025-10-25', '2025-10-28', 'Booked'),
(2, 3, '2025-10-26', '2025-10-30', 'Booked'),
(3, 5, '2025-10-27', '2025-10-29', 'Booked'),
(4, 2, '2025-10-28', '2025-10-31', 'Booked'),
(5, 4, '2025-10-29', '2025-11-02', 'Booked')
ON CONFLICT DO NOTHING;

-- Insert sample Services
INSERT INTO Service (BookingID, Description, Cost, StaffID)
VALUES
(1, 'Laundry', 15.00, 101),
(1, 'Breakfast', 20.00, 102),
(2, 'Lunch', 25.00, 103),
(3, 'Spa', 50.00, 104),
(4, 'Dinner', 30.00, 105)
ON CONFLICT DO NOTHING;

-- Insert sample Payments
INSERT INTO Payment (BookingID, Amount, PaymentDate, Method)
VALUES
(1, 185.00, '2025-10-28', 'Credit Card'),
(2, 205.00, '2025-10-30', 'Cash'),
(3, 200.00, '2025-10-29', 'Credit Card'),
(4, 110.00, '2025-10-31', 'Mobile Money'),
(5, 150.00, '2025-11-02', 'Cash')
ON CONFLICT DO NOTHING;



SELECT b.BookingID, g.FullName, rt.TypeName, rt.PricePerNight + COALESCE(SUM(s.Cost),0) AS TotalCost
FROM Booking b
JOIN Guest g ON b.GuestID = g.GuestID
JOIN Room r ON b.RoomID = r.RoomID
JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
LEFT JOIN Service s ON b.BookingID = s.BookingID
GROUP BY b.BookingID, g.FullName, rt.TypeName, rt.PricePerNight;



UPDATE Room r
SET Status = 'Available'
FROM Booking b
WHERE r.RoomID = b.RoomID
  AND b.CheckOutDate < CURRENT_DATE
  AND r.Status <> 'Available';



SELECT DISTINCT g.FullName, s.Description, s.Cost
FROM Service s
JOIN Booking b ON s.BookingID = b.BookingID
JOIN Guest g ON b.GuestID = g.GuestID
WHERE s.Cost > 30;

CREATE OR REPLACE VIEW HotelRevenuePerMonth AS
SELECT DATE_TRUNC('month', PaymentDate) AS Month,
       SUM(Amount) AS TotalRevenue
FROM Payment
GROUP BY DATE_TRUNC('month', PaymentDate)
ORDER BY Month;

-- Function
CREATE OR REPLACE FUNCTION prevent_overlap()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM Booking
        WHERE RoomID = NEW.RoomID
          AND NEW.CheckInDate < CheckOutDate
          AND NEW.CheckOutDate > CheckInDate
    ) THEN
        RAISE EXCEPTION 'Room % is already booked for these dates.', NEW.RoomID;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
CREATE TRIGGER trg_prevent_overlap
BEFORE INSERT OR UPDATE ON Booking
FOR EACH ROW EXECUTE FUNCTION prevent_overlap();



-- This will work (no overlap)
INSERT INTO Booking (GuestID, RoomID, CheckInDate, CheckOutDate, Status)
VALUES (1, 1, '2025-11-01', '2025-11-05', 'Booked');

-- This will fail (overlaps with previous booking)
INSERT INTO Booking (GuestID, RoomID, CheckInDate, CheckOutDate, Status)
VALUES (2, 1, '2025-11-03', '2025-11-06', 'Booked');







