# Supabase para AgroIA

AgroIA puede correr en modo demo sin Supabase, pero el modo real espera una
base PostgreSQL en Supabase con estas tablas minimas.

## Configuracion

Define las claves en variables de entorno o en `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://tu-proyecto.supabase.co"
SUPABASE_KEY = "tu-anon-o-publishable-key"
APP_PASSWORD = "password-de-la-app"
ADMIN_PIN = "0000"
```

Si falta alguna clave o falla la conexion, `app.py` entra en modo demo y
usa datos locales de ejemplo.

Para correr el modo demo:

```bash
AGROIA_DATA_BACKEND=demo uv run streamlit run app.py
```

## Tabla `inventario`

Guarda el stock y costo real por insumo. Los datos nutricionales base se leen
desde `bd_agro_v2.json`; Supabase solo sobreescribe stock y precio.

| Columna | Tipo sugerido | Uso |
| --- | --- | --- |
| `id` | `bigint generated always as identity primary key` | Identificador interno |
| `insumo` | `text unique not null` | Llave que debe coincidir con `bd_agro_v2.json` |
| `stock_kg` | `numeric not null default 0` | Existencia disponible |
| `costo_kg` | `numeric not null default 0` | Costo actual por kg |
| `updated_at` | `timestamptz default now()` | Auditoria opcional |

## Tabla `bitacora`

Registra movimientos operativos, compras, mermas y formulaciones.

| Columna | Tipo sugerido | Uso |
| --- | --- | --- |
| `id` | `bigint generated always as identity primary key` | Identificador interno |
| `fecha` | `timestamptz default now()` | Fecha para ordenar historial |
| `accion` | `text not null` | Tipo de movimiento |
| `detalle` | `text not null` | Descripcion legible |
| `gasto_total` | `numeric not null default 0` | Gasto auditado |
| `kilos_procesados` | `numeric not null default 0` | Volumen asociado |

## Tabla `perfiles_lotes`

Guarda los lotes de ganado que el laboratorio carga para formular dietas.

| Columna | Tipo sugerido | Uso |
| --- | --- | --- |
| `id` | `bigint generated always as identity primary key` | Identificador interno |
| `nombre_lote` | `text unique not null` | Nombre mostrado en la app |
| `raza` | `text not null` | Raza seleccionada |
| `genero` | `text not null` | Macho/Hembra |
| `proposito` | `text not null` | Carne, leche u otro objetivo |
| `edad` | `integer not null` | Edad en meses |
| `peso_promedio` | `numeric not null` | Peso promedio en kg |
| `clima_local` | `numeric not null` | Temperatura local usada por la app |
| `costo_salud` | `numeric not null default 0` | Costo sanitario calculado |
| `created_at` | `timestamptz default now()` | Auditoria opcional |

## SQL base sugerido

```sql
create table if not exists inventario (
  id bigint generated always as identity primary key,
  insumo text unique not null,
  stock_kg numeric not null default 0,
  costo_kg numeric not null default 0,
  updated_at timestamptz default now()
);

create table if not exists bitacora (
  id bigint generated always as identity primary key,
  fecha timestamptz default now(),
  accion text not null,
  detalle text not null,
  gasto_total numeric not null default 0,
  kilos_procesados numeric not null default 0
);

create table if not exists perfiles_lotes (
  id bigint generated always as identity primary key,
  nombre_lote text unique not null,
  raza text not null,
  genero text not null,
  proposito text not null,
  edad integer not null,
  peso_promedio numeric not null,
  clima_local numeric not null,
  costo_salud numeric not null default 0,
  created_at timestamptz default now()
);
```

## Datos de ejemplo

Para probar sin tocar Supabase real, no cargues secretos y entra con:

- Password: `demo`
- PIN administrador: `0000`

El modo demo usa un cliente local compatible con el patron actual de Supabase:
`.table().select().insert().update().eq().order().execute()`.