from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Person(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    full_name = models.CharField(max_length=60, null=True, blank=True)
    email = models.EmailField(max_length=254, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)

    def age(self):
        import datetime
        return int((datetime.date.today() - self.birth_date).days / 365.25)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.first_name and self.last_name:
            self.full_name = f'{self.first_name} {self.last_name}'
        super(Person, self).save(*args, **kwargs)

class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    txn_id = models.CharField(max_length=50, unique=True)
    paid_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='transactions')
    paid_to = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='received_transactions')
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    valid = models.BooleanField(default=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self) -> str:
        return f'{self.paid_by} paid {self.amount} to {self.paid_to} on {self.date}'
    
    def save(self, *args, **kwargs):
        super(Transaction, self).save(*args, **kwargs)
        if not self.txn_id:
            from random import randint
            self.txn_id = f'TXN{self.date.strftime("%Y%m%d")}{randint(10000, 99999)}{self.id}'
            
        super(Transaction, self).save(*args, **kwargs)

    def set_expired(self):
        self.valid = False
        self.save()
    def is_expired(self):
        return not self.valid
    

class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    From = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    title = models.CharField(max_length=50)
    message = models.TextField()
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('read', 'Read'), ('unread', 'Unread')], default='unread')
    def __str__(self) -> str:
        return f'{self.title} - {self.date}'