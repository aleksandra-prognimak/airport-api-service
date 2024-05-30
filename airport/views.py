from datetime import datetime
from django.db.models import F, Count
from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet
from airport.models import (
    AirplaneType,
    City,
    Crew,
    Airport,
    Airplane,
    Route,
    Flight,
    Order,
)
from airport.serializers import (
    AirplaneTypeSerializer,
    CitySerializer,
    CrewSerializer,
    AirportSerializer,
    AirplaneSerializer,
    AirportListSerializer,
    AirplaneListSerializer,
    RouteListSerializer,
    RouteSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    FlightSerializer,
    OrderSerializer,
    OrderListSerializer,
)


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class CityViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airport.objects.select_related("closest_big_city")

    def get_queryset(self):
        name = self.request.query_params.get("name")
        city_id = self.request.query_params.get("city")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        if city_id:
            queryset = queryset.filter(closest_big_city_id=int(city_id))

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer

        return AirportSerializer


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airplane.objects.select_related("airplane_type")

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer

        return AirplaneSerializer


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.select_related("source", "destination")

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        return RouteSerializer


class FlightViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        Flight.objects.prefetch_related("crew")
        .select_related("route", "airplane")
        .annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )
        )
    )

    def get_queryset(self):
        date = self.request.query_params.get("date")
        route_id = self.request.query_params.get("route")
        crew = self.request.query_params.get("crew")

        queryset = self.queryset

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=date)

        if route_id:
            queryset = queryset.filter(route_id=int(route_id))

        if crew:
            crew_ids = [int(crew_id) for crew_id in crew.split(",")]
            queryset = queryset.filter(crew__id__in=crew_ids)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        return FlightSerializer


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__route", "tickets__flight__airplane"
    )
    pagination_class = OrderPagination

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
