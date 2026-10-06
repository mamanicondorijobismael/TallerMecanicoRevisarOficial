from django.apps import AppConfig


class OrdenesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ordenes'
    verbose_name = 'Ordenes de Trabajo'

    def ready(self):
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS "ordenes_repuestoexterno" (
                        "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                        "descripcion" varchar(200) NOT NULL,
                        "proveedor" varchar(100) NOT NULL DEFAULT '',
                        "cantidad" integer unsigned NOT NULL DEFAULT 1,
                        "precio_unitario" decimal NOT NULL DEFAULT 0,
                        "orden_id" bigint NOT NULL REFERENCES "ordenes_ordentrabajo" ("id") DEFERRABLE INITIALLY DEFERRED
                    );
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS "ordenes_repuestoexterno_orden_id_idx" 
                    ON "ordenes_repuestoexterno" ("orden_id");
                """)
        except Exception:
            pass

