from django.db import models
from core.models import BaseModel
from users.models import StudentProfile, User

class Book(BaseModel):
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=100)
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return f"{self.title} by {self.author}"

class BorrowRecord(BaseModel):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='borrow_records')
    borrowed_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Borrow Record"
        verbose_name_plural = "Borrow Records"
