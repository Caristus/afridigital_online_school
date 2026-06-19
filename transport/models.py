from django.db import models
from core.models import BaseModel, AcademicYear
from users.models import StudentProfile

class Bus(BaseModel):
    bus_number = models.CharField(max_length=50, unique=True)
    capacity = models.IntegerField()
    driver_name = models.CharField(max_length=200)
    driver_phone = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Bus"
        verbose_name_plural = "Buses"

    def __str__(self):
        return f"Bus {self.bus_number}"

class Route(BaseModel):
    name = models.CharField(max_length=200)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Route"
        verbose_name_plural = "Routes"

    def __str__(self):
        return self.name

class StudentTransportAllocation(BaseModel):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='transport_allocations')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Transport Allocation"
        verbose_name_plural = "Transport Allocations"
        unique_together = ['student', 'academic_year']
