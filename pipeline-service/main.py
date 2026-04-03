from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models.customer import Customer
from services.ingestion import fetch_all_customers_from_flask, upsert_customers

app = FastAPI(title="Pipeline Service")

Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health():
    return {"status": "healthy"}


@app.post("/api/ingest")
def ingest(db: Session = Depends(get_db)):
    try:
        customers = fetch_all_customers_from_flask()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch from mock server: {str(e)}")

    try:
        count = upsert_customers(db, customers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {"status": "success", "records_processed": count}


@app.get("/api/customers")
def get_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total = db.query(Customer).count()
    offset = (page - 1) * limit
    customers = db.query(Customer).offset(offset).limit(limit).all()

    return {
        "data": [
            {
                "customer_id": c.customer_id,
                "first_name": c.first_name,
                "last_name": c.last_name,
                "email": c.email,
                "phone": c.phone,
                "address": c.address,
                "date_of_birth": str(c.date_of_birth) if c.date_of_birth else None,
                "account_balance": float(c.account_balance) if c.account_balance else None,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in customers
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }


@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return {
        "data": {
            "customer_id": customer.customer_id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
            "phone": customer.phone,
            "address": customer.address,
            "date_of_birth": str(customer.date_of_birth) if customer.date_of_birth else None,
            "account_balance": float(customer.account_balance) if customer.account_balance else None,
            "created_at": customer.created_at.isoformat() if customer.created_at else None,
        }
    }
