#!/bin/bash

# Colores para la terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuración por defecto
DEFAULT_DB_NAME="coip_system"
DEFAULT_DB_USER="postgres"
DEFAULT_DB_HOST="localhost"
DEFAULT_DB_PORT="5432"
DEFAULT_DB_PASSWORD="postgres"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}     SETUP COIP SYSTEM${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Función para mostrar mensajes de éxito
success() {
    echo -e "${GREEN}[✓] $1${NC}"
}

# Función para mostrar errores
error() {
    echo -e "${RED}[✗] $1${NC}"
}

# Función para mostrar advertencias
warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

# Función para mostrar información
info() {
    echo -e "${CYAN}[i] $1${NC}"
}

# 1. Verificar versión de Python
echo -e "${MAGENTA}1. Verificando Python...${NC}"
if ! command -v python &> /dev/null; then
    error "Python no está instalado"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1)
success "Python encontrado: $PYTHON_VERSION"

MIN_VERSION=3.8
PYTHON_MAJOR=$(python -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]; }; then
    error "Se requiere Python 3.8 o superior"
    exit 1
fi

success "Versión de Python compatible"
echo ""

# 2. Verificar PostgreSQL
echo -e "${MAGENTA}2. Verificando PostgreSQL...${NC}"
POSTGRES_AVAILABLE=false
if command -v psql &> /dev/null; then
    success "PostgreSQL encontrado: $(psql --version)"
    POSTGRES_AVAILABLE=true
else
    warning "PostgreSQL no está instalado o no está en el PATH."
    warning "Los pasos de base de datos serán omitidos."
    warning "Para instalar PostgreSQL visita: https://www.postgresql.org/download/"
    info "Puedes continuar con SQLite para desarrollo local."
fi
echo ""

# 3. Configurar datos de la Base de Datos
echo -e "${MAGENTA}3. Configurando Base de Datos...${NC}"

if [ "$POSTGRES_AVAILABLE" = false ]; then
    warning "PostgreSQL no disponible — saltando configuración de BD."
    echo ""
else
echo ""

echo -ne "${CYAN}Nombre de la BD [default: ${DEFAULT_DB_NAME}]: ${NC}"
read -r DB_NAME
DB_NAME=${DB_NAME:-$DEFAULT_DB_NAME}

echo -ne "${CYAN}Usuario de PostgreSQL [default: ${DEFAULT_DB_USER}]: ${NC}"
read -r DB_USER
DB_USER=${DB_USER:-$DEFAULT_DB_USER}

echo -ne "${CYAN}Host de PostgreSQL [default: ${DEFAULT_DB_HOST}]: ${NC}"
read -r DB_HOST
DB_HOST=${DB_HOST:-$DEFAULT_DB_HOST}

echo -ne "${CYAN}Puerto de PostgreSQL [default: ${DEFAULT_DB_PORT}]: ${NC}"
read -r DB_PORT
DB_PORT=${DB_PORT:-$DEFAULT_DB_PORT}

echo -ne "${CYAN}Contraseña de PostgreSQL [default: ${DEFAULT_DB_PASSWORD}]: ${NC}"
read -rs DB_PASSWORD
DB_PASSWORD=${DB_PASSWORD:-$DEFAULT_DB_PASSWORD}
echo ""

info "Configuración de BD:"
echo "  - Nombre: $DB_NAME"
echo "  - Usuario: $DB_USER"
echo "  - Host: $DB_HOST"
echo "  - Puerto: $DB_PORT"
echo ""

export PGPASSWORD="$DB_PASSWORD"

info "Verificando conexión a PostgreSQL..."
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "SELECT version();" &> /dev/null; then
    success "Conexión a PostgreSQL exitosa"
else
    error "No se pudo conectar a PostgreSQL. Verifica que el servidor esté corriendo y los datos sean correctos."
    exit 1
fi

# Verificar si la BD existe
DB_EXISTS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';" 2>/dev/null)

