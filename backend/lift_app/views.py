from django.shortcuts import render
import json
from django.http import HttpResponse, JsonResponse
from lift_app.models import Lift
from lift_app.lift_movement import enqueue_movement


from django.views.decorators.csrf import csrf_exempt

# Have to do this as we're likely making a request from the same system
@csrf_exempt
def lift_config(request) -> (JsonResponse | HttpResponse):
    try:
        if request.method == 'GET':
            lift_data = list(Lift.objects.all().values("serviced_floors"))

            # Convert from string to list of int's
            lift_data = [{"serviced_floors" : json.loads(x["serviced_floors"])} for x in lift_data]
            json_data = {"lifts" : lift_data}

            return JsonResponse(json_data, content_type='application/json')
    except:
        print("Error handling lift config request")
    return HttpResponse("<h1>404 Page not found</h1>")

# Have to do this as we're likely making a request from the same system
@csrf_exempt
def lift_status(request)-> (JsonResponse | HttpResponse):
    try:
        if request.method == 'GET':
            destination_data = list(Lift.objects.all().values("destination_floors"))
            floor_data = list(Lift.objects.all().values("current_floor"))

            # Convert from string to list of int's
            destination_data = [{"floor": floor_data[idx]["current_floor"], "destinations" : json.loads(x["destination_floors"])} for idx, x in enumerate(destination_data)]
            json_data = {"lifts" : destination_data}

            return JsonResponse(json_data)
    except:
        print("Error handling lift status request")
    return HttpResponse("<h1>404 Page not found</h1>")

# Have to do this as we're likely making a request from the same system
@csrf_exempt
def lift_request(request)-> (JsonResponse | HttpResponse):
    try:
        if request.method == 'POST':
            request_data = json.loads(request.body)
            to_floor = -1
            from_floor = -1
            if 'to_floor' in request_data:
                to_floor = int(request_data["to_floor"])
            if 'from_floor' in request_data:
                from_floor = int(request_data["from_floor"])
            
            lift_to_use = get_first_avaliable_lift(from_floor=from_floor,to_floor=to_floor)
            append_distinct_lift_route(from_floor=from_floor, to_floor=to_floor, lift_index=lift_to_use)

            json_data = {"lift" : lift_to_use}
            return JsonResponse(json_data)
    except:
        print("Error handling lift request")
    return HttpResponse("<h1>404 Page not found</h1>")

# Gets the first avaliable lift that services both floors provided
# Returns -1 if no lift can be found.
def get_first_avaliable_lift(from_floor, to_floor) -> int:
    try:
        lifts = Lift.objects.all().values("serviced_floors")
        for idx, lift in enumerate(lifts):
            serviced_floors_arr = json.loads(lift["serviced_floors"])
            if from_floor in serviced_floors_arr and to_floor in serviced_floors_arr:
                return idx
    except:
        print("Error finding first avaliable lift")

    return -1

def route_in_destinations(from_floor: int, to_floor: int, destinations: list[int], current_floor: int) -> bool:
    try:
        # Check it contains both values or we're currently on that floor
        if (from_floor not in destinations and from_floor != current_floor) or to_floor not in destinations:
            return False
        
        if current_floor == from_floor and to_floor in destinations:
            return True
        
        # Check the floors are in the correct order for arrival
        if destinations.index(from_floor) <= destinations.index(to_floor):
            return True
    except:
        print("Error checking route in destination")

    # All other scenarios false.
    return False

def append_distinct_lift_route(from_floor: int, to_floor: int, lift_index: int) -> None:
    try:
        lift = Lift.objects.get(pk=(lift_index+1))

        destinations = json.loads(lift.destination_floors)
        
        # Check if route was already added to the list
        if not route_in_destinations(from_floor=from_floor, to_floor=to_floor, 
                                    destinations=destinations, current_floor=lift.current_floor):
            # If we're not already at the floor move to 'to_floor'
            if not lift.current_floor == from_floor:
                destinations.append(from_floor)
            destinations.append(to_floor)
            lift.destination_floors = str(destinations)
            lift.save()

        enqueue_movement.delay(lift_index=lift_index)
    except:
        print("Error appending distinct lift route to Lift object")
