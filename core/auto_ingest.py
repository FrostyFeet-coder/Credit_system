import os
from django.conf import settings
from core.tasks import process_customer_excel, process_loan_excel

def run_ingestion_if_needed():
    customer_path = os.path.join(settings.BASE_DIR, 'media', 'customer_data.xlsx')
    loan_path = os.path.join(settings.BASE_DIR, 'media', 'loan_data.xlsx')

    if os.path.exists(customer_path):
        print(f"[INFO] Found {customer_path} — triggering Celery task.")
        process_customer_excel.delay(customer_path)
    else:
        print("[INFO] No customer_data.xlsx found.")

    if os.path.exists(loan_path):
        print(f"[INFO] Found {loan_path} — triggering Celery task.")
        process_loan_excel.delay(loan_path)
    else:
        print("[INFO] No loan_data.xlsx found.")
