"""
models.py — Módulo Penal (COIP)
Sistema de Gestión Legal — Ecuador
"""
from django.db import models
from apps.core.models import ModelBase, Ciudad
from apps.security.models import User

# =============================================================================
# CATÁLOGOS
# =============================================================================
class TipoDelito(ModelBase):
    ACCION_TIPO_CHOICE = (
        ('publica', 'Pública'),
        ('privada', 'Privada'),
    )
     
    id = models.AutoField(primary_key=True)
    nombre = models.CharField('Nombre', max_length=200, unique=True)
    articulo_coip = models.CharField('Artículo COIP', max_length=50, unique=True)
    accion_tipo = models.CharField('Tipo de Acción', max_length=100, blank=True, choices=ACCION_TIPO_CHOICE)
    plazo_dias_investigacion = models.PositiveIntegerField('Plazo Días Investigación', null=True, blank=True)
    plazo_instruccion_dias = models.PositiveIntegerField('Plazo Días Instruccion', null=True, blank=True)

    class Meta:
        verbose_name = 'Tipo de Delito'
        verbose_name_plural = 'Tipos de Delito'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre'], name='idx_tipodelito_nombre'),
            models.Index(fields=['articulo_coip'], name='idx_tipodelito_articulo_coip'),
        ]

    def __str__(self) -> str:
        return f"{self.nombre} (Art. {self.articulo_coip})"


class TipoProcedimiento(ModelBase):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField('Nombre', max_length=200, unique=True)
    accion = models.CharField('Acción', max_length=200, blank=True)
    tipo_accion = models.CharField('Tipo de Acción', max_length=10, choices=[('publica', 'Pública'), ('privada', 'Privada')], default='publica')

    def __str__(self):
        return f'Tipo de Procedimiento: {self.nombre}'

    class Meta:
        verbose_name = 'Tipo de Procedimiento'
        verbose_name_plural = 'Tipos de Procedimiento'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre'], name='idx_tipoprocedimiento_nombre'),
        ]


class RolProcesal(ModelBase):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField('Nombre', max_length=200, unique=True)

    def __str__(self):
        return f'Rol Procesal: {self.nombre}'

    class Meta:
        verbose_name = 'Rol Procesal'
        verbose_name_plural = 'Roles Procesales'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre'], name='idx_rolprocesal_nombre'),
        ]


class CategoriaEvidencia(ModelBase):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField('Nombre', max_length=200, unique=True)

    def __str__(self):
        return f'Categoria Evidencia: {self.nombre}'

    class Meta:
        verbose_name = 'Categoría de Evidencia'
        verbose_name_plural = 'Categorías de Evidencia'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre'], name='idx_categoriaevidencia_nombre'),
        ]


class RolExpediente(ModelBase):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField('Nombre', max_length=200, unique=True)

    def __str__(self):
        return f'Rol de Expediente: {self.nombre}'

    class Meta:
        verbose_name = 'Rol de Expediente'
        verbose_name_plural = 'Roles de Expediente'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre'], name='idx_rolexpediente_nombre'),
        ]


class TipoEscrito(ModelBase):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField('Nombre', max_length=200, unique=True)

    def __str__(self):
        return f'Tipo de Escrito: {self.nombre}'

    class Meta:
        verbose_name = 'Tipo de Escrito'
        verbose_name_plural = 'Tipos de Escrito'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre'], name='idx_tipoescrito_nombre'),
        ]


# =============================================================================
# CLIENTE
# =============================================================================

class Cliente(ModelBase):
    id = models.AutoField(primary_key=True)
    ciudad = models.ForeignKey(
        Ciudad,
        on_delete=models.PROTECT,  # Corregido: Obligatorio por jurisdicción
        db_column='ciudad_id',
        related_name='clientes',
        verbose_name='Ciudad'
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)

    @property
    def get_full_name(self):
        return f'{self.nombre} {self.apellido}'.strip()

    def __str__(self):
        return f'Cliente: {self.get_full_name} - {self.cedula}'

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre'], name='idx_cliente_nombre'),
            models.Index(fields=['apellido'], name='idx_cliente_apellido'),
            models.Index(fields=['cedula'], name='idx_cliente_cedula'),
        ]


