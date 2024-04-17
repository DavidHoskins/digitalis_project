from lift_app.models import Lift
import json
from time import sleep
from celery import shared_task

@shared_task
def enqueue_movement(lift_index: int):
    try:
        lift = Lift.objects.get(pk=(lift_index + 1))
        destinations = list(json.loads(lift.destination_floors))
    except:
        print("Error finding lift from list of lifts")
    else:
        while len(destinations) > 0:
            try:
                next_floor = destinations[0]
                lift.current_floor = next_floor
                new_destinations = destinations
                new_destinations.pop(0)
                lift.destination_floors = json.dumps(new_destinations)
                lift.save()
            except:
                print("Error applying destination floors change to lift record")
            else:
                destinations = new_destinations 