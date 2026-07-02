import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT_DIR / "source"
DATA_DIR = SOURCE_DIR / "Data"

for path in (ROOT_DIR, SOURCE_DIR, SOURCE_DIR / "models", SOURCE_DIR / "cleaners"):
    sys.path.insert(0, str(path))

from config.database import init_db

from source.cleaners.category_cleaner import CategoryCleaner
from source.cleaners.status_cleaner import StatusCleaner
from source.cleaners.country_cleaner import CountryCleaner
from source.cleaners.source_type_cleaner import SourceTypeCleaner
from source.cleaners.customers_cleaner import CustomersCleaner
from source.cleaners.products_cleaner import ProductsCleaner
from source.cleaners.order_cleaner import OrdersCleaner
from source.cleaners.order_detail_cleaner import OrderDetailCleaner

from source.load.category_loader import CategoryLoader
from source.load.status_loader import StatusLoader
from source.load.country_loader import CountryLoader
from source.load.source_type_loader import SourceTypeLoader
from source.load.customer_loader import CustomerLoader
from source.load.product_loader import ProductLoader
from source.load.order_loader import OrderLoader
from source.load.order_detail_loader import OrderDetailLoader

from source.utils.process_logger import ProcessLogger

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("pipeline")

PROCESS_STATUSES = ["Success", "Failed"]

def load_db_config() -> dict:
    config_path = ROOT_DIR / "config" / "config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config["database"]["sql_server"]

def seed_catalogs():
    logger.info("--- Seed: SourceType ---")
    SourceTypeLoader().load(SourceTypeCleaner().clean())

    logger.info("--- Seed: Status (Success/Failed para el log del proceso) ---")
    process_statuses_raw = pd.DataFrame({"Status": PROCESS_STATUSES})
    StatusLoader().load(StatusCleaner().clean(process_statuses_raw))

def run_step(name: str, cleaner, loader, raw_data: pd.DataFrame, source_path: Path) -> None:
    process_logger = ProcessLogger()
    extracted_at = datetime.now()
    records_extracted = len(raw_data)

    try:
        logger.info(f"--- {name}: limpiando ---")
        clean_data = cleaner.clean(raw_data)

        invalid = cleaner.get_invalid_records()
        if invalid:
            logger.warning(f"{name}: {len(invalid)} registro(s) inválido(s) descartado(s).")

        logger.info(f"--- {name}: cargando ---")
        loader.load(clean_data)

        process_logger.log(
            source_name=name,
            source_descriptor=str(source_path),
            extracted_at=extracted_at,
            loaded_at=datetime.now(),
            records_extracted=records_extracted,
            records_loaded=len(clean_data),
            records_failed=len(invalid),
            status_name="Success",
        )

    except Exception as e:
        logger.error(f"{name}: falló el proceso -> {e}")
        process_logger.log(
            source_name=name,
            source_descriptor=str(source_path),
            extracted_at=extracted_at,
            loaded_at=datetime.now(),
            records_extracted=records_extracted,
            records_loaded=0,
            records_failed=records_extracted,
            status_name="Failed",
            error_log=traceback.format_exc(),
        )
        raise

def run_pipeline():
    db_config = load_db_config()
    init_db(
        server=db_config["serverName"],
        database=db_config["DataBase"],
    )

    seed_catalogs()

    customers_path = DATA_DIR / "customers.csv"
    orders_path = DATA_DIR / "orders.csv"
    products_path = DATA_DIR / "products.csv"
    order_details_path = DATA_DIR / "order_details.csv"

    customers_raw = pd.read_csv(customers_path)
    orders_raw = pd.read_csv(orders_path)
    products_raw = pd.read_csv(products_path)
    order_details_raw = pd.read_csv(order_details_path)

    run_step("Category", CategoryCleaner(), CategoryLoader(), products_raw, products_path)
    run_step("Status", StatusCleaner(), StatusLoader(), orders_raw, orders_path)
    run_step("Country", CountryCleaner(), CountryLoader(), customers_raw, customers_path)

    run_step("Customer", CustomersCleaner(), CustomerLoader(), customers_raw, customers_path)
    run_step("Product", ProductsCleaner(), ProductLoader(), products_raw, products_path)

    run_step("Order", OrdersCleaner(), OrderLoader(), orders_raw, orders_path)
    run_step("OrderDetail", OrderDetailCleaner(), OrderDetailLoader(), order_details_raw, order_details_path)

    logger.info("Pipeline finalizado.")

if __name__ == "__main__":
    run_pipeline()
