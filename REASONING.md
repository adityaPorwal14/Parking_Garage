# 🧠 Engineering Reasoning & Technical Decisions

This document outlines the architectural choices, algorithm design, trade-offs, and testing methodology used to build the Parking Garage Management System.

---

## 1. Problem Decomposition & Objectives

The problem presents four main technical challenges:
1. **$O(1)$ Scalability**: Lookups by plate number must remain instantaneous even when the evening log grows to tens of thousands of records.
2. **Flexible & Fair Billing**: Tiered rates (first hour vs. additional hours), ceiling rounding for partial hours, and rolling 24-hour daily caps.
3. **Strict Constraints**: EV vehicles must strictly park in EV charger spots.
4. **Concurrency**: Multi-gate entries and exits must not cause race conditions or double-parking.

---

## 2. Key Architectural Decisions

### Data Structure Selection
* **Active Tickets Index (`Dict[str, Ticket]`)**: Stores active parkers indexed by their normalized license plate. Yields **$O(1)$ time complexity** for lookups and check-outs.
* **Available Spot Index (`Dict[SpotType, Set[str]]`)**: Maintains free spot IDs grouped by spot type in Hash Sets. 
  * Checking availability (`count_available_spots`) runs in **$O(1)$** via `len()`.
  * Assigning a spot takes **$O(1)$** by extracting an arbitrary ID from the set.

### Strategy Pattern for Pricing
Pricing logic is decoupled into a configurable rate structure. This ensures that changing the rate model (e.g., adding weekend rates or special holiday surge pricing) requires no changes to the core garage state machine.

### Thread Safety (`threading.RLock`)
A city-centre garage has multiple entry and exit gates operating concurrently. Mutating operations (`check_in`, `check_out`) are protected using Python's re-entrant lock (`RLock`), preventing two cars at different gates from claiming the same spot simultaneously.

---

## 3. Core Algorithm Logic

### Fee Calculation Strategy
```text
Total Hours = ceil(Total Seconds / 3600)
Full Days   = Total Hours // 24
Rem Hours   = Total Hours % 24

Partial Day Fee = First Hour Rate + (Rem Hours - 1) * Additional Hour Rate
Final Fee       = (Full Days * Daily Cap) + min(Partial Day Fee, Daily Cap)
