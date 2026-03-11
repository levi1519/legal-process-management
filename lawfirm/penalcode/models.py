"""
models.py — Módulo Penal (COIP)
Sistema de Gestión Legal — Ecuador

IMPORTANTE: Configura en settings.py:
    AUTH_USER_MODEL = 'tu_app.Abogado'
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


# =============================================================================
# MODELO DE USUARIO PERSONALIZADO
# =============================================================================

class Abogado(AbstractUser):
    telefono = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'abogado'
        verbose_name = 'Abogado'
        verbose_name_plural = 'Abogados'

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.username


# =============================================================================
# GEOGRAFÍA
# =============================================================================

class Region(models.Model):
    region_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'region'
        verbose_name = 'Región'
        verbose_name_plural = 'Regiones'

    def __str__(self) -> str:
        return self.nombre


class Provincia(models.Model):
    provincia_id = models.AutoField(primary_key=True)
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        db_column='region_id',
        related_name='provincias',
    )
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'provincia'
        verbose_name = 'Provincia'
        verbose_name_plural = 'Provincias'

    def __str__(self) -> str:
        return self.nombre


class Ciudad(models.Model):
    ciudad_id = models.AutoField(primary_key=True)  # Corregido: id_ciudad -> ciudad_id
    provincia = models.ForeignKey(
        Provincia,
        on_delete=models.CASCADE,
        db_column='provincia_id',
        related_name='ciudades',
    )
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'ciudad'
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'

    def __str__(self) -> str:
        return self.nombre


# =============================================================================
# CATÁLOGOS
# =============================================================================

class TipoDelito(models.Model):
    tipodelito_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    articulo_coip = models.CharField(max_length=50)  # Corregido: obligatorio
    accion_tipo = models.CharField(max_length=100, blank=True)
    plazo_dias_investigacion = models.PositiveIntegerField(null=True, blank=True)
    plazo_instruccion_dias = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'tipodelito'
        verbose_name = 'Tipo de Delito'
        verbose_name_plural = 'Tipos de Delito'

    def __str__(self) -> str:
        return f"{self.nombre} (Art. {self.articulo_coip})"


class TipoProcedimiento(models.Model):
    tipoprocedimiento_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    accion = models.CharField(max_length=200, blank=True)
    tipo_accion = models.CharField(
        max_length=10,
        choices=[('publica', 'Pública'), ('privada', 'Privada')],
        default='publica',
    )

    class Meta:
        db_table = 'tipoprocedimiento'
        verbose_name = 'Tipo de Procedimiento'
        verbose_name_plural = 'Tipos de Procedimiento'

    def __str__(self) -> str:
        return self.nombre


class RolProcesal(models.Model):  # Corregido: Procesar -> Procesal
    rolprocesal_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'rolprocesal'
        verbose_name = 'Rol Procesal'
        verbose_name_plural = 'Roles Procesales'

    def __str__(self) -> str:
        return self.nombre


class CategoriaEvidencia(models.Model):
    categoriaevidencia_id = models.AutoField(primary_key=True)  # Corregido el typo
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'categoriaevidencia'
        verbose_name = 'Categoría de Evidencia'
        verbose_name_plural = 'Categorías de Evidencia'

    def __str__(self) -> str:
        return self.nombre


# =============================================================================
# CLIENTE
# =============================================================================

class Cliente(models.Model):
    cliente_id = models.AutoField(primary_key=True)
    ciudad = models.ForeignKey(
        Ciudad,
        on_delete=models.PROTECT,  # Corregido: Obligatorio por jurisdicción
        db_column='ciudad_id',
        related_name='clientes',
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self) -> str:
        return f"{self.nombre} {self.apellido} — {self.cedula}"


# =============================================================================
# EXPEDIENTE PENAL
# =============================================================================

class ExpedientePenal(models.Model):

    class EstadoExpediente(models.TextChoices):
        DENUNCIA = 'denuncia', 'Denuncia'
        INDAGACION_PREVIA = 'indagacion_previa', 'Indagación Previa'
        INSTRUCCION_FISCAL = 'instruccion_fiscal', 'Instrucción Fiscal'
        EVALUACION_PREPARATORIA = 'evaluacion_preparatoria', 'Evaluación y Preparatoria'
        JUICIO = 'juicio', 'Juicio'
        SENTENCIA = 'sentencia', 'Sentencia'
        ARCHIVADO = 'archivado', 'Archivado'
        ABANDONADO = 'abandonado', 'Abandonado'
        PRESCRITO = 'prescrito', 'Prescrito'

    expedientepenal_id = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        db_column='cliente_id',
        related_name='expedientes',
    )
    # Protegemos catálogos en lugar de SET_NULL para mantener historial legal
    tipodelito = models.ForeignKey(
        TipoDelito,
        on_delete=models.PROTECT,
        db_column='tipodelito_id',
        related_name='expedientes',
    )
    tipoprocedimiento = models.ForeignKey(
        TipoProcedimiento,
        on_delete=models.PROTECT,
        db_column='tipoprocedimiento_id',
        related_name='expedientes',
    )
    ciudad = models.ForeignKey(
        Ciudad,
        on_delete=models.PROTECT,
        db_column='ciudad_id',
        related_name='expedientes',
    )
    abogados = models.ManyToManyField(
        'Abogado',
        through='ExpedienteAbogado',
        related_name='expedientes_penales',
    )
    numero_juicio = models.CharField(max_length=100, blank=True, db_index=True)
    unidad_judicial = models.CharField(max_length=200, blank=True)
    estado = models.CharField(
        max_length=30,
        choices=EstadoExpediente.choices,
        default=EstadoExpediente.DENUNCIA,
        db_index=True,
    )
    fecha_apertura = models.DateField(db_index=True)
    fecha_cierre = models.DateField(null=True, blank=True)
    prescripcion_fecha_limite = models.DateField(null=True, blank=True)  # Corregido el typo
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'expedientepenal'
        verbose_name = 'Expediente Penal'
        verbose_name_plural = 'Expedientes Penales'

    def __str__(self) -> str:
        numero = self.numero_juicio or str(self.expedientepenal_id)
        return f"Expediente #{numero} — {self.cliente}"


# =============================================================================
# TABLA INTERMEDIA EXPEDIENTE ↔ ABOGADO (Mejorada)
# =============================================================================

class ExpedienteAbogado(models.Model):
    expedienteabogado_id = models.AutoField(primary_key=True)
    expediente = models.ForeignKey(
        ExpedientePenal,
        on_delete=models.CASCADE,
        db_column='expediente_id',
        related_name='expediente_abogados',
    )
    abogado = models.ForeignKey(
        Abogado,
        on_delete=models.CASCADE,
        db_column='abogado_id',
        related_name='expediente_abogados',
    )
    # Nuevos campos sugeridos para mejor gestión legal
    rol = models.CharField(max_length=100, blank=True, help_text="Ej: Abogado Principal, Asistente")
    fecha_asignacion = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'expedienteabogado'
        verbose_name = 'Expediente — Abogado'
        verbose_name_plural = 'Expedientes — Abogados'
        constraints = [
            models.UniqueConstraint(fields=['expediente', 'abogado'], name='unique_expediente_abogado')
        ]

    def __str__(self) -> str:
        estado = "Activo" if self.activo else "Inactivo"
        return f"{self.expediente} ↔ {self.abogado} ({estado})"


# =============================================================================
# ETAPA PROCESAL
# =============================================================================

class EtapaProcesal(models.Model):

    class TipoEtapa(models.TextChoices):
        INVESTIGACION_PREVIA = 'investigacion_previa', 'Investigación Previa'
        INSTRUCCION_FISCAL = 'instruccion_fiscal', 'Instrucción Fiscal'
        EVALUACION_PREPARATORIA = 'evaluacion_preparatoria', 'Evaluación y Preparatoria'
        AUDIENCIA_PREPARATORIA = 'audiencia_preparatoria', 'Audiencia Preparatoria'
        JUICIO = 'juicio', 'Juicio'
        SENTENCIA = 'sentencia', 'Sentencia'
        SUSPENSION_CONDICIONAL = 'suspension_condicional', 'Suspensión Condicional'

    class EstadoEtapa(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        ACTIVA = 'activa', 'Activa'
        CERRADA = 'cerrada', 'Cerrada'

    etapaprocesal_id = models.AutoField(primary_key=True)
    expediente = models.ForeignKey(
        ExpedientePenal,
        on_delete=models.CASCADE,
        db_column='expediente_id',
        related_name='etapas',
    )
    tipo_etapa = models.CharField(
        max_length=30,
        choices=TipoEtapa.choices,
    )
    fecha_inicio = models.DateField(db_index=True)
    fecha_limite = models.DateField(null=True, blank=True)
    fecha_cierre = models.DateField(null=True, blank=True)
    estado = models.CharField(
        max_length=10,
        choices=EstadoEtapa.choices,
        default=EstadoEtapa.PENDIENTE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'etapaprocesal'
        verbose_name = 'Etapa Procesal'
        verbose_name_plural = 'Etapas Procesales'
        # Regla de negocio: Un expediente no puede tener dos etapas del mismo tipo activas a la vez
        constraints = [
            models.UniqueConstraint(
                fields=['expediente', 'tipo_etapa'],
                condition=Q(estado='activa'),
                name='unique_etapa_activa_por_expediente'
            )
        ]

    def __str__(self) -> str:
        return f"{self.get_tipo_etapa_display()} — {self.expediente}"


# =============================================================================
# ESCRITO
# =============================================================================

class Escrito(models.Model):
    escrito_id = models.AutoField(primary_key=True)
    expedientepenal = models.ForeignKey(
        ExpedientePenal,
        on_delete=models.CASCADE,
        db_column='expedientepenal_id',
        related_name='escritos',
    )
    etapaprocesal = models.ForeignKey(
        EtapaProcesal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='etapaprocesal_id',
        related_name='escritos',
    )
    abogado = models.ForeignKey(
        Abogado,
        on_delete=models.PROTECT,
        db_column='abogado_id',
        related_name='escritos',
    )
    tipo_escrito = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    fecha = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'escrito'
        verbose_name = 'Escrito'
        verbose_name_plural = 'Escritos'

    def __str__(self) -> str:
        return f"{self.tipo_escrito} ({self.fecha}) — {self.expedientepenal}"


# =============================================================================
# SUJETO PROCESAL
# =============================================================================

class SujetoProcesal(models.Model):  # Corregido: Procesar -> Procesal
    sujetoprocesal_id = models.AutoField(primary_key=True)
    expediente = models.ForeignKey(
        ExpedientePenal,
        on_delete=models.CASCADE,
        db_column='expediente_id',
        related_name='sujetos_procesales',
    )
    rolprocesal = models.ForeignKey(
        RolProcesal,
        on_delete=models.PROTECT,
        db_column='rolprocesal_id',
        related_name='sujetos',
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, blank=True, db_index=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sujetoprocesal'
        verbose_name = 'Sujeto Procesal'
        verbose_name_plural = 'Sujetos Procesales'

    def __str__(self) -> str:
        return f"{self.nombre} {self.apellido} ({self.rolprocesal})"


# =============================================================================
# EVIDENCIA / DOCUMENTO
# =============================================================================

class EvidenciaDocumento(models.Model):
    evidenciadocumento_id = models.AutoField(primary_key=True)
    expediente = models.ForeignKey(
        ExpedientePenal,
        on_delete=models.CASCADE,
        db_column='expediente_id',
        related_name='evidencias',
    )
    escrito = models.ForeignKey(
        Escrito,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='escrito_id',
        related_name='evidencias',
    )
    categoria = models.ForeignKey(
        CategoriaEvidencia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='categoria_id',
        related_name='evidencias',
    )
    titulo = models.CharField(max_length=255)
    # FileField sin null=True (mejor práctica Django/PostgreSQL)
    # Si ya hay registros con null, la migración los convertirá a string vacío
    archivo = models.FileField(upload_to='evidencias/%Y/%m/', blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)  # Corregido: eliminado fecha_subida redundante y typo create_at

    class Meta:
        db_table = 'evidenciadocumento'
        verbose_name = 'Evidencia / Documento'
        verbose_name_plural = 'Evidencias / Documentos'

    def __str__(self) -> str:
        return f"{self.titulo} — {self.expediente}"