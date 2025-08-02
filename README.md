# Credit Approval System

## Overview

This is a backend-only Credit Approval System developed using **Django 4+**, **Django REST Framework**, **PostgreSQL**, and **Celery**. The project is containerized using **Docker** and orchestrated with **Docker Compose**.

The system allows customer registration, loan eligibility checking, and loan processing based on historical data and business rules.

---

## Features

* Register customers and compute approved credit limits
* Check loan eligibility with credit score logic
* Create loans if eligible
* View loan details by loan ID or customer ID
* Background ingestion of Excel data using Celery

---

## Tech Stack

* **Backend:** Python, Django, DRF
* **Database:** PostgreSQL
* **Task Queue:** Celery
* **Broker:** Redis
* **Containerization:** Docker, Docker Compose

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/FrostyFeet-coder/Credit_system.git
cd Credit_system
```

### 2. Build and Start the Application

```bash
docker-compose up --build
```

This will:

* Start Django app
* Set up PostgreSQL
* Run Redis server
* Start Celery worker

### 3. Load Initial Data

Place `customer_data.xlsx` and `loan_data.xlsx` into the `/media` folder. The ingestion will be triggered automatically when files are detected.

---

## API Endpoints

### 1. Register Customer

`POST /register`
Registers a new customer and calculates approved limit as:

```
approved_limit = round(36 * monthly_salary / 100000) * 100000
```

#### Request Body

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "monthly_income": 50000,
  "phone_number": "1234567890"
}
```

#### Response Body

```json
{
  "customer_id": 1,
  "name": "John Doe",
  "age": 30,
  "monthly_income": 50000,
  "approved_limit": 1800000,
  "phone_number": "1234567890"
}
```

---

### 2. Check Eligibility

`POST /check-eligibility`

#### Request Body

```json
{
  "customer_id": 1,
  "loan_amount": 300000,
  "interest_rate": 10.5,
  "tenure": 12
}
```

#### Response Body

```json
{
  "customer_id": 1,
  "approval": true,
  "interest_rate": 10.5,
  "corrected_interest_rate": 12.0,
  "tenure": 12,
  "monthly_installment": 26537.56
}
```

---

### 3. Create Loan

`POST /create-loan`

#### Request Body

```json
{
  "customer_id": 1,
  "loan_amount": 300000,
  "interest_rate": 12.0,
  "tenure": 12
}
```

#### Response Body

```json
{
  "loan_id": 1,
  "customer_id": 1,
  "loan_approved": true,
  "message": "Loan approved successfully.",
  "monthly_installment": 26789.50
}
```

---

### 4. View Loan Details

`GET /view-loan/<loan_id>`

#### Response Body

```json
{
  "loan_id": 1,
  "customer": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "1234567890",
    "age": 30
  },
  "loan_amount": 300000,
  "interest_rate": 12.0,
  "monthly_installment": 26789.50,
  "tenure": 12
}
```

---

### 5. View Loans by Customer

`GET /view-loans/<customer_id>`

#### Response Body

```json
[
  {
    "loan_id": 1,
    "loan_amount": 300000,
    "interest_rate": 12.0,
    "monthly_installment": 26789.50,
    "repayments_left": 10
  },
  ...
]
```

---

## Credit Score Calculation Logic

* Credit Score out of 100 based on:

  * Past loans paid on time
  * No of loans taken
  * Loan activity in current year
  * Approved loan volume
  * If `current_loans > approved_limit`: credit score = 0

**Loan Approval Rules:**

* Score > 50 → Approve loan
* 30 < Score <= 50 → Approve with ≥ 12% interest
* 10 < Score <= 30 → Approve with ≥ 16% interest
* Score <= 10 or EMI > 50% of income → Reject

---

## Testing

Run tests using:

```bash
docker-compose exec web python manage.py test                              
```

---
![Docker](https://img.shields.io/badge/docker-ready-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