# =============================================================================
# EXPEDIENTE PENAL
# =============================================================================

class ExpedientePenal(ModelBase):
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
    
    id = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        db_column='cliente_id',
        related_name='expedientes',
        verbose_name='Cliente'
    )
    # Protegemos catálogos en lugar de SET_NULL para mantener historial legal
    tipodelito = models.ForeignKey(
        TipoDelito,
        on_delete=models.PROTECT,
        db_column='tipodelito_id',
        related_name='expedientes',
        verbose_name='Tipo de Delito'
    )
    tipoprocedimiento = models.ForeignKey(
        TipoProcedimiento,
        on_delete=models.PROTECT,
        db_column='tipoprocedimiento_id',
        related_name='expedientes',
        verbose_name='Tipo de Procedimiento'
    )
    ciudad = models.ForeignKey(
        Ciudad,
        on_delete=models.PROTECT,
        db_column='ciudad_id',
        related_name='expedientes',
        verbose_name='Ciudad'
    )
    abogados = models.ManyToManyField(
        User,
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
    
    def __str__(self):
        numero = self.numero_juicio or str(self.id)
        return f'Expediente #{numero} - {self.cliente}'
    
    class Meta:
        verbose_name = 'Expediente Penal'
        verbose_name_plural = 'Expedientes Penales'
        ordering = ['-numero_juicio']
        indexes = [
            models.Index(fields=['numero_juicio'], name='idx_expediente_numerojuicio'),
            models.Index(fields=['cliente'], name='idx_expediente_cliente'),
        ]


# =============================================================================
# TABLA INTERMEDIA EXPEDIENTE ↔ ABOGADO (Mejorada)
# =============================================================================

class ExpedienteAbogado(ModelBase):
    id = models.AutoField(primary_key=True)
    expediente = models.ForeignKey(
        ExpedientePenal,
        on_delete=models.CASCADE,
        db_column='expediente_id',
        related_name='expediente_abogados',
        verbose_name='Expediente'
    )
    abogado = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='abogado_id',
        related_name='expediente_abogados',
        verbose_name='Abogado'
    )

    rol = models.ForeignKey(
        RolExpediente,
        on_delete=models.CASCADE,
        db_column='rol_id',
        related_name='expediente_abogados',
        help_text='Ej: Abogado Principal, Asistente, etc.',
        verbose_name='Rol'
    )

    fecha_asignacion = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f'{self.expediente} ↔ {self.abogado} ({estado})'

    class Meta:
        verbose_name = 'Expediente — Abogado'
        verbose_name_plural = 'Expedientes — Abogados'
        ordering = ['-fecha_asignacion']
        indexes = [
            models.Index(fields=['expediente'], name='idx_expabog_exp'),
            models.Index(fields=['abogado'], name='idx_expabog_abog'),
        ]
        constraints = [
            models.UniqueConstraint(fields=['expediente', 'abogado'], name='unique_expediente_abogado')
        ]


# =============================================================================
# ETAPA PROCESAL
# =============================================================================

class EtapaProcesal(ModelBase):
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

    id = models.AutoField(primary_key=True)
    expediente = models.ForeignKey(
        ExpedientePenal,
        on_delete=models.CASCADE,
        db_column='expediente_id',
        related_name='etapas',
        verbose_name='Expediente'
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


    @property
    def tipo_etapa_label(self):
        """Helper que devuelve la etiqueta legible del tipo de etapa.

        Usa el método generado por Django `get_tipo_etapa_display` para mantener
        los *labels* definidos en `TipoEtapa`.
        """
        return self.get_tipo_etapa_display()

    def __str__(self):
        return f"{self.tipo_etapa_label} — {self.expediente}"
    
    class Meta:
        verbose_name = 'Etapa Procesal'
        verbose_name_plural = 'Etapas Procesales'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['expediente'], name='idx_etapaprocesal_expediente'),
            models.Index(fields=['tipo_etapa'], name='idx_etapaprocesal_tipoetapa'),
        ]


