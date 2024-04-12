from datetime import datetime, timezone
from operator import attrgetter

from model.Bus import BusActivity, Bus, BusMovement
from model.Passenger import Passenger, PassengerRoute, PassengerOnboardStatus
from dataclasses import dataclass
from dataclasses_json import dataclass_json
import json

@dataclass_json
@dataclass
class BusAttendance:
    bus: Bus
    passengers: list[Passenger]

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.bus = Bus(plate_number='ABC123', bus_activities=[])
            cls._instance.passengers = []
        return cls._instance

    def add_and_update_passenger(self, passenger: Passenger):
        found, p = self.find_passenger(passenger)
        if not found:
            print("passenger not found")
            self.passengers.append(passenger)
        else:
            print("passenger found, update data")
            p.passenger_activities.append(PassengerRoute(
                passenger.passenger_activities[-1].location,
                passenger.passenger_activities[-1].passenger_status,
                "At {}, {} {} at {}".format(passenger.passenger_activities[-1].time,
                                            passenger.name,
                                            passenger.passenger_activities[-1].passenger_status.value,
                                            passenger.passenger_activities[-1].location),
                passenger.passenger_activities[-1].time
            ))

            p.passenger_activities = sorted(p.passenger_activities, key=attrgetter('time'))


    def remove_passenger(self, passenger: Passenger):
        if passenger in self.passengers:
            self.passengers.remove(passenger)

    def find_passenger(self, p: Passenger):
        p = next((passenger for passenger in self.passengers if passenger.name == p.name), Passenger("", "", []))
        return (
            p.name != "",
            p
        )

    @classmethod
    def from_json(cls, json_data):
        bus = Bus.from_json(json_data['bus'])
        passengers = [Passenger.from_json(p) for p in json_data['passengers']]
        cls._instance.bus = bus
        cls._instance.passengers = passengers
        return cls._instance

    def update_attendance_from_json(self, passenger_data_json):
        passenger_data = json.loads(passenger_data_json)
        self.bus.plate_number = passenger_data["data"][0]["bus_plate_number"]
        for p in passenger_data["data"]:
            loc =  self.bus.bus_activities[-1].location if len(self.bus.bus_activities) > 0 else ""
            if p["status"] == "exited":
                passerngerOnboardStatus = PassengerOnboardStatus.EXITING
            elif p["status"] == "entered":
                passerngerOnboardStatus = PassengerOnboardStatus.ENTERING
            else:
                passerngerOnboardStatus = PassengerOnboardStatus.BOARDING

            found_passenger = Passenger(
                name=p["name"],
                final_destination= p["intended_disembarkation_point"],
                passenger_activities=[
                    PassengerRoute(
                        loc,
                        passerngerOnboardStatus,
                        "At {}, {} {} at {}".format(datetime.strptime(p['time'], "%Y/%m/%d %H:%M:%S"), p["name"], passerngerOnboardStatus.value, loc),
                        datetime.strptime(p['time'], "%Y/%m/%d %H:%M:%S")
                    )
                ]
            )
            self.add_and_update_passenger(found_passenger)

    def update_bus_info_from_json(self, bus_data_list_json):
        bus_data_list = json.loads(bus_data_list_json)
        for bus_data in bus_data_list:
            movement = BusMovement.GO if bus_data["bus_door_status"] == "closed" else BusMovement.STOP
            self.bus.plate_number = bus_data["bus_id"]
            bus_activity = BusActivity(bus_data["location"],
                                       movement,
                                       datetime.strptime(bus_data['time'], "%Y/%m/%d %H:%M:%S").replace(
                                           tzinfo=timezone.utc))
            if bus_activity not in self.bus.bus_activities:
                self.bus.bus_activities.append(bus_activity)
                self.bus.bus_activities = sorted(self.bus.bus_activities, key=attrgetter('time'))
        if self.passengers:
            # update all passengers who has no location
            for p in self.passengers:
                if not p.passenger_activities or p.passenger_activities[-1].location == "":
                    p.passenger_activities[-1].location = self.bus.bus_activities[-1].location


    def get_passenger_list_who_missed_the_stop(self) -> list[Passenger]:
        bus_movements = self.bus.bus_activities
        all_passengers = self.passengers
        if bus_movements and all_passengers:
            last_bus_stop = bus_movements[-1].location
            passengers_who_disembarked_at_last_stop = [passenger for passenger in all_passengers
                                                       if passenger.final_destination == last_bus_stop]
            passengers_who_might_have_missed_stop = [disembarked_passenger for disembarked_passenger in
                                                     passengers_who_disembarked_at_last_stop
                                                     if disembarked_passenger.passenger_activities
                                                     and disembarked_passenger.passenger_activities[
                                                         -1].passenger_status != PassengerOnboardStatus.EXITING]
            return passengers_who_might_have_missed_stop
        return []



if __name__ == '__main__':
    bus = Bus('', [])
    bus_attendance = BusAttendance(bus, [])
    passengers = [
        Passenger(name='Alice', final_destination='Boston', passenger_activities=[PassengerRoute("", PassengerOnboardStatus.ENTERING, datetime.now())]),
        Passenger(name='Alice', final_destination='Boston', passenger_activities=[PassengerRoute("", PassengerOnboardStatus.ENTERING, datetime.now())]),
        Passenger(name='Bob', final_destination='Philadelphia', passenger_activities=[PassengerRoute("", PassengerOnboardStatus.ENTERING, datetime.now())]),
        Passenger(name='Charlie', final_destination='Washington D.C.', passenger_activities=[PassengerRoute("", PassengerOnboardStatus.ENTERING, datetime.now())]),
    ]
    bus.bus_activities = BusActivity("", BusMovement.STOP, datetime.now())
    # Add some Passenger instances
    for p in passengers:
        bus_attendance.add_and_update_passenger(p)

    # Serialize the BusAttendance instance to JSON
    bus_attendance_json = bus_attendance.to_json()
    print(bus_attendance_json)