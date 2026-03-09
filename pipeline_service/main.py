from contextlib import asynccontextmanager
from typing import Annotated, Any, Dict
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm.session import Session

from database import Base, get_db, engine
from models.customer import Customer
from services.ingestion import PostgresIngestion


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

SessionDep = Annotated[Session, Depends(get_db)]

@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    return {
        "status": "healthy"
    }

@app.post("/api/ingest")
async def ingest_to_db() -> Dict[str, Any]:
    try:
        postgres_ingestion = PostgresIngestion
        ingest_result = await postgres_ingestion.run()
        if ingest_result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=ingest_result.get("message", "Unknown ingestion error")
            )

        return ingest_result

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/api/customers")
async def get_customers(db_session: SessionDep, page: int = 1, limit: int = 10) -> Dict[str, Any]:
    try:
        offset = (page - 1) * limit
        total = db_session.query(Customer).count()
        customers = db_session.query(Customer).offset(offset).limit(limit).all()

        return {
            "data": customers,
            "total": total,
            "page": page,
            "limit": limit
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/api/customers/{customer_id}")
async def get_customer_by_id(db_session: SessionDep, customer_id: str) -> Dict[str, Any]:
    try:
        customer = db_session.query(Customer).filter(Customer.customer_id == customer_id).first()

        if customer is None:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        return {
            "data": customer
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
