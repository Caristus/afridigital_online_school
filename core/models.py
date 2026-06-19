import uuid
from django.db import models

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.__class__.__name__} - {self.id}"

    def soft_delete(self):
        self.is_active = False
        self.save()

class AcademicYear(BaseModel):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

class Term(BaseModel):
    name = models.CharField(max_length=50)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='terms')
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Term"
        verbose_name_plural = "Terms"
        unique_together = ['name', 'academic_year']

    def __str__(self):
        return f"{self.name} - {self.academic_year.name}"
