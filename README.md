# ETL_Python

Pipeline ETL en Python que extrae datos de archivos CSV (clientes, productos, órdenes y detalles de orden), los limpia y valida, y los carga en una base de datos **SQL Server**. Incluye además su propio sistema de auditoría: cada paso del pipeline registra en la base de datos cuántos registros extrajo, cargó y descartó.

## Características

- **Extracción** desde archivos CSV (`customers.csv`, `orders.csv`, `products.csv`, `order_details.csv`).
- **Limpieza y validación** por entidad: elimina duplicados, maneja nulos, normaliza teléfonos/emails/nombres y valida cada registro con modelos de **Pydantic** antes de cargarlo. Los registros inválidos se descartan sin detener el pipeline y quedan disponibles para revisión.
- **Deduplicación contra la base de datos**: antes de insertar, cada cleaner consulta qué registros ya existen (por email, nombre de categoría, país, etc.) para no duplicar datos en corridas repetidas.
- **Carga masiva a SQL Server** usando `bcpandas` (bulk copy), en un orden de dependencias correcto: primero catálogos (`SourceType`, `Status`, `Country`, `Category`), luego dimensiones (`Customer`, `Product`) y por último hechos (`Order`, `OrderDetail`).
- **Auditoría del propio proceso**: cada paso queda registrado en una tabla `DataSource` con la fuente, tipo de fuente (detectado automáticamente), fecha de extracción/carga, cantidad de registros extraídos/cargados/fallidos, estado (`Success`/`Failed`) y el log de error si aplica.
- **Resumen final en consola** con el detalle de cada entidad procesada.

## Conjunto de datos incluido

| Archivo               | Filas   | Descripción                          |
|------------------------|--------:|---------------------------------------|
| `customers.csv`        | 5,000   | Clientes (nombre, email, teléfono, ciudad, país) |
| `products.csv`         | 2,000   | Productos (nombre, categoría, precio, stock) |
| `orders.csv`           | 20,000  | Órdenes (cliente, fecha, estado)     |
| `order_details.csv`    | 60,161  | Líneas de detalle por orden (producto, cantidad, total) |

## Estructura del proyecto

```
ETL_Python/
├── pipeline/
│   └── main.py                    # Orquesta el pipeline completo (extract -> clean -> load)
├── config/
│   ├── config.yaml                # Configuración de conexión a SQL Server
│   └── database.py                # Inicializa y expone las credenciales de conexión (bcpandas)
├── source/
│   ├── Data/                      # CSV de origen (customers, orders, products, order_details)
│   ├── cleaners/                  # Limpieza y validación por entidad
│   │   ├── base_cleaner.py            # Clase base: duplicados, nulos, filtrado contra BD
│   │   ├── customers_cleaner.py
│   │   ├── products_cleaner.py
│   │   ├── order_cleaner.py
│   │   ├── order_detail_cleaner.py
│   │   ├── category_cleaner.py        # Catálogo derivado de products.csv
│   │   ├── country_cleaner.py         # Catálogo derivado de customers.csv
│   │   ├── status_cleaner.py          # Catálogo derivado de orders.csv
│   │   ├── source_type_cleaner.py     # Catálogo fijo (API / CSV / Database)
│   │   └── normalizer.py              # Normalización de teléfono, email y nombres
│   ├── load/                      # Un loader por tabla, todos sobre una base común
│   │   ├── sql_server_loader.py       # Carga masiva genérica vía bcpandas
│   │   ├── customer_loader.py
│   │   ├── product_loader.py
│   │   ├── order_loader.py
│   │   ├── order_detail_loader.py
│   │   ├── category_loader.py
│   │   ├── country_loader.py
│   │   ├── status_loader.py
│   │   ├── source_type_loader.py
│   │   └── data_source_loader.py      # Carga los registros de auditoría del pipeline
│   ├── models/                    # Modelos Pydantic (validación de esquema por entidad)
│   │   ├── customer_model.py, product_model.py, order_model.py, order_detail_model.py
│   │   ├── category_model.py, country_model.py, status_model.py, source_type_model.py
│   │   ├── data_source_model.py       # Modelo del log de auditoría del pipeline
│   │   └── validations.py             # Reglas de validación compartidas (string, email, teléfono)
│   └── utils/
│       ├── process_logger.py          # Registra cada corrida del pipeline en la tabla DataSource
│       └── source_detector.py         # Detecta el tipo de fuente (CSV / Database / API) a partir de una ruta
└── requirements.txt
```

## Requisitos

- Python 3.x
- SQL Server accesible desde la máquina donde corre el pipeline
- [ODBC Driver para SQL Server](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server) instalado (lo requiere `pyodbc`)
- Utilitario **bcp** de SQL Server instalado y disponible en el `PATH` (lo requiere `bcpandas` para la carga masiva)
- Dependencias de Python (`requirements.txt`):
  - `pandas`, `pydantic`, `SQLAlchemy`, `pyodbc`, `bcpandas`, `PyYAML`

## Configuración

1. Clona el repositorio:
   ```bash
   git clone https://github.com/DanielAugusto456/ETL_Python.git
   cd ETL_Python
   ```
2. Crea un entorno virtual e instala las dependencias:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # En Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Crea en tu SQL Server la base de datos y las tablas destino: `Customers`, `Products`, `Orders`, `OrderDetails`, `Category`, `Country`, `Status`, `SourceType` y `DataSource` (tabla de auditoría del pipeline). El repositorio no incluye el script de creación de estas tablas.
4. Ajusta `config/config.yaml` con los datos de tu servidor:
   ```yaml
   database:
     sql_server:
       serverType: "Database engine"
       serverName: "TU_SERVIDOR"
       Authentication: "Windows Authentication"
       DataBase: "TU_BASE_DE_DATOS"
   ```
   > Actualmente el pipeline solo usa `serverName` y `DataBase` de este archivo, y se conecta con autenticación integrada de Windows (`init_db` acepta `username`/`password` opcionales por si se necesita autenticación SQL).

## Uso

Ejecuta el pipeline desde la raíz del proyecto:

```bash
python pipeline/main.py
```

El pipeline:
1. Se conecta a SQL Server con los datos de `config.yaml`.
2. Siembra los catálogos base (`SourceType`, `Status` de proceso).
3. Lee los 4 CSV de `source/Data/`.
4. Limpia, valida y carga en orden: `Category → Status → Country → Customer → Product → Order → OrderDetail`.
5. Registra el resultado de cada paso en la tabla de auditoría `DataSource`.
6. Imprime un resumen final con extraídos/cargados/fallidos por entidad.

## Autor

**Daniel Augusto Martinez Zapata**
📧 MartinezZapata809@gmail.com
🌐 [www.sitioincreible.com](https://www.sitioincreible.com)
