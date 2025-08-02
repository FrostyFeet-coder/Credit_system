from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import CustomerSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .utils import calculate_credit_score
import math
import datetime
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

class RegisterCustomerView(APIView):
    def post(self, request):
        data = request.data

        # Calculate approved limit: 36 * salary (rounded to nearest lakh)
        monthly_income = int(data['monthly_income'])
        approved_limit = round((36 * monthly_income) / 100000) * 100000

        customer = Customer.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=data['age'],
            monthly_income=monthly_income,
            phone_number=data['phone_number'],
            approved_limit=approved_limit,
            current_debt=0,
        )

        serializer = CustomerSerializer(customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

import traceback

import traceback
import sys

from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import Customer, Loan
from datetime import datetime
import math
import traceback, sys

class CheckEligibilityView(APIView):
    def post(self, request):
        try:
            data = request.data
            customer = Customer.objects.get(id=data['customer_id'])
            loan_amount = float(data['loan_amount'])
            input_rate = float(data['interest_rate'])
            tenure = int(data['tenure'])

            # 🔹 1. Fetch active loans
            active_loans = Loan.objects.filter(customer=customer)

            # 🔹 2. Check EMI threshold
            total_emis = sum(l.monthly_installment for l in active_loans)
            if total_emis > 0.5 * customer.monthly_income:
                return Response({
                    "approval": False,
                    "message": "Total EMIs exceed 50% of monthly income"
                }, status=200)

            # 🔹 3. Check if total loans > approved limit
            total_loan_amount = sum(l.loan_amount for l in active_loans)
            if total_loan_amount > customer.approved_limit:
                credit_score = 0
            else:
                credit_score = self.calculate_credit_score(customer)

            # 🔹 4. Calculate EMI
            monthly_rate = input_rate / (12 * 100)
            emi = (loan_amount * monthly_rate * math.pow(1 + monthly_rate, tenure)) / (math.pow(1 + monthly_rate, tenure) - 1)

            # 🔹 5. Eligibility based on credit score
            approval = False
            corrected_rate = input_rate

            if credit_score > 50:
                approval = True
            elif 30 < credit_score <= 50:
                if input_rate >= 12:
                    approval = True
                else:
                    corrected_rate = 12
            elif 10 < credit_score <= 30:
                if input_rate >= 16:
                    approval = True
                else:
                    corrected_rate = 16
            else:
                approval = False

            return Response({
                "customer_id": customer.id,
                "approval": approval,
                "credit_score": credit_score,
                "interest_rate": input_rate,
                "corrected_interest_rate": corrected_rate,
                "tenure": tenure,
                "monthly_installment": round(emi, 2)
            }, status=200)

        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            return Response({"error": str(e)}, status=500)

    # 🔹 6. Calculate Credit Score from loan history
    def calculate_credit_score(self, customer):
        loans = Loan.objects.filter(customer=customer)
        score = 0

        paid_on_time_loans = loans.filter(emis_paid_on_time=True).count()
        total_loans = loans.count()
        if total_loans > 0:
            score += (paid_on_time_loans / total_loans) * 30  

        # ii. Number of loans taken in past
        if total_loans >= 5:
            score += 10
        elif total_loans >= 3:
            score += 7
        elif total_loans >= 1:
            score += 5

        # iii. Loan activity in current year
        current_year = datetime.now().year
        current_year_loans = loans.filter(start_date__year=current_year).count()
        if current_year_loans >= 2:
            score += 10
        elif current_year_loans == 1:
            score += 5

        # iv. Loan approved volume
        total_approved_volume = sum(l.loan_amount for l in loans)
        if total_approved_volume >= 500000:
            score += 20
        elif total_approved_volume >= 200000:
            score += 10
        else:
            score += 5

        return round(score)
from datetime import datetime, timedelta

class CreateLoanView(APIView):
    def post(self, request):
        try:
            data = request.data
            customer = Customer.objects.get(id=data['customer_id'])
            loan_amount = float(data['loan_amount'])
            input_rate = float(data['interest_rate'])
            tenure = int(data['tenure'])

            credit_score = calculate_credit_score(customer)

            # Step 1: Check existing EMIs
            existing_emis = sum(
                l.monthly_installment for l in Loan.objects.filter(customer=customer)
            )
            if existing_emis > 0.5 * customer.monthly_income:
                return Response({
                    "loan_id": None,
                    "customer_id": customer.id,
                    "loan_approved": False,
                    "message": "Existing EMIs exceed 50% of salary",
                    "monthly_installment": None
                })

            # Step 2: Calculate EMI with input interest rate
            r = input_rate / (12 * 100)
            emi = (loan_amount * r * pow(1 + r, tenure)) / (pow(1 + r, tenure) - 1)
            corrected_rate = input_rate
            loan_approved = False

            # Step 3: Approval logic based on credit score and interest rate
            if credit_score > 50:
                loan_approved = True
            elif 30 < credit_score <= 50:
                if input_rate >= 12:
                    loan_approved = True
                else:
                    corrected_rate = 12
            elif 10 < credit_score <= 30:
                if input_rate >= 16:
                    loan_approved = True
                else:
                    corrected_rate = 16
                    loan_approved = corrected_rate >= 16

            else:
                loan_approved = False

            # Step 4: Recalculate EMI if corrected rate was applied
            if corrected_rate != input_rate:
                r = corrected_rate / (12 * 100)
                emi = (loan_amount * r * pow(1 + r, tenure)) / (pow(1 + r, tenure) - 1)

                # ✅ Fix: Set loan_approved = True if corrected rate satisfies condition
                if 30 < credit_score <= 50 and corrected_rate >= 12:
                    loan_approved = True
                elif 10 < credit_score <= 30 and corrected_rate >= 16:
                    loan_approved = True

            # Step 5: If still not approved, return rejection response
            if not loan_approved:
                return Response({
                    "loan_id": None,
                    "customer_id": customer.id,
                    "loan_approved": False,
                    "message": "Loan not approved due to low credit score or interest rate.",
                    "monthly_installment": round(emi, 2)
                })

            # Step 6: Create the loan
            start_date = datetime.today()
            end_date = start_date + timedelta(days=30 * tenure)
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount,
                interest_rate=corrected_rate,
                tenure=tenure,
                monthly_installment=emi,
                emis_paid_on_time=0,
                end_date=end_date
            )

            # Step 7: Update customer's current debt
            customer.current_debt += loan_amount
            customer.save()

            # Step 8: Return success response
            return Response({
                "loan_id": loan.id,
                "customer_id": customer.id,
                "loan_approved": True,
                "message": "Loan approved and created.",
                "monthly_installment": round(emi, 2)
            })

        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class ViewLoanById(APIView):
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(id=loan_id)
            customer = loan.customer

            return Response({
                "loan_id": loan.id,
                "customer": {
                    "id": customer.id,
                    "first_name": customer.first_name,
                    "last_name": customer.last_name,
                    "phone_number": customer.phone_number,
                    "age": customer.age
                },
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": round(loan.monthly_installment, 2),
                "tenure": loan.tenure
            })

        except Loan.DoesNotExist:
            return Response({"error": "Loan not found"}, status=404)


