from datetime import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


from airport.models import (
    City,
    Airport,
    Route,
    AirplaneType,
    Crew,
    Airplane,
    Flight,
)
from airport.serializers import (
    RouteListSerializer,
    AirportListSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
)

AIRPORT_URL = reverse("airport:airport-list")
ROUTE_URL = reverse("airport:route-list")
FLIGHT_URL = reverse("airport:flight-list")


def sample_city(**params):
    defaults = {"name": "Kyiv"}
    defaults.update(params)

    return City.objects.create(**defaults)


def sample_airport(**params):
    city = params.get("closest_big_city") or sample_city()
    defaults = {
        "name": "Kyiv International Airport (Zhuliany)",
        "closest_big_city": city,
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


def sample_route(**params):
    city_1 = sample_city(name="Kharkiv")
    city_2 = sample_city(name="Lviv")
    airport_1 = sample_airport(
        name="Kharkiv International Airport", closest_big_city=city_1
    )
    airport_2 = sample_airport(
        name="Lviv Danylo Halytskyi International Airport",
        closest_big_city=city_2,
    )
    defaults = {
        "source": airport_1,
        "destination": airport_2,
        "distance": 1020,
    }

    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_airplane_type(**params):
    defaults = {"name": "Airbus"}
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)


def sample_crew(**params):
    defaults = {"first_name": "John", "last_name": "Doe"}
    defaults.update(params)

    return Crew.objects.create(**defaults)


def sample_airplane(**params):
    airplane_type = sample_airplane_type()
    defaults = {
        "name": "Airbus A318",
        "rows": 26,
        "seats_in_row": 6,
        "airplane_type": airplane_type,
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


def sample_flight(**params):
    route = sample_route()
    airplane = sample_airplane()
    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": "2024-06-02T14:00:00",
        "arrival_time": "2024-06-02T15:40:00",
    }
    defaults.update(params)

    return Flight.objects.create(**defaults)


def detail_url(flight_id):
    return reverse("airport:flight-detail", args=[flight_id])


class UnauthorizedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="test123"
        )
        self.client.force_authenticate(self.user)

    def test_airport_list(self):
        sample_airport()

        response = self.client.get(AIRPORT_URL)
        airports = Airport.objects.all()
        serializer = AirportListSerializer(airports, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_airport_by_name(self):
        city_1 = sample_city(name="Kharkiv")
        city_2 = sample_city(name="Lviv")
        airport_1 = sample_airport(
            name="Kharkiv International Airport", closest_big_city=city_1
        )
        airport_2 = sample_airport(
            name="Lviv Danylo Halytskyi International Airport",
            closest_big_city=city_2,
        )

        response = self.client.get(AIRPORT_URL, {"name": f"{airport_1.name}"})

        serializer_1 = AirportListSerializer(airport_1)
        serializer_2 = AirportListSerializer(airport_2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, response.data)
        self.assertNotIn(serializer_2.data, response.data)

    def test_filter_airport_by_city(self):
        city_1 = sample_city(name="Kharkiv")
        city_2 = sample_city(name="Lviv")
        airport_1 = sample_airport(
            name="Kharkiv International Airport", closest_big_city=city_1
        )
        airport_2 = sample_airport(
            name="Lviv Danylo Halytskyi International Airport",
            closest_big_city=city_2,
        )

        response = self.client.get(AIRPORT_URL, {"city": city_1.id})

        serializer_1 = AirportListSerializer(airport_1)
        serializer_2 = AirportListSerializer(airport_2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, response.data)
        self.assertNotIn(serializer_2.data, response.data)

    def test_route_list(self):
        sample_route()

        response = self.client.get(ROUTE_URL)
        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_flight_list(self):
        sample_flight()

        response = self.client.get(FLIGHT_URL)
        flights = Flight.objects.all()
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_flight_by_crew(self):
        flight = sample_flight()

        crew_1 = sample_crew(first_name="John", last_name="Doe")
        crew_2 = sample_crew(first_name="Jane", last_name="Doe")
        crew_3 = sample_crew(first_name="Jack", last_name="Doe")

        flight.crew.add(crew_1)
        flight.crew.add(crew_2)

        response_1 = self.client.get(
            FLIGHT_URL, {"crew": f"{crew_1.id},{crew_2.id}"}
        )
        response_2 = self.client.get(FLIGHT_URL, {"crew": f"{crew_2.id}"})
        response_3 = self.client.get(FLIGHT_URL, {"crew": f"{crew_3.id}"})

        serializer = FlightListSerializer(flight)

        self.assertEqual(response_1.status_code, status.HTTP_200_OK)
        self.assertEqual(response_2.status_code, status.HTTP_200_OK)
        self.assertEqual(response_3.status_code, status.HTTP_200_OK)
        self.assertIn(serializer.data, response_1.data)
        self.assertIn(serializer.data, response_2.data)
        self.assertNotIn(serializer.data, response_3.data)

    def test_retrieve_flight_detail(self):
        flight = sample_flight()

        flight.crew.add(sample_crew())

        url = detail_url(flight.id)
        response = self.client.get(url)

        serializer = FlightDetailSerializer(flight)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_create_flight_forbidden(self):
        route = sample_route()
        airplane = sample_airplane()
        payload = {
            "route": route,
            "airplane": airplane,
            "departure_time": "2024-06-02T14:00:00",
            "arrival_time": "2024-06-02T15:40:00",
        }

        response = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com", password="admin123", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_flight(self):
        route = sample_route()
        airplane = sample_airplane()
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2024-06-02 14:00:00",
            "arrival_time": "2024-06-02 15:40:00",
        }

        response = self.client.post(FLIGHT_URL, payload)
        flight = Flight.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(
                payload[key],
                (
                    getattr(flight, key).id
                    if hasattr(getattr(flight, key), "id")
                    else str(getattr(flight, key))
                ),
            )

    def test_create_flight_with_crew(self):
        crew_1 = sample_crew(first_name="John", last_name="Doe")
        crew_2 = sample_crew(first_name="Jane", last_name="Doe")
        route = sample_route()
        airplane = sample_airplane()
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2024-06-02T14:00:00",
            "arrival_time": "2024-06-02T15:40:00",
            "crew": [crew_1.id, crew_2.id],
        }

        response = self.client.post(FLIGHT_URL, payload)
        flight = Flight.objects.get(id=response.data["id"])
        crew = flight.crew.all()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(crew_1, crew)
        self.assertIn(crew_2, crew)
        self.assertEqual(crew.count(), 2)

    def test_update_flight_forbidden(self):
        flight = sample_flight()
        payload = {
            "route": flight.route,
            "airplane": flight.airplane,
            "departure_time": "2024-06-07T16:05:00",
            "arrival_time": "2024-06-07T17:45:00",
        }
        response = self.client.put(detail_url(flight.id), payload)

        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_partial_update_flight_forbidden(self):
        flight = sample_flight()
        payload = {
            "departure_time": "2024-06-07T16:05:00",
            "arrival_time": "2024-06-07T17:45:00",
        }
        response = self.client.put(detail_url(flight.id), payload)

        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_delete_movie_forbidden(self):
        flight = sample_flight()
        response = self.client.delete(detail_url(flight.id))

        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
