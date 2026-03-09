from datetime import date, datetime
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql.elements import Decimal
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.sqltypes import Numeric, String, Text

from database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(Text)
    date_of_birth: Mapped[date | None]
    account_balance: Mapped[Decimal | None] = mapped_column(Numeric(15,2))
    created_at: Mapped[datetime | None] = mapped_column(default=datetime.utcnow, server_default=func.now())
    def __repr__(self) -> str:
        return f"Customer(customerid={self.customer_id!r}, first_name={self.first_name!r}, last_name={self.last_name!r})"