class ViewLoansByCustomer(APIView):
    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(id=customer_id)
            loans = Loan.objects.filter(customer=customer)

            result = []
            for loan in loans:
                remaining_months = loan.tenure - loan.emis_paid_on_time
                result.append({
                    "loan_id": loan.id,
                    "loan_amount": loan.loan_amount,
                    "interest_rate": loan.interest_rate,
                    "monthly_installment": round(loan.monthly_installment, 2),
                    "repayments_left": remaining_months
                })

            return Response(result)

        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)


from rest_framework.parsers import MultiPartParser
from .tasks import process_customer_excel, process_loan_excel

class UploadCustomerExcelView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        excel_file = request.FILES['file']
        path = f'media/customer_data.xlsx'
        with open(path, 'wb+') as f:
            for chunk in excel_file.chunks():
                f.write(chunk)

        process_customer_excel.delay(path)
        return Response({'message': 'Customer file uploaded. Processing...'}, status=200)

class UploadLoanExcelView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        excel_file = request.FILES['file']
        path = f'media/loan_data.xlsx'
        with open(path, 'wb+') as f:
            for chunk in excel_file.chunks():
                f.write(chunk)

        process_loan_excel.delay(path)
        return Response({'message': 'Loan file uploaded. Processing...'}, status=200)
