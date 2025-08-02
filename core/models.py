from django.db import models

# Create your models here.
class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    monthly_income = models.IntegerField()
    phone_number = models.BigIntegerField()
    approved_limit = models.IntegerField()
    current_debt = models.FloatField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_amount = models.FloatField()
    interest_rate = models.FloatField()
    tenure = models.IntegerField()
    monthly_installment = models.FloatField()
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    emis_paid_on_time = models.IntegerField(default=0)

    def __str__(self):
        return f"Loan {self.id} for {self.customer}"
