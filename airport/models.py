from django.db import models
from django.conf import settings


class AirplaneType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Airport(models.Model):
    name = models.CharField(max_length=255, unique=True)
    closest_big_city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="airports"
    )

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE, related_name="airplanes"
    )

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="routes"
    )
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source.name} -> {self.destination.name}"


class Flight(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew)

    class Meta:
        ordering = ["-departure_time"]

    def __str__(self):
        return f"{str(self.route)} {(self.departure_time)}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    def __str__(self):
        return f"{str(self.flight)} (row: {self.row}, seat: {self.seat})"

    class Meta:
        ordering = ["row", "seat"]
