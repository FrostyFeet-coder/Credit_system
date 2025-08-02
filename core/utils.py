from .models import Loan
import datetime
def calculate_credit_score(customer):
    loans = Loan.objects.filter(customer=customer)
    total_loans = loans.count()

    if customer.current_debt > customer.approved_limit:
        return 0

    on_time_ratio = (
        sum(loan.emis_paid_on_time for loan in loans) / total_loans if total_loans else 0
    )
    current_year_loans = loans.filter(start_date__year=datetime.date.today().year).count()
    total_volume = sum(loan.loan_amount for loan in loans)

    score = 40 * on_time_ratio + 10 * current_year_loans + 0.0002 * total_volume

    # ✅ Add a base score if user is new but has no bad record
    if total_loans == 0:
        score = 60  # force good score for new users

    return min(int(score), 100)
