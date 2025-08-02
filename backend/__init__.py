from .celery import app as celery_app
__all__ = ['celery_app']

def trigger_excel_ingestion():
    try:
        from core.auto_ingest import run_ingestion_if_needed
        run_ingestion_if_needed()
    except Exception as e:
        print(f"[ERROR] Auto ingestion failed: {e}")

trigger_excel_ingestion()
