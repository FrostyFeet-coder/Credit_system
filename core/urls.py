from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterCustomerView.as_view(), name='register-customer'),
    path('check-eligibility/', CheckEligibilityView.as_view(), name='check-eligibility'),
    path('create-loan/', CreateLoanView.as_view(), name='create-loan'),
    path('view-loan/<int:loan_id>/', ViewLoanById.as_view(), name='view-loan'),
    path('view-loans/<int:customer_id>/', ViewLoansByCustomer.as_view(), name='view-loans'),
    path('upload-customers/', UploadCustomerExcelView.as_view(), name='upload-customers'),
    path('upload-loans/', UploadLoanExcelView.as_view(), name='upload-loans'),

]