# =============================================================================
# ESCRITO
# =============================================================================

class Escrito(ModelBase):
    id = models.AutoField(primary_key=True)
    expedientepenal = models.ForeignKey(
        ExpedientePenal,
        on_delete=models.CASCADE,
        db_column='expedientepenal_id',
        related_name='escritos',
        verbose_name='Expediente Penal'
    )
    etapaprocesal = models.ForeignKey(
        EtapaProcesal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='etapaprocesal_id',
        related_name='escritos',
        verbose_name='Etapa Procesal'
    )
    abogado = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        db_column='abogado_id',
        related_name='escritos',
        verbose_name='Abogado'
    )
    tipo_escrito = models.ForeignKey(
        TipoEscrito,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='tipo_escrito_id',
        related_name='escritos',
        verbose_name='Tipo de Escrito'
    )
    descripcion = models.TextField(blank=True)
    fecha = models.DateField(db_index=True)

    def __str__(self):
        return f"{self.tipo_escrito} ({self.fecha}) — {self.expedientepenal}"

    class Meta:
        verbose_name = 'Escrito'
        verbose_name_plural = 'Escritos'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['fecha'], name='idx_escrito_fecha'),
        ]


# =============================================================================
# SUJETO PROCESAL
# =============================================================================

class SujetoProcesal(ModelBase):
    id = models.AutoField(primary_key=True)
    expediente = models.ForeignKey(
        ExpedientePenal,
        on_delete=models.CASCADE,
        db_column='expediente_id',
        related_name='sujetos_procesales',
        verbose_name='Expediente'
    )
    rolprocesal = models.ForeignKey(
        RolProcesal,
        on_delete=models.PROTECT,
        db_column='rol_id',
        related_name='sujetos_procesales',
        verbose_name='Rol Procesal'
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, blank=True, db_index=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)

    @property
    def get_full_name(self):
        return f'{self.nombre} {self.apellido}'

    def __str__(self):
        return f"{self.get_full_name} ({self.rolprocesal})"

    class Meta:
        verbose_name = 'Sujeto Procesal'
        verbose_name_plural = 'Sujetos Procesales'
        ordering = ['-cedula']
        indexes = [
            models.Index(fields=['cedula'], name='idx_sujeto_procesal_cedula'),
            models.Index(fields=['rolprocesal'], name='idx_sujeto_procesal_rol'),
        ]


# =============================================================================
# EVIDENCIA / DOCUMENTO
# =============================================================================

class EvidenciaDocumento(ModelBase):
    id = models.AutoField(primary_key=True)
    expediente = models.ForeignKey(
        ExpedientePenal,
        on_delete=models.CASCADE,
        db_column='expediente_id',
        related_name='evidencias',
        verbose_name='Expediente'
    )
    escrito = models.ForeignKey(
        Escrito,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='escrito_id',
        related_name='evidencias',
        verbose_name='Escrito'
    )
    categoria = models.ForeignKey(
        CategoriaEvidencia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='categoria_id',
        related_name='evidencias',
        verbose_name='Categoría de Evidencia'
    )
    titulo = models.CharField(max_length=255)
    # FileField sin null=True (mejor práctica Django/PostgreSQL)
    # Si ya hay registros con null, la migración los convertirá a string vacío
    archivo = models.FileField(upload_to='evidencias/%Y/%m/', blank=True, default='')

    def __str__(self):
        return f"{self.titulo} — {self.expediente}"
    
    class Meta:
        verbose_name = 'Evidencia / Documento'
        verbose_name_plural = 'Evidencias / Documentos'
        ordering = ['-titulo']
        indexes = [
            models.Index(fields=['titulo'], name='idx_evi_doc_titulo'),
            models.Index(fields=['expediente'], name='idx_evi_doc_exp'),
        ]
