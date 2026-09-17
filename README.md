# 🅿️ Multi-Level City-Centre Parking Garage Management System

A high-performance, thread-safe backend system designed for garage attendants to manage real-time vehicle check-ins, check-outs, tiered fee calculations, EV charger enforcement, and sub-millisecond license plate lookups.

---

## 🚀 Features

- **Tiered & Capped Fee Engine**: Automatically handles first-hour rates, cheaper additional hour rates, part-hour ceiling rounding, and rolling 24-hour daily caps.
- **Strict Spot Assignment**: Guarantees EVs receive EV charger spots, with automatic fallback mapping for Compact and Standard vehicles.
- **$O(1)$ High-Speed Lookups**: In-memory Hash Maps and Sets ensure instant plate location lookups and availability checks even with thousands of active logs.
- **Concurrency & Race Condition Prevention**: Utilizes re-entrant thread locks (`RLock`) to safely handle simultaneous multi-gate check-ins and check-outs.
- **Interactive Terminal & API Ready**: Includes both a local CLI attendant interface and standard REST API contracts.

---

## 🛠️ Tech Stack & Requirements

- **Language**: Python 3.10+
- **Testing Framework**: `pytest`
- **Dependencies**: Zero external dependencies for core logic (uses standard libraries `datetime`, `math`, `typing`, `dataclasses`, `threading`).

---

## ⚙️ Setup & Installation

1. Clone the Repository
```bash
git clone [https://github.com/adityaPorwal14/Parking_Garage]

---

2. Setup Environment

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

# Install test dependencies
pip install pytest

3. Execution
Run the attendant terminal interface:
python main.py

4. Testing & Debugging
# Run all tests
pytest -v

5. API Endpoint Specifications
Endpoint,Method,Description,Request Body / Params
/api/v1/garage/check-in,POST,Assigns spot & issues ticket,"{""plate"": ""EV-101"", ""vehicle_type"": ""EV""}"
/api/v1/garage/check-out,POST,Vacates spot & calculates fee,"{""plate"": ""EV-101""}"
/api/v1/garage/availability,GET,Returns free spot count,?type=EV (optional)
/api/v1/garage/vehicles/{plate},GET,O(1) active plate lookup,URL Parameter
/api/v1/garage/dashboard,GET,Returns full layout status,None
