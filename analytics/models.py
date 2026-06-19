from django.db import models
from core.models import BaseModel, AcademicYear, Term

class PerformanceReport(BaseModel):
    report_type = models.CharField(max_length=50, choices=[('student', 'Student'), ('class', 'Class'), ('subject', 'Subject')])
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    data = models.JSONField(help_text="Report data in JSON")

    class Meta:
        verbose_name = "Performance Report"
        verbose_name_plural = "Performance Reports"

class FinancialReport(BaseModel):
    report_type = models.CharField(max_length=50, choices=[('revenue', 'Revenue'), ('expenses', 'Expenses'), ('outstanding', 'Outstanding')])
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Financial Report"
        verbose_name_plural = "Financial Reports"
