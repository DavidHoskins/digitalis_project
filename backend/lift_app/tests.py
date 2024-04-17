from django.test import TestCase, RequestFactory

from lift_app.lift_movement import enqueue_movement
from lift_app.models import Lift
from lift_app.views import lift_config, lift_status, get_first_avaliable_lift, route_in_destinations, append_distinct_lift_route, lift_request
from unittest.mock import patch

import json

# Create your tests here.

class TestLiftMovement(TestCase):
    def setUp(self):
        Lift.objects.create(current_floor=1, serviced_floors=[0,1,2,3], destination_floors=[0,1])
        Lift.objects.create(current_floor=1, serviced_floors=[0,1,2,3], destination_floors=[-1,2])
        Lift.objects.create(current_floor=1, serviced_floors=[0,1,2,3], destination_floors=[3,1])

    def test_enqueue_movement_positive(self):
        enqueue_movement(0)
        lift = Lift.objects.get(pk=1)
        self.assertEqual(lift.destination_floors, '[]')
    
    def test_enqueue_movement_negative(self):
        enqueue_movement(1)
        lift = Lift.objects.get(pk=2)
        self.assertEqual(lift.destination_floors, '[]')

    def test_enqueue_movement_reverse(self):
        enqueue_movement(2)
        lift = Lift.objects.get(pk=3)
        self.assertEqual(lift.destination_floors, '[]')

class TestViews(TestCase):
    def setUp(self):
        Lift.objects.create(current_floor=1, serviced_floors=[0,1,2], destination_floors=[0,1])
        Lift.objects.create(current_floor=1, serviced_floors=[0,1,2,3], destination_floors=[-1,2])
        Lift.objects.create(current_floor=1, serviced_floors=[1,2,4], destination_floors=[3,1])
        self.factory = RequestFactory()

    def test_lift_config(self):
        request = self.factory.get("/api/lift/config/")
        response = lift_config(request=request)
        self.assertEqual({'lifts': [{'serviced_floors': [0, 1, 2]}, 
                                    {'serviced_floors': [0, 1, 2, 3]}, 
                                    {'serviced_floors': [1, 2, 4]}]}, 
                                    json.loads(response.content))
        
    def test_lift_status(self):
        request = self.factory.get("/api/lift/status/")
        response = lift_status(request=request)
        self.assertEqual({'lifts': [{'floor': 1, 'destinations': [0, 1]}, 
                                    {'floor': 1, 'destinations': [-1, 2]}, 
                                    {'floor': 1, 'destinations': [3, 1]}]}, 
                                    json.loads(response.content))
    
    # Block of tests for get_first_avaliable_lift
    def test_get_first_avaliable_lift_positive(self):
        result = get_first_avaliable_lift(0, 2)
        self.assertEqual(0, result)
    
    def test_get_first_avaliable_lift_negative(self):
        result = get_first_avaliable_lift(0, -2)
        self.assertEqual(-1, result)

    def test_get_first_avaliable_lift_reverse(self):
        result = get_first_avaliable_lift(4,2)
        self.assertEqual(2, result)

    # Block of tests for route_in_destinations
    def test_route_in_destinations_contains_journey(self):
        result = route_in_destinations(0, 1, [0, 1], 0)
        self.assertTrue(result)
    
    def test_route_in_destinations_not_contains_journey(self):
        result = route_in_destinations(2, 3, [0, 1], 0)
        self.assertFalse(result)
    
    def test_route_in_destinations_half_contains_journey(self):
        result = route_in_destinations(1, 3, [0, 1], 0)
        self.assertFalse(result)
    
    # Block of tests for append_distinct_lift_route
    def test_append_distinct_lift_route_included(self):
        with patch('lift_app.views.enqueue_movement.delay'):
            index = 0
            append_distinct_lift_route(0, 1, index)
            lift = Lift.objects.get(pk=(index+1))
            self.assertEqual(json.loads(lift.destination_floors), [0,1])
    
    def test_append_distinct_lift_route_not_included(self):
        with patch('lift_app.views.enqueue_movement.delay'):
            index = 1
            append_distinct_lift_route(0, 1, index)
            lift = Lift.objects.get(pk=(index+1))
            self.assertEqual(json.loads(lift.destination_floors), [-1, 2, 0,1])
    
    # Testing to confirm direction of route is input correctly, i.e. 1 -> 0 is already included however we 0 -> 1
    def test_append_distinct_lift_route_half_included_wrong_direction(self):
        with patch('lift_app.views.enqueue_movement.delay'):
            index = 2
            append_distinct_lift_route(0, 1, index)
            lift = Lift.objects.get(pk=(index+1))
            self.assertEqual(json.loads(lift.destination_floors), [3,1,0,1])
    
    def test_append_distinct_lift_route_half_included_correct_direction(self):
        with patch('lift_app.views.enqueue_movement.delay'):
            index = 2
            append_distinct_lift_route(1, 0, index)
            lift = Lift.objects.get(pk=(index+1))
            self.assertEqual(json.loads(lift.destination_floors), [3,1,0])
    
    # Block of tests for lift_request
    def test_lift_request_match_one_lift(self):
        with patch('lift_app.views.enqueue_movement.delay'):
            request = self.factory.post("/api/lift/request/", {"to_floor": 0, "from_floor": 2}, content_type="application/json")
            response = lift_request(request=request)
            self.assertEqual(json.loads(response.content), {'lift': 0})
    
    def test_lift_request_match_different_list(self):
        with patch('lift_app.views.enqueue_movement.delay'):
            request = self.factory.post("/api/lift/request/", {"to_floor": 1, "from_floor": 4}, content_type="application/json")
            response = lift_request(request=request)
            self.assertEqual(json.loads(response.content), {'lift': 2})
