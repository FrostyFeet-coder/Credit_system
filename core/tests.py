from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from django.urls import reverse
from core.models import Customer

class CustomerTests(APITestCase):
    def test_register_customer(self):
        data = {
            "first_name": "Test",
            "last_name": "User",
            "age": 30,
            "monthly_income": 50000,
            "phone_number": "9999988888"
        }
        response = self.client.post(reverse('register-customer'), data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["monthly_income"], 50000)
        self.assertEqual(response.data["approved_limit"], 1800000)  # 36 * salary rounded to lakh

    def test_check_eligibility_success(self):
        # Create dummy customer for eligibility
        customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=30,
            phone_number="9876543210",
            monthly_income=100000,
            approved_limit=3600000,
            current_debt=0
        )
        data = {
            "customer_id": customer.id,
            "loan_amount": 100000,
            "interest_rate": 14,
            "tenure": 12
        }
        response = self.client.post(reverse('check-eligibility'), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("approval", response.data)

    def test_check_eligibility_fail_due_to_emis(self):
        # Force fail due to high EMIs
        customer = Customer.objects.create(
            first_name="Fail",
            last_name="User",
            age=28,
            phone_number="8888877777",
            monthly_income=20000,
            approved_limit=720000,
            current_debt=100000  # too high
        )
        data = {
            "customer_id": customer.id,
            "loan_amount": 50000,
            "interest_rate": 10,
            "tenure": 24
        }
        response = self.client.post(reverse('check-eligibility'), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['approval'] , False)

