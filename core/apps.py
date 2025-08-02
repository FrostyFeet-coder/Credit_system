from django.apps import AppConfig
import threading

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from core.auto_ingest import run_ingestion_if_needed

        def run_async():
            try:
                run_ingestion_if_needed()
            except Exception as e:
                print(f"[ERROR] Auto ingestion failed: {e}")

        threading.Thread(target=run_async).start()
