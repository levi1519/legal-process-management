# 🏛️ LegalTech Core — Sistema de Gestión Penal COIP

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0.3-green?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-blue?logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-Proprietary-red)

Sistema backend robusto para la **gestión integral de expedientes penales**, control de plazos procesales y administración de evidencias judiciales, diseñado específicamente para cumplir con la normativa del **Código Orgánico Integral Penal (COIP)** de Ecuador.

Este proyecto constituye el núcleo del sistema LegalTech para despachos de abogados penalistas, proporcionando una interfaz administrativa avanzada para el seguimiento completo del ciclo de vida procesal: desde la denuncia inicial hasta la sentencia o archivo del caso.

---

## 📋 Tabla de Contenidos

- [Características Principales](#-características-principales)
- [Configuraciones Base](#️-configuraciones-base-settingspy)
- [Arquitectura de Datos](#-arquitectura-de-datos-modelspy)
- [Panel de Administración](#-panel-de-administración-adminpy)
- [Instalación y Despliegue Local](#-instalación-y-despliegue-local)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)

---

## ✨ Características Principales

### 🗂️ **Gestión Integral de Expedientes**
- Control completo del **ciclo de vida procesal** según el COIP ecuatoriano:
  - Denuncia → Indagación Previa → Instrucción Fiscal → Evaluación y Preparatoria → Juicio → Sentencia
- Registro de múltiples sujetos procesales por expediente (procesados, víctimas, testigos, peritos)
- Gestión de etapas procesales con control automático de unicidad (una etapa activa por tipo)

### ⏱️ **Control de Plazos y Alertas Judiciales**
- **Filtro dinámico de prescripción** con 3 estados:
  - ✅ Vigente
  - ⚠️ Próximo a prescribir (< 30 días)
  - ❌ Prescrito
- Cálculo automático de **días transcurridos** desde la apertura del caso
- Campos específicos para plazos de investigación e instrucción según tipo de delito

### 📄 **Administración Documental**
- Almacenamiento organizado de evidencias y documentos judiciales
- Sistema de categorización de evidencias (testimonial, documental, pericial, etc.)
- Previsualización y descarga directa de archivos desde el panel administrativo
- Vinculación de documentos a etapas procesales y escritos específicos

### ⚡ **Rendimiento Optimizado**
- Base de datos con **índices estratégicos** (`db_index=True`) en:
  - `ExpedientePenal.numero_juicio` (búsquedas frecuentes)
  - `ExpedientePenal.estado` (filtrado de casos activos/archivados)
  - `ExpedientePenal.fecha_apertura` (reportes cronológicos)
  - `Cliente.cedula` y `SujetoProcesal.cedula` (identificación rápida)
  - `EtapaProcesal.fecha_inicio` y `Escrito.fecha` (ordenamiento temporal)

### 🛡️ **Integridad Referencial Estricta**
- Políticas de borrado diseñadas para contexto legal:
  - `PROTECT` en catálogos (TipoDelito, TipoProcedimiento) → Preserva historial legal
  - `CASCADE` en relaciones secundarias (Etapas, Escritos) → Limpieza automática
  - `SET_NULL` en referencias opcionales → Mantiene datos históricos

### 👥 **Modelo de Usuario Personalizado**
- Sistema de autenticación basado en modelo `Abogado` (extiende `AbstractUser`)
- Gestión de equipos legales mediante tabla intermedia `ExpedienteAbogado`
- Registro de roles y fechas de asignación por expediente

---

## ⚙️ Configuraciones Base (`settings.py`)

### **Usuario Personalizado**
```python
AUTH_USER_MODEL = 'penalcode.Abogado'
```
El sistema utiliza un modelo de usuario extendido que incluye campos específicos para abogados (teléfono, datos de contacto profesional).

### **Localización Ecuador**
```python
LANGUAGE_CODE = 'es-ec'
TIME_ZONE = 'America/Guayaquil'  # Zona horaria oficial de Ecuador
USE_I18N = True
USE_TZ = True
```

### **Gestión de Archivos (Media)**
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```
Los archivos subidos (evidencias, documentos procesales) se almacenan localmente en la carpeta `media/` con estructura jerárquica por fecha (`evidencias/%Y/%m/`).

### **Base de Datos**
El proyecto está configurado inicialmente con **SQLite** para desarrollo, pero está optimizado para **PostgreSQL** en producción:
- Campos `FileField` sin `null=True` (compatibilidad PostgreSQL)
- Uso de `BigAutoField` para claves primarias
- Constraints de base de datos (UniqueConstraint con condiciones)

---

## 🗄️ Arquitectura de Datos (`models.py`)

El sistema está estructurado en **4 capas conceptuales**:

### **1. Geografía y Jurisdicción**
Estructura jerárquica para determinar competencia territorial:

| Modelo | Descripción |
|--------|-------------|
| `Region` | 4 regiones del Ecuador (Costa, Sierra, Oriente, Insular) |
| `Provincia` | 24 provincias con relación a región |
| `Ciudad` | Ciudades/cantones con relación a provincia |

### **2. Catálogos del COIP**
Tablas maestras de clasificación legal:

| Modelo | Función |
|--------|---------|
| `TipoDelito` | Delitos del COIP con artículo, plazos de investigación e instrucción |
| `TipoProcedimiento` | Procedimientos ordinarios, abreviados, directos, etc. |
| `RolProcesal` | Roles de sujetos procesales (Procesado, Víctima, Testigo, Perito, etc.) |
| `CategoriaEvidencia` | Clasificación de medios probatorios |

**Decisión de diseño**: Los tipos de escrito (`tipo_escrito`) se manejan como `CharField` para flexibilidad en el MVP, sin tabla catálogo rígida.

### **3. Gestión de Clientes y Expedientes**

#### **Cliente**
Persona natural que contrata servicios legales:
- Datos de identificación (cédula única)
- Información de contacto
- Vinculación obligatoria a ciudad (jurisdicción)

#### **ExpedientePenal** (Entidad Central)
Representa el caso judicial completo:

```python
class ExpedientePenal(models.Model):
    # Estados del ciclo procesal
    ESTADOS = [
        'denuncia', 'indagacion_previa', 'instruccion_fiscal',
        'evaluacion_preparatoria', 'juicio', 'sentencia',
        'archivado', 'abandonado', 'prescrito'
    ]
    
    # Campos clave
    numero_juicio       # db_index=True
    estado              # db_index=True
    fecha_apertura      # db_index=True
    prescripcion_fecha_limite
    unidad_judicial
    
    # Relaciones
    cliente → Cliente (PROTECT)
    tipodelito → TipoDelito (PROTECT)
    tipoprocedimiento → TipoProcedimiento (PROTECT)
    ciudad → Ciudad (PROTECT)
    abogados → ManyToMany through ExpedienteAbogado
```

**Restricciones**:
- Los catálogos usan `PROTECT` para evitar borrado accidental de clasificaciones en uso
- El cliente está protegido (`PROTECT`) para mantener integridad histórica

### **4. Seguimiento Procesal**

#### **EtapaProcesal**
Control granular de fases del proceso:
- 7 tipos de etapa (investigación previa, instrucción, audiencias, juicio, etc.)
- Estados: Pendiente / Activa / Cerrada
- **Constraint único**: Solo una etapa del mismo tipo puede estar activa por expediente

#### **Escrito**
Registro de actuaciones procesales:
- Demandas, contestaciones, alegatos, recursos, etc.
- Vinculación opcional a etapa procesal (`SET_NULL`)
- Autoría rastreada (abogado responsable con `PROTECT`)
- Fecha indexada para ordenamiento cronológico

#### **SujetoProcesal**
Partes involucradas en el proceso (distintas al cliente):
- Procesados, coacusados, víctimas, testigos, peritos
- Cédula indexada (`db_index=True`) para búsquedas rápidas

#### **EvidenciaDocumento**
Medios probatorios y documentación judicial:
- Categorización por tipo de evidencia
- Almacenamiento de archivos digitales (`FileField`)
- Vinculación a expediente (obligatoria) y escrito (opcional)

---

## 🎛️ Panel de Administración (`admin.py`)

El sistema **funciona completamente a través del Panel de Administración de Django**, optimizado para la productividad diaria del abogado.

### **Características Avanzadas Implementadas**

#### **1. Gestión Integrada con Inlines**
El `ExpedientePenalAdmin` permite administrar desde una sola vista:
- ✅ Asignación de abogados al caso (`ExpedienteAbogadoInline`)
- ✅ Sujetos procesales involucrados (`SujetoProcesalInline`)
- ✅ Etapas procesales (`EtapaProcesalInline`)
- ✅ Evidencias y documentos (`EvidenciaDocumentoInline`)

```python
inlines = [
    ExpedienteAbogadoInline,
    SujetoProcesalInline,
    EtapaProcesalInline,
    EvidenciaDocumentoInline
]
```

#### **2. Autocompletado Inteligente**
Para evitar problemas de rendimiento con catálogos masivos:
```python
autocomplete_fields = ['cliente', 'tipodelito', 'ciudad', 'abogado', 'expediente']
```
Todos los modelos necesarios tienen configurado `search_fields` para habilitar búsquedas AJAX.

#### **3. Filtros Personalizados**

##### **Filtro de Estado de Prescripción** (`EstadoPrescripcionFilter`)
Clasificación dinámica basada en fecha límite:
- **Vigente**: Casos con fecha de prescripción futura
- **Próximo a prescribir**: Menos de 30 días restantes ⚠️
- **Prescrito**: Fecha límite vencida

##### **Filtros Jerárquicos**
```python
list_filter = (
    'estado',
    EstadoPrescripcionFilter,
    'tipodelito',
    'ciudad__provincia__region',  # Filtro geográfico multinivel
    'fecha_apertura'
)
```

#### **4. Columnas Calculadas**

##### **Días Transcurridos** (en `ExpedientePenalAdmin`)
```python
@admin.display(description='Días Transcurridos')
def dias_transcurridos(self, obj):
    if obj.fecha_cierre:
        return (obj.fecha_cierre - obj.fecha_apertura).days
    return (timezone.now().date() - obj.fecha_apertura).days
```

##### **Vista Previa de Archivos** (en `EvidenciaDocumentoAdmin`)
```python
@admin.display(description='Enlace')
def preview_archivo(self, obj):
    if obj.archivo:
        return format_html('<a href="{}" target="_blank">📄 Descargar</a>', obj.archivo.url)
    return "-"
```

#### **5. Acciones Masivas**

##### **Marcar Expedientes como Archivados**
```python
@admin.action(description='Marcar como Archivado (Cerrar caso)')
def marcar_archivado(self, request, queryset):
    updated = queryset.update(
        estado='archivado',
        fecha_cierre=timezone.now().date()
    )
    self.message_user(request, f'{updated} expediente(s) archivado(s)')
```

#### **6. Campos de Solo Lectura**
Todos los modelos protegen campos de auditoría:
```python
readonly_fields = ('created_at', 'updated_at')
```

#### **7. Jerarquía Temporal**
Navegación cronológica en listados principales:
```python
date_hierarchy = 'fecha_apertura'  # en ExpedientePenal
date_hierarchy = 'fecha'           # en Escrito
```

### **Modelos Registrados (13)**

| ModelAdmin | Funcionalidad Destacada |
|------------|-------------------------|
| `AbogadoAdmin` | Extiende `UserAdmin` de Django + campo teléfono |
| `RegionAdmin` | Búsqueda por nombre |
| `ProvinciaAdmin` | Filtro por región |
| `CiudadAdmin` | Filtro jerárquico por región/provincia |
| `TipoDelitoAdmin` | Ordenamiento por artículo COIP |
| `TipoProcedimientoAdmin` | Lista tipo de acción (pública/privada) |
| `RolProcesalAdmin` | Búsqueda de roles |
| `CategoriaEvidenciaAdmin` | Búsqueda de categorías |
| `EtapaProcesalAdmin` | Filtros por tipo y estado de etapa |
| `ClienteAdmin` | Filtro geográfico + búsqueda por cédula |
| `ExpedientePenalAdmin` | **Hub central** con inlines y filtros avanzados |
| `EscritoAdmin` | Búsqueda por expediente + autocompletado |
| `SujetoProcesalAdmin` | Búsqueda por cédula/nombre |
| `EvidenciaDocumentoAdmin` | Preview de archivos + categorización |

### **Personalización del Sitio**
```python
admin.site.site_header = "LegalTech Ecuador — Gestión COIP"
admin.site.site_title = "Portal Legal"
admin.site.index_title = "Panel de Control de Juicios y Expedientes"
```

---

## 🚀 Instalación y Despliegue Local

### **Prerrequisitos**
- Python 3.13+
- pip (gestor de paquetes de Python)
- Git

### **Paso 1: Clonar el Repositorio**
```bash
git clone <URL_DEL_REPOSITORIO>
cd LawFirm
```

### **Paso 2: Crear Entorno Virtual**
```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux/macOS
python3 -m venv env
source env/bin/activate
```

### **Paso 3: Instalar Dependencias**
```bash
pip install -r requirements.txt
```

**Dependencias principales**:
- Django 6.0.3
- asgiref 3.11.1
- sqlparse 0.5.5
- tzdata 2025.3

### **Paso 4: Configurar Base de Datos**
```bash
cd lawfirm
python manage.py makemigrations
python manage.py migrate
```

Esto creará las siguientes migraciones:
- `0001_initial.py` → Estructura completa de tablas
- `0002_add_performance_indexes.py` → Índices de rendimiento

### **Paso 5: Crear Superusuario**
```bash
python manage.py createsuperuser
```

Ingresa los datos solicitados:
- Username (nombre de usuario del abogado)
- Email
- Password (contraseña segura)

### **Paso 6: Ejecutar Servidor de Desarrollo**
```bash
python manage.py runserver
```

### **Paso 7: Acceder al Panel de Administración**
1. Abre el navegador en: **http://127.0.0.1:8000/admin/**
2. Inicia sesión con las credenciales del superusuario
3. Comienza a gestionar expedientes penales

---

## 📁 Estructura del Proyecto

```
LawFirm/
│
├── env/                          # Entorno virtual (no versionado)
│
├── lawfirm/                      # Proyecto Django principal
│   ├── manage.py                 # Script de gestión de Django
│   ├── db.sqlite3                # Base de datos SQLite (desarrollo)
│   │
│   ├── lawfirm/                  # Configuración del proyecto
│   │   ├── __init__.py
│   │   ├── settings.py           # ⚙️ Configuraciones globales
│   │   ├── urls.py               # Rutas principales (solo admin)
│   │   ├── wsgi.py               # Punto de entrada WSGI
│   │   └── asgi.py               # Punto de entrada ASGI
│   │
│   └── penalcode/                # Aplicación principal
│       ├── __init__.py
│       ├── apps.py               # Configuración de la app
│       ├── models.py             # 🗄️ Modelos de datos (13 modelos)
│       ├── admin.py              # 🎛️ Panel administrativo (13 ModelAdmin)
│       ├── tests.py              # Suite de pruebas
│       └── migrations/           # Historial de migraciones
│           ├── 0001_initial.py
│           └── 0002_add_performance_indexes.py
│
├── media/                        # Archivos subidos (evidencias)
│   └── evidencias/               # Organizado por año/mes
│
├── requirements.txt              # Dependencias del proyecto
└── README.md                     # Este archivo
```

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | 3.13 | Lenguaje base |
| **Django** | 6.0.3 | Framework web full-stack |
| **SQLite** | 3.x | Base de datos de desarrollo |
| **PostgreSQL** | 12+ | Base de datos de producción (recomendado) |

### **Librerías Python**
- `asgiref` → Soporte para servidores ASGI
- `sqlparse` → Parser SQL para migraciones
- `tzdata` → Base de datos de zonas horarias

---

## 📊 Modelo Entidad-Relación (Conceptual)

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│   Abogado   │◄────┐   │ ExpedientePenal  │────────►│   Cliente   │
└─────────────┘     │   └──────────────────┘         └─────────────┘
                    │            │
                    │            ├──────► TipoDelito
┌─────────────────┐ │            ├──────► TipoProcedimiento
│ExpedienteAbogado│─┘            └──────► Ciudad
└─────────────────┘                       
                                  │
                   ┌──────────────┼──────────────┐
                   │              │              │
            ┌──────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
            │EtapaProcesal│ │  Escrito │ │   Sujeto   │
            └─────────────┘ └──────────┘ │  Procesal  │
                                │         └────────────┘
                                │
                         ┌──────▼──────┐
                         │  Evidencia  │
                         │  Documento  │
                         └─────────────┘
```

---

## 📝 Notas Técnicas

### **Decisiones de Arquitectura**

1. **Modelo de Usuario Personalizado**  
   Se utilizó `AbstractUser` en lugar de un perfil separado para mantener la integridad de autenticación de Django.

2. **Políticas de Borrado**  
   - `PROTECT` en catálogos → Evita pérdida de clasificaciones legales históricas
   - `CASCADE` en relaciones secundarias → Limpieza automática al borrar expedientes
   - `SET_NULL` en referencias opcionales → Preserva datos aunque se borre la referencia

3. **Campos `blank=True` sin `null=True`**  
   En campos de texto, se usa solo `blank=True` para evitar dos representaciones de "vacío" en PostgreSQL (NULL vs string vacío).

4. **FileField sin `null=True`**  
   Los archivos vacíos se representan como string vacío `''` en lugar de `NULL` para compatibilidad con PostgreSQL.

5. **Índices Estratégicos**  
   Se agregaron índices solo en campos con alta frecuencia de búsqueda para equilibrar rendimiento y espacio en disco.

### **Migración a PostgreSQL**

Para producción, actualizar `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'legaltech_db',
        'USER': 'postgres_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Instalar adaptador PostgreSQL:
```bash
pip install psycopg2-binary
```

---

## 👥 Autoría y Contexto Académico

Este proyecto constituye la **base técnica** de una tesis de Ingeniería de Software enfocada en:
- Aplicación de patrones de diseño en sistemas legales
- Optimización de bases de datos para contextos judiciales
- Diseño de interfaces administrativas centradas en el usuario (abogado)

**Desarrollado para**: Despacho de abogados especializado en Derecho Penal (Ecuador)  
**Marco Legal**: Código Orgánico Integral Penal (COIP) vigente  
**Fecha de Desarrollo**: Marzo 2026  

---

## 📄 Licencia

Este proyecto es **software propietario** desarrollado con fines comerciales y académicos. Todos los derechos reservados.

---

## 📧 Contacto y Soporte

Para consultas sobre implementación, personalización o soporte técnico, contactar al equipo de desarrollo del proyecto.

---

**Versión del Sistema**: 1.0.0 (MVP Backend)  
**Última Actualización**: 11 de marzo de 2026
