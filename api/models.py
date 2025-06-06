import uuid
from django.db import models
from django.utils import timezone
from accounts.models import Member


def get_today():
    """Get today's date"""
    return timezone.now().date()


class Book(models.Model):
    """Model for library books"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    availability = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        ordering = ['title']

    def __str__(self):
        return f"{self.title} - {'Available' if self.availability else 'Loaned'}"


class Loan(models.Model):
    """Model for book loans"""
    STATUS_CHOICES = [
        ('LOANED', 'Loaned'),
        ('RETURNED', 'Returned'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name='loans'
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name='loans'
    )
    loan_date = models.DateField(default=get_today)
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='LOANED'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Loan'
        verbose_name_plural = 'Loans'
        ordering = ['-loan_date']

    def save(self, *args, **kwargs):
        # Check if this is a new loan by looking at the database
        is_new = self._state.adding
        
        if is_new:
            if not self.book.availability:
                raise ValueError("Book is not available for loan")
        
        # Handle return logic
        if self.status == 'RETURNED' and not self.return_date:
            self.return_date = timezone.now().date()
        
        super().save(*args, **kwargs)
        
        # Update book availability after saving
        if is_new:
            self.book.availability = False
            self.book.save()
        elif self.status == 'RETURNED':
            self.book.availability = True
            self.book.save()
        
        # Create loan history entry
        LoanHistory.objects.create(
            book=self.book,
            member=self.member,
            action_type=self.status,
            action_date=self.return_date if self.status == 'RETURNED' else self.loan_date
        )

    def __str__(self):
        return f"{self.book.title} - {self.member.name} ({self.status})"


class LoanHistory(models.Model):
    """Model for loan history tracking"""
    ACTION_CHOICES = [
        ('LOANED', 'Loaned'),
        ('RETURNED', 'Returned'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name='history'
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name='history'
    )
    action_type = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        default='LOANED'
    )
    action_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Loan History'
        verbose_name_plural = 'Loan History'
        ordering = ['-action_date']

    def __str__(self):
        return f"{self.book.title} - {self.member.name} ({self.action_date})"
