from datetime import datetime, timezone
from operator import attrgetter

from model.Bus import BusActivity, Bus, BusStatus
from model.ObjectDetection import ObjectDetection, CarMovement
from model.Passenger import Passenger, PassengerRoute, PassengerOnboardStatus
from dataclasses import dataclass
from dataclasses_json import dataclass_json
import json
import pytz

@dataclass_json
@dataclass
class BusAttendance:
    bus: Bus
    passengers: list[Passenger]
    traffic_events: list[ObjectDetection]
    description = ""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.bus = Bus(plate_number='ABC123', bus_activities=[])
            cls._instance.passengers = []
            cls._instance.traffic_events = []
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
            p.passenger_activities = sorted(p.passenger_activities,
                                            key=lambda x: x.time.astimezone(timezone.utc))


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
        events = [Passenger.from_json(evt) for evt in json_data['traffic_events']]
        cls._instance.bus = bus
        cls._instance.passengers = passengers
        cls._instance.traffic_events = events
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
                        "At {}, {} {} at {}".format(datetime.strptime(p['time'], "%Y/%m/%d %H:%M:%S").replace(tzinfo=pytz.UTC), p["name"], passerngerOnboardStatus.value, loc),
                        datetime.strptime(p['time'], "%Y/%m/%d %H:%M:%S").replace(tzinfo=pytz.UTC)
                    )
                ]
            )
            self.add_and_update_passenger(found_passenger)

    def update_bus_info_from_json(self, bus_data_list_json):
        bus_data_list = json.loads(bus_data_list_json)
        for bus_data in bus_data_list:
            if "bus_stop_sign_status" in bus_data and bus_data["bus_stop_sign_status"] == "show":
                bus_status = BusStatus.STOP
            elif bus_data["bus_door_status"] == "closed":
                bus_status = BusStatus.DOOR_CLOSE
            elif "bus_stop_sign_status" in bus_data and bus_data["bus_stop_sign_status"] == "hide":
                bus_status = BusStatus.GO
            else:
                bus_status = BusStatus.WAITING

            self.bus.plate_number = bus_data["bus_id"]
            bus_activity = BusActivity(bus_data["location"],
                                       bus_status,
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
        if self.bus.bus_activities and len(self.bus.bus_activities) > 0:
            self.update_location_for_existing_traffic_violation(self.bus.bus_activities[-1].location)


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

    def update_location_for_existing_traffic_violation(self, bus_location:str):
        for object_detection in reversed(self.traffic_events):
            if not object_detection.location or len(object_detection.location) <=0:
                object_detection.location = bus_location

    def update_object_detection_events_from_json(self, traffic_data_json):
        traffic_data_list = json.loads(traffic_data_json)
        if "data" in traffic_data_list:
            for traffic_data in traffic_data_list["data"]:
                if traffic_data["status"] == "nearby":
                    movement = CarMovement.NEARBY
                elif traffic_data["status"] == "stop":
                    movement = CarMovement.STOP
                else:
                    movement = CarMovement.GONE

                traffic_event = ObjectDetection(
                    traffic_data["location"], traffic_data["car_plate_number"],
                    movement, datetime.strptime(traffic_data["time"], "%Y/%m/%d %H:%M:%S").replace(tzinfo=pytz.UTC)
                )
                if traffic_event not in self.traffic_events:
                    self.traffic_events.append(traffic_event)
        self.traffic_events = sorted(self.traffic_events, key=attrgetter('time'))

    def get_list_of_vehicle_detected_on_bus_last_stop(self) -> list[ObjectDetection]:
        bus_activity = self.bus.bus_activities[-1] if self.bus.bus_activities else None
        is_bus_stop_sign_on = bus_activity and (
                bus_activity.activity == BusStatus.STOP or bus_activity.activity == BusStatus.WAITING)

        print("is_bus_stop_sign_on: {}".format(is_bus_stop_sign_on))
        if is_bus_stop_sign_on:
            print("bus stop time: {}".format(bus_activity.time))
            for traffic_event in self.traffic_events:
                print("traffic time: {}".format(traffic_event.time))
            # get the traffic event happen after the last bus activity
            events: list[ObjectDetection] = [traffic_event for traffic_event in self.traffic_events
                                             if traffic_event.time >= bus_activity.time]
            for event in events:
                print("traffic event: {}".format(event))
            return events
        return []

    def get_list_of_last_vehicle_movement_on_bus_last_stop(self) -> (bool, int):
        events = self.get_list_of_vehicle_detected_on_bus_last_stop()
        last_movements = {event.plate_number: event for event in events}
        nearby_vehicle_count = sum(1 for event in last_movements.values() if event.status == CarMovement.NEARBY)
        return nearby_vehicle_count > 0, nearby_vehicle_count

if __name__ == '__main__':
    bus = Bus('', [])
    bus_attendance = BusAttendance(bus, [], [])
    passengers = [
        Passenger(name='Alice', final_destination='Boston', passenger_activities=[PassengerRoute("", PassengerOnboardStatus.ENTERING, datetime.now())]),
        Passenger(name='Alice', final_destination='Boston', passenger_activities=[PassengerRoute("", PassengerOnboardStatus.ENTERING, datetime.now())]),
        Passenger(name='Bob', final_destination='Philadelphia', passenger_activities=[PassengerRoute("", PassengerOnboardStatus.ENTERING, datetime.now())]),
        Passenger(name='Charlie', final_destination='Washington D.C.', passenger_activities=[PassengerRoute("", PassengerOnboardStatus.ENTERING, datetime.now())]),
    ]
    bus.bus_activities = BusActivity("", BusStatus.STOP, datetime.now())
    # Add some Passenger instances
    for p in passengers:
        bus_attendance.add_and_update_passenger(p)

    # Serialize the BusAttendance instance to JSON
    bus_attendance_json = bus_attendance.to_json()
    print(bus_attendance_json)