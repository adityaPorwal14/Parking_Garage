import math
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Set


class VehicleType(Enum):
    COMPACT = "COMPACT"
    STANDARD = "STANDARD"
    EV = "EV"


class SpotType(Enum):
    COMPACT = "COMPACT"
    STANDARD = "STANDARD"
    EV = "EV"


@dataclass
class RateConfig:
    first_hour_rate: float
    additional_hour_rate: float
    daily_cap: float


class ParkingSpot:
    def __init__(self, spot_id: str, level: int, spot_type: SpotType):
        self.spot_id = spot_id
        self.level = level
        self.spot_type = spot_type
        self.is_occupied = False
        self.occupying_plate: Optional[str] = None

    def occupy(self, plate: str):
        self.is_occupied = True
        self.occupying_plate = plate

    def vacate(self):
        self.is_occupied = False
        self.occupying_plate = None


@dataclass
class Ticket:
    ticket_id: str
    plate: str
    vehicle_type: VehicleType
    spot_id: str
    entry_time: datetime
    exit_time: Optional[datetime] = None
    fee: Optional[float] = None


class ParkingGarage:
    def __init__(self, name: str, rate_config: RateConfig):
        self.name = name
        self.rate_config = rate_config
        self.spots: Dict[str, ParkingSpot] = {}
        self.available_spots: Dict[SpotType, Set[str]] = {
            SpotType.COMPACT: set(),
            SpotType.STANDARD: set(),
            SpotType.EV: set(),
        }
        self.active_tickets_by_plate: Dict[str, Ticket] = {}
        self.completed_tickets: List[Ticket] = []
        self._ticket_counter = 0

    def add_spot(self, spot_id: str, level: int, spot_type: SpotType):
        spot = ParkingSpot(spot_id, level, spot_type)
        self.spots[spot_id] = spot
        self.available_spots[spot_type].add(spot_id)

    def count_available_spots(self, spot_type: SpotType) -> int:
        return len(self.available_spots[spot_type])

    def lookup_vehicle(self, plate: str) -> Optional[Ticket]:
        return self.active_tickets_by_plate.get(plate.upper().strip())

    def _find_suitable_spot(self, vehicle_type: VehicleType) -> Optional[ParkingSpot]:
        if vehicle_type == VehicleType.EV:
            allowed = [SpotType.EV]
        elif vehicle_type == VehicleType.COMPACT:
            allowed = [SpotType.COMPACT, SpotType.STANDARD]
        else:
            allowed = [SpotType.STANDARD]

        for s_type in allowed:
            if self.available_spots[s_type]:
                spot_id = next(iter(self.available_spots[s_type]))
                return self.spots[spot_id]
        return None

    def check_in(self, plate: str, vehicle_type: VehicleType, entry_time: Optional[datetime] = None) -> Ticket:
        plate = plate.upper().strip()
        if plate in self.active_tickets_by_plate:
            raise ValueError(f"Vehicle '{plate}' is already inside the garage!")

        spot = self._find_suitable_spot(vehicle_type)
        if not spot:
            raise RuntimeError(f"Garage Full: No spot available for vehicle type '{vehicle_type.value}'.")

        entry_time = entry_time or datetime.now()
        spot.occupy(plate)
        self.available_spots[spot.spot_type].remove(spot.spot_id)

        self._ticket_counter += 1
        ticket = Ticket(
            ticket_id=f"TICK-{self._ticket_counter:04d}",
            plate=plate,
            vehicle_type=vehicle_type,
            spot_id=spot.spot_id,
            entry_time=entry_time,
        )
        self.active_tickets_by_plate[plate] = ticket
        return ticket

    def calculate_fee(self, entry_time: datetime, exit_time: datetime) -> float:
        if exit_time < entry_time:
            raise ValueError("Exit time cannot precede entry time.")

        duration_seconds = (exit_time - entry_time).total_seconds()
        if duration_seconds <= 0:
            return 0.0

        total_hours = math.ceil(duration_seconds / 3600.0)
        full_days = total_hours // 24
        remaining_hours = total_hours % 24

        total_fee = full_days * self.rate_config.daily_cap
        if remaining_hours > 0:
            uncapped = self.rate_config.first_hour_rate + (remaining_hours - 1) * self.rate_config.additional_hour_rate
            total_fee += min(uncapped, self.rate_config.daily_cap)

        return round(total_fee, 2)

    def check_out(self, plate: str, exit_time: Optional[datetime] = None) -> Ticket:
        plate = plate.upper().strip()
        ticket = self.active_tickets_by_plate.get(plate)
        if not ticket:
            raise KeyError(f"Vehicle '{plate}' not found in the garage.")

        exit_time = exit_time or datetime.now()
        ticket.fee = self.calculate_fee(ticket.entry_time, exit_time)
        ticket.exit_time = exit_time

        spot = self.spots[ticket.spot_id]
        spot.vacate()
        self.available_spots[spot.spot_type].add(spot.spot_id)

        del self.active_tickets_by_plate[plate]
        self.completed_tickets.append(ticket)
        return ticket


