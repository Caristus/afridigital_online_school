from django.db import models
from django.utils import timezone
from core.models import BaseModel, AcademicYear
from users.models import StudentProfile, User

class FeeStructure(BaseModel):
    name = models.CharField(max_length=200)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='fee_structures')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Fee Structure"
        verbose_name_plural = "Fee Structures"

    def __str__(self):
        return f"{self.name} - {self.amount}"

class Invoice(BaseModel):
    STATUS_CHOICES = [('pending', 'Pending'), ('paid', 'Paid'), ('overdue', 'Overdue'), ('cancelled', 'Cancelled')]
    invoice_number = models.CharField(max_length=50, unique=True)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='invoices')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    issued_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ['-issued_date']

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.student}"

    def save(self, *args, **kwargs):
        self.balance = self.amount - self.amount_paid
        if self.balance <= 0:
            self.status = 'paid'
        elif self.due_date and self.due_date < timezone.now().date():
            self.status = 'overdue'
        super().save(*args, **kwargs)

class Payment(BaseModel):
    PAYMENT_METHOD_CHOICES = [('cash', 'Cash'), ('mpesa', 'M-Pesa'), ('bank_transfer', 'Bank Transfer'), ('card', 'Card')]
    payment_reference = models.CharField(max_length=100, unique=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=200, blank=True, null=True)
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment {self.payment_reference} - {self.amount}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        total_paid = Payment.objects.filter(invoice=self.invoice).aggregate(models.Sum('amount'))['amount__sum'] or 0
        self.invoice.amount_paid = total_paid
        self.invoice.save()
