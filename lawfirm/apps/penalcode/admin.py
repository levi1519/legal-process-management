from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import (
    TipoDelito, TipoProcedimiento, RolProcesal, CategoriaEvidencia,
    RolExpediente, TipoEscrito, Cliente, ExpedientePenal, ExpedienteAbogado,
    EtapaProcesal, Escrito, SujetoProcesal, EvidenciaDocumento
)

# =============================================================================
# BRANDING DEL SITIO ADMIN
# =============================================================================
admin.site.site_header = "Sistema COIP — Gestión Legal"
admin.site.site_title = "COIP Admin"
admin.site.index_title = "Panel de Administración"


# =============================================================================
# FILTROS PERSONALIZADOS
# =============================================================================

class EstadoPrescripcionFilter(admin.SimpleListFilter):
    """Filtra expedientes por estado de prescripción."""
    title = 'Estado de prescripción'
    parameter_name = 'prescripcion'

    def lookups(self, request, model_admin):
        return [
            ('vigente', 'Vigente'),
            ('proximo', 'Próximo a prescribir (≤30 días)'),
            ('prescrito', 'Prescrito'),
        ]

    def queryset(self, request, queryset):
        hoy = timezone.now().date()
        if self.value() == 'prescrito':
            return queryset.filter(prescripcion_fecha_limite__lt=hoy)
        if self.value() == 'proximo':
            limite = hoy + timezone.timedelta(days=30)
            return queryset.filter(
                prescripcion_fecha_limite__gte=hoy,
                prescripcion_fecha_limite__lte=limite,
            )
        if self.value() == 'vigente':
            return queryset.filter(prescripcion_fecha_limite__gt=hoy)
        return queryset


# =============================================================================
# INLINES
# =============================================================================

class ExpedienteAbogadoInline(admin.TabularInline):
    model = ExpedienteAbogado
    extra = 1
    fields = ('abogado', 'rol', 'fecha_asignacion', 'activo')
    readonly_fields = ('fecha_asignacion',)
    autocomplete_fields = ('abogado', 'rol')


class SujetoProcesalInline(admin.TabularInline):
    model = SujetoProcesal
    extra = 1
    fields = ('nombre', 'apellido', 'cedula', 'rolprocesal')
    autocomplete_fields = ('rolprocesal',)


class EtapaProcesalInline(admin.TabularInline):
    model = EtapaProcesal
    extra = 0
    fields = ('tipo_etapa', 'estado', 'fecha_inicio', 'fecha_limite', 'fecha_cierre')
    show_change_link = True


class EvidenciaDocumentoInline(admin.TabularInline):
    model = EvidenciaDocumento
    extra = 0
    fields = ('titulo', 'categoria', 'archivo')
    autocomplete_fields = ('categoria',)


# =============================================================================
# CATÁLOGOS
# =============================================================================

@admin.register(TipoDelito)
class TipoDelitoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'articulo_coip', 'accion_tipo', 'plazo_dias_investigacion')
    search_fields = ('nombre', 'articulo_coip')
    list_filter = ('accion_tipo',)
    ordering = ('nombre',)


@admin.register(TipoProcedimiento)
class TipoProcedimientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'accion', 'tipo_accion')
    search_fields = ('nombre',)
    list_filter = ('tipo_accion',)
    ordering = ('nombre',)


@admin.register(RolProcesal)
class RolProcesalAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(CategoriaEvidencia)
class CategoriaEvidenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(RolExpediente)
class RolExpedienteAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(TipoEscrito)
class TipoEscritoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    ordering = ('nombre',)


# =============================================================================
# CLIENTE
# =============================================================================

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'cedula', 'ciudad', 'email', 'telefono')
    search_fields = ('nombre', 'apellido', 'cedula', 'email')
    list_filter = ('ciudad',)
    ordering = ('nombre', 'apellido')
    autocomplete_fields = ('ciudad',)


# =============================================================================
# EXPEDIENTE PENAL
# =============================================================================

def marcar_archivado(modeladmin, request, queryset):
    """Acción masiva: marcar expedientes seleccionados como Archivado."""
    updated = queryset.update(estado=ExpedientePenal.EstadoExpediente.ARCHIVADO)
    modeladmin.message_user(request, f"{updated} expediente(s) marcado(s) como Archivado.")