def run_attendant_terminal():
    # Setup garage with configurable rate structure
    rates = RateConfig(first_hour_rate=10.0, additional_hour_rate=5.0, daily_cap=35.0)
    garage = ParkingGarage("City Center Multi-Level Garage", rates)

    # Initialize layout
    garage.add_spot("L1-EV1", 1, SpotType.EV)
    garage.add_spot("L1-EV2", 1, SpotType.EV)
    garage.add_spot("L1-C1", 1, SpotType.COMPACT)
    garage.add_spot("L2-S1", 2, SpotType.STANDARD)
    garage.add_spot("L2-S2", 2, SpotType.STANDARD)

    while True:
        print("\n==========================================")
        print("     GARAGE ATTENDANT TERMINAL            ")
        print("==========================================")
        print("1. Check In Vehicle")
        print("2. Check Out Vehicle")
        print("3. Spot Availability Query (e.g. EV spots)")
        print("4. Find Vehicle Location by License Plate")
        print("5. View Garage Occupancy Dashboard")
        print("6. Exit")

        choice = input("\nSelect Option (1-6): ").strip()

        if choice == "1":
            plate = input("Enter License Plate: ").strip()
            if not plate:
                print(">> Error: Plate cannot be empty.")
                continue

            print("Vehicle Types: [1] COMPACT  [2] STANDARD  [3] EV")
            v_choice = input("Select Vehicle Type (1-3): ").strip()
            type_map = {"1": VehicleType.COMPACT, "2": VehicleType.STANDARD, "3": VehicleType.EV}
            v_type = type_map.get(v_choice)

            if not v_type:
                print(">> Error: Invalid vehicle type selection.")
                continue

            # Optional simulated historical entry time
            hours_ago = input("Hours ago vehicle entered (press ENTER for right now): ").strip()
            entry_time = datetime.now()
            if hours_ago:
                try:
                    entry_time -= timedelta(hours=float(hours_ago))
                except ValueError:
                    print(">> Invalid hours format. Defaulting to now.")

            try:
                ticket = garage.check_in(plate, v_type, entry_time)
                print(f"\n[SUCCESS] Check-In Completed!")
                print(f" Ticket ID : {ticket.ticket_id}")
                print(f" Plate     : {ticket.plate}")
                print(f" Assigned  : Spot {ticket.spot_id}")
                print(f" Entry     : {ticket.entry_time.strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as e:
                print(f"\n[ERROR] {e}")

        elif choice == "2":
            plate = input("Enter License Plate to Check Out: ").strip()
            try:
                ticket = garage.check_out(plate, datetime.now())
                duration = ticket.exit_time - ticket.entry_time
                hrs = math.ceil(duration.total_seconds() / 3600.0)

                print(f"\n[SUCCESS] Check-Out Completed!")
                print(f" Ticket ID   : {ticket.ticket_id}")
                print(f" Plate       : {ticket.plate}")
                print(f" Spot Freed  : {ticket.spot_id}")
                print(f" Time Stayed : {duration.seconds // 3600}h {(duration.seconds % 3600) // 60}m (Billed for {hrs}h)")
                print(f" TOTAL FEE   : ${ticket.fee:.2f}")
            except Exception as e:
                print(f"\n[ERROR] {e}")

        elif choice == "3":
            print("\n--- SPOT AVAILABILITY ---")
            print(f" EV Spots Free       : {garage.count_available_spots(SpotType.EV)}")
            print(f" Compact Spots Free  : {garage.count_available_spots(SpotType.COMPACT)}")
            print(f" Standard Spots Free : {garage.count_available_spots(SpotType.STANDARD)}")

        elif choice == "4":
            plate = input("Enter License Plate to search: ").strip()
            ticket = garage.lookup_vehicle(plate)
            if ticket:
                print(f"\n[FOUND] Vehicle Details:")
                print(f" Plate    : {ticket.plate}")
                print(f" Location : Spot {ticket.spot_id} (Level {garage.spots[ticket.spot_id].level})")
                print(f" Entered  : {ticket.entry_time.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"\n[NOT FOUND] No active session for plate '{plate.upper()}'.")

        elif choice == "5":
            print("\n--- LIVE GARAGE DASHBOARD ---")
            for spot_id, spot in sorted(garage.spots.items()):
                status = f"OCCUPIED by [{spot.occupying_plate}]" if spot.is_occupied else "AVAILABLE"
                print(f" Spot {spot.spot_id:<7} | Level {spot.level} | Type: {spot.spot_type.value:<8} | {status}")

        elif choice == "6":
            print("\nShutting down attendant system. Goodbye!")
            break
        else:
            print("\n>> Invalid option. Please select 1 through 6.")


if __name__ == "__main__":
    run_attendant_terminal()
