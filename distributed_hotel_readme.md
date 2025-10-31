# 🏨 Distributed Hotel Management Database System

## 📌 Project Overview
This project demonstrates a **distributed hotel management database system** using **Oracle SQL**.  
It simulates a real-world hotel service management scenario with:

- **Data fragmentation & recombination**  
- **Distributed transactions**  
- **Declarative constraints & triggers**  
- **Hierarchical data management**  
- **Business rule enforcement and audit tracking**

The system ensures **data integrity**, **business compliance**, and provides **audit trails**.

---

## ⚙️ Features

- **Fragmented Service Tables:** `Service_A` & `Service_B` simulate distributed data.  
- **Unified View:** `Service_ALL` combines fragmented tables for reporting.  
- **Guest & Booking Management:** Tracks guests and their bookings.  
- **Two-Phase Commit Simulation:** Ensures atomic operations across fragments.  
- **Distributed Lock Simulation:** Demonstrates concurrent transaction handling.  
- **Declarative Rules & Constraints:** Maintains data integrity.  
- **Audit Triggers:** Tracks changes in service totals via `Booking_AUDIT`.  
- **Recursive Hierarchy:** ROOT → CATEGORY → SERVICE management.  
- **Knowledge Base with Transitive Inference:** Implements `isA` relationships.  
- **Business Limit Enforcement:** Function + trigger enforce maximum service price.

---

## 🗂 Tables & Structures

### **Service Tables**
- `Service_A` and `Service_B` → Fragmented services  
- `Service_ALL` → Unified view  

### **Supporting Tables**
- `Guest` → Guest information  
- `Booking` → Records service bookings  
- `Booking_AUDIT` → Tracks total price changes  
- `HIER` → Stores hierarchical relationships  
- `TRIPLE` → Mini knowledge base for inference  
- `BUSINESS_LIMITS` → Stores business rules

---

## 💾 Sample Data

- **Services:** 10 services across `Service_A` & `Service_B`  
- **Guests:** 4 sample guests  
- **Bookings:** 4 bookings  
- **Business Limits:** Maximum service price = 90  

---

## 🛠 SQL Features Demonstrated

- **Fragmentation & recombination** using views  
- **Parallel vs serial aggregation queries**  
- **Two-phase commit & rollback handling**  
- **Distributed lock simulation**  
- **Declarative constraints & triggers**  
- **Recursive hierarchy queries**  
- **Transitive inference knowledge base**  
- **Business rule enforcement**

---

## 🏃 How to Run

1. **Clone the repository:**

```bash
git clone https://github.com/cl414/distributed-hotel-db.git
cd distributed-hotel-db
```

2. **Open the SQL script** in Oracle SQL Developer or SQL*Plus.  
3. **Run the script step by step**:
   - Drop existing objects (tables, views, functions)  
   - Create tables & insert sample data  
   - Create views, triggers, and functions  
   - Run validation queries & testing  
4. **Verify outputs** using the SELECT statements provided.  

---

## ✅ Validation Checks

- Row count validation for all tables and views  
- Checksum validation for services  
- Trigger & function tests for business rules  
- Audit log verification for service totals  

---

## 👤 Author
**Jean Claude Harerimana**  
Student at **ACE-DS**  
Tel: +250 783 606 210  
Email: hareraclaude18@gmail.com  

---

## 📄 License
This project is **open-source** and free to use for **educational purposes**.