marcar_archivado.short_description = "Marcar seleccionados como Archivado"


@admin.register(ExpedientePenal)
class ExpedientePenalAdmin(admin.ModelAdmin):
    list_display = (
        'numero_juicio', 'cliente', 'tipodelito', 'estado',
        'fecha_apertura', 'ciudad', 'dias_transcurridos',
    )
    search_fields = ('numero_juicio', 'cliente__nombre', 'cliente__apellido')
    list_filter = ('estado', 'tipodelito', 'ciudad', EstadoPrescripcionFilter)
    ordering = ('-numero_juicio', '-created_at')
    date_hierarchy = 'fecha_apertura'
    actions = [marcar_archivado]
    autocomplete_fields = ('cliente', 'tipodelito', 'tipoprocedimiento', 'ciudad')
    inlines = [
        ExpedienteAbogadoInline,
        SujetoProcesalInline,
        EtapaProcesalInline,
        EvidenciaDocumentoInline,
    ]
    fieldsets = (
        ('Identificación', {
            'fields': ('numero_juicio', 'unidad_judicial', 'estado')
        }),
        ('Partes', {
            'fields': ('cliente',)
        }),
        ('Clasificación Legal', {
            'fields': ('tipodelito', 'tipoprocedimiento', 'ciudad')
        }),
        ('Fechas', {
            'fields': ('fecha_apertura', 'fecha_cierre', 'prescripcion_fecha_limite')
        }),
    )

    @admin.display(description='Días transcurridos')
    def dias_transcurridos(self, obj):
        if obj.fecha_apertura:
            delta = (timezone.now().date() - obj.fecha_apertura).days
            return delta
        return '—'


# =============================================================================
# EXPEDIENTE ↔ ABOGADO
# =============================================================================

@admin.register(ExpedienteAbogado)
class ExpedienteAbogadoAdmin(admin.ModelAdmin):
    list_display = ('expediente', 'abogado', 'rol', 'fecha_asignacion', 'activo')
    search_fields = ('expediente__numero_juicio', 'abogado__username')
    list_filter = ('rol', 'activo')
    ordering = ('-fecha_asignacion',)
    autocomplete_fields = ('expediente', 'abogado', 'rol')


# =============================================================================
# ETAPA PROCESAL
# =============================================================================

@admin.register(EtapaProcesal)
class EtapaProcesalAdmin(admin.ModelAdmin):
    list_display = ('expediente', 'tipo_etapa', 'estado', 'fecha_inicio', 'fecha_limite')
    search_fields = ('expediente__numero_juicio',)
    list_filter = ('tipo_etapa', 'estado')
    ordering = ('-fecha_inicio',)
    autocomplete_fields = ('expediente',)


# =============================================================================
# ESCRITO
# =============================================================================

@admin.register(Escrito)
class EscritoAdmin(admin.ModelAdmin):
    list_display = ('expedientepenal', 'tipo_escrito', 'abogado', 'fecha')
    search_fields = ('expedientepenal__numero_juicio', 'descripcion')
    list_filter = ('tipo_escrito', 'fecha')
    ordering = ('-fecha',)
    date_hierarchy = 'fecha'
    autocomplete_fields = ('expedientepenal', 'abogado', 'tipo_escrito')


# =============================================================================
# SUJETO PROCESAL
# =============================================================================

@admin.register(SujetoProcesal)
class SujetoProcesalAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'cedula', 'expediente', 'rolprocesal')
    search_fields = ('nombre', 'apellido', 'cedula')
    list_filter = ('rolprocesal',)
    ordering = ('apellido', 'nombre')
    autocomplete_fields = ('expediente', 'rolprocesal')


# =============================================================================
# EVIDENCIA / DOCUMENTO
# =============================================================================

@admin.register(EvidenciaDocumento)
class EvidenciaDocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'expediente', 'categoria', 'archivo')
    search_fields = ('titulo', 'expediente__numero_juicio')
    list_filter = ('categoria',)
    ordering = ('-created_at',)
    autocomplete_fields = ('expediente', 'categoria')
