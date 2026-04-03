import httpx
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from models.customer import Customer

MOCK_SERVER_URL = "http://mock-server:5000"


def fetch_all_customers_from_flask() -> list[dict]:
    """Fetch all customers from the Flask mock server, handling pagination."""
    all_customers = []
    page = 1
    limit = 10

    while True:
        response = httpx.get(
            f"{MOCK_SERVER_URL}/api/customers",
            params={"page": page, "limit": limit},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

        customers = data.get("data", [])
        if not customers:
            break

        all_customers.extend(customers)

        total = data.get("total", 0)
        if page * limit >= total:
            break

        page += 1

    return all_customers


def upsert_customers(db: Session, customers: list[dict]) -> int:
    """Upsert customers into PostgreSQL. Returns count of records processed."""
    records_processed = 0

    for c in customers:
        dob = None
        if c.get("date_of_birth"):
            dob = date.fromisoformat(c["date_of_birth"])

        created = None
        if c.get("created_at"):
            created = datetime.fromisoformat(c["created_at"])

        balance = None
        if c.get("account_balance") is not None:
            balance = Decimal(str(c["account_balance"]))

        values = {
            "customer_id": c["customer_id"],
            "first_name": c["first_name"],
            "last_name": c["last_name"],
            "email": c["email"],
            "phone": c.get("phone"),
            "address": c.get("address"),
            "date_of_birth": dob,
            "account_balance": balance,
            "created_at": created,
        }

        stmt = insert(Customer).values(**values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["customer_id"],
            set_={k: v for k, v in values.items() if k != "customer_id"},
        )
        db.execute(stmt)
        records_processed += 1

    db.commit()
    return records_processed
