from datetime import datetime
import logging
import os
from typing import Any, Dict, List
import dlt
import httpx

from database import database_url

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [Pipeline] %(message)s"
)
logger = logging.getLogger(__name__)

class PostgresIngestion:
    api_url: str = "http://mock-server:5000"
    timeout: float = 60.0

    @classmethod
    def get_pipeline(cls):
        logger.debug("Initializing dlt pipeline connection to Postgres.")
        return dlt.pipeline(
            pipeline_name="mock_customers",
            destination=dlt.destinations.postgres(
                credentials=database_url
            ),
            dataset_name="public"
        )

    @staticmethod
    def normalize_customer(customer: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if customer.get("date_of_birth"):
                customer["date_of_birth"] = datetime.strptime(
                    customer["date_of_birth"], "%Y-%m-%d"
                ).date()

            if customer.get("created_at"):
                customer["created_at"] = datetime.fromisoformat(
                    customer["created_at"]
                )

            return customer

        except Exception as e:
            logger.error(f"Failed to normailze customer {customer.get('customer_id', 'UNKNOWN')}: {e}")
            raise

    @classmethod
    async def load_customer_data(cls) -> List[Dict[str, Any]]:
        all_customers: List[Dict[str, Any]] = []
        page: int = 1
        limit: int = 50

        logger.info(f"Starting data fetch from {cls.api_url}")

        try:
            async with httpx.AsyncClient(timeout=cls.timeout) as client:
                while True:
                    logger.info(f"Fetching page {page} (limit: {limit})...")
                    response = await client.get(
                        f"{cls.api_url}/api/customers?page={page}&limit={limit}"
                    )

                    response.raise_for_status()

                    full_response = response.json()
                    data = full_response.get("data", [])

                    if not data:
                        logger.info(f"Page {page} returned empty. Pagination complete.")
                        break

                    logger.debug(f"Normalizing {len(data)} records from page {page}...")
                    normalized_data = [
                        cls.normalize_customer(customer)
                        for customer in data
                    ]

                    all_customers.extend(normalized_data)
                    logger.info(f"Successfully loaded page {page}. Total fetched so far: {len(all_customers)}")
                    page += 1

            return all_customers

        except httpx.HTTPError as http_err:
            logger.error(f"HTTP error occurred during fetch on page {page}: {http_err}")
            return []

        except Exception as e:
            logger.error(f"Unexpected error fetching data on page {page}: {e}")
            return []

    @classmethod
    async def run(cls) -> Dict[str, Any]:
        logger.info("--- STARTING INGESTION JOB ---")
        try:
            data = await cls.load_customer_data()
            total_customers: int = len(data)

            if total_customers == 0:
                logger.warning("No data fetched from source API. Aborting dlt run.")
                return {
                    "status": "warning",
                    "records_processed": 0,
                    "message": "No data fetched from source API"
                }

            logger.info(f"Proceeding to dlt pipeline run with {total_customers} total records.")
            pipeline = cls.get_pipeline()

            load_info = pipeline.run(
                data,
                table_name="customers",
                write_disposition="merge",
                primary_key="customer_id"
            )

            logger.info(f"dlt load complete. Package ID: {load_info.loads_ids}")

            return {
                "status": "success",
                "records_processed": total_customers
            }

        except Exception as e:
            error: str = str(e)

            logger.critical(f"FATAL ERROR during ingestion job: {error}")

            return {
                "status": "error",
                "message": f"Failed ingest mock data into Postgres: {error}"
            }