if [ "$DB_EXISTS" = "1" ]; then
    warning "La base de datos '$DB_NAME' ya existe"
    echo -ne "${YELLOW}¿Desea reiniciarla? (perdera todos los datos) [s/N]: ${NC}"
    read -r response
    if [[ "$response" =~ ^[Ss]$ ]]; then
        info "Eliminando base de datos existente..."
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "DROP DATABASE IF EXISTS \"$DB_NAME\";" 2>/dev/null
        if [ $? -ne 0 ]; then
            error "No se pudo eliminar la base de datos. Puede haber conexiones activas."
            exit 1
        fi
        success "Base de datos eliminada"
        
        info "Creando base de datos '$DB_NAME'..."
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "CREATE DATABASE \"$DB_NAME\";" 2>/dev/null
        if [ $? -eq 0 ]; then
            success "Base de datos '$DB_NAME' creada exitosamente"
        else
            error "Error al crear la base de datos"
            exit 1
        fi
    else
        info "Mantendremos la base de datos existente"
    fi
else
    info "Creando base de datos '$DB_NAME'..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "CREATE DATABASE \"$DB_NAME\";" 2>/dev/null
    if [ $? -eq 0 ]; then
        success "Base de datos '$DB_NAME' creada exitosamente"
    else
        error "Error al crear la base de datos"
        exit 1
    fi
fi
echo ""

# fi — fin bloque PostgreSQL disponible
fi
echo ""

# Exportar variables de entorno para Django (solo si PostgreSQL disponible)
if [ "$POSTGRES_AVAILABLE" = true ]; then
    export DB_NAME="$DB_NAME"
    export DB_USER="$DB_USER"
    export DB_HOST="$DB_HOST"
    export DB_PORT="$DB_PORT"
    export DB_PASSWORD="$DB_PASSWORD"
fi

# 5. Instalar dependencias
echo -e "${MAGENTA}5. Instalando dependencias...${NC}"

# Buscar y activar el entorno virtual
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
    success "Entorno virtual (venv/Scripts/activate) activado"
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    success "Entorno virtual (venv/bin/activate) activado"
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
    success "Entorno virtual (.venv/Scripts/activate) activado"
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    success "Entorno virtual (.venv/bin/activate) activado"
elif [ -f "env/Scripts/activate" ]; then
    source env/Scripts/activate
    success "Entorno virtual (env/Scripts/activate) activado"
elif [ -f "env/bin/activate" ]; then
    source env/bin/activate
    success "Entorno virtual (env/bin/activate) activado"
elif [ -d "venv" ] || [ -d ".venv" ] || [ -d "env" ]; then
    warning "Entorno virtual encontrado pero no se pudo activar"
else
    warning "No se encontró entorno virtual"
fi

if [ -f "requirements.txt" ]; then
    info "Instalando dependencias de requirements.txt..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        success "Dependencias instaladas"
    else
        error "Error al instalar dependencias"
        exit 1
    fi
else
    warning "No se encontró requirements.txt"
fi
echo ""

# 6. Crear migraciones
echo -e "${MAGENTA}6. Creando migraciones...${NC}"
if [ "$POSTGRES_AVAILABLE" = false ]; then
    warning "PostgreSQL no disponible — saltando migraciones."
    info "Instala PostgreSQL y vuelve a ejecutar setup.sh para aplicar migraciones."
    echo ""
else
if [ -f "manage.py" ]; then
    python manage.py makemigrations
    if [ $? -eq 0 ]; then
        success "Migraciones creadas"
    else
        error "Error al crear migraciones"
        exit 1
    fi
else
    error "No se encontró manage.py"
    exit 1
fi

info "Aplicando migraciones..."
python manage.py migrate
if [ $? -eq 0 ]; then
    success "Migraciones aplicadas"
else
    error "Error al aplicar migraciones"
    exit 1
fi
echo ""

# 7. Crear superusuario
echo -e "${MAGENTA}7. Creando superusuario...${NC}"
info "Ejecutando createsuperuser..."
python manage.py createsuperuser
if [ $? -eq 0 ]; then
    success "Superusuario creado"
else
    warning "No se pudo crear el superusuario (puede ser cancelado por el usuario)"
fi
echo ""
fi  # fin bloque PostgreSQL para migraciones

# Resumen final
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}     SETUP COMPLETADO${NC}"
echo -e "${GREEN}========================================${NC}"
success "El sistema está listo para usar"
info "Ejecuta: python manage.py runserver"
echo ""
