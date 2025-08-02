from django.apps import AppConfig
import threading
import os 

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from core.auto_ingest import run_ingestion_if_needed

        def run_async():
            try:
                # ✅ CI environment me skip karna hai ingestion ko
                if os.getenv("CI") != "true":
                    run_ingestion_if_needed()
                else:
                    print("[INFO] Skipping auto-ingestion in CI environment.")
            except Exception as e:
                print(f"[ERROR] Auto ingestion failed: {e}")

        threading.Thread(target=run_async).start()
