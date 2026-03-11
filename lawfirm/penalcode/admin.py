from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta
from django.contrib.admin import SimpleListFilter

from .models import (
    Abogado, Region, Provincia, Ciudad, TipoDelito, TipoProcedimiento,
    RolProcesal, CategoriaEvidencia, Cliente, ExpedientePenal, 
    ExpedienteAbogado, EtapaProcesal, Escrito, SujetoProcesal, EvidenciaDocumento
)

# =============================================================================
# FILTROS PERSONALIZADOS
# =============================================================================
class EstadoPrescripcionFilter(SimpleListFilter):
    title = 'Estado de Prescripción'
    parameter_name = 'prescripcion'
    
    def lookups(self, request, model_admin):
        return (
            ('vigente', 'Vigente'),
            ('proximo', 'Próximo a prescribir (< 30 días)'),
            ('prescrito', 'Prescrito'),
        )
    
    def queryset(self, request, queryset):
        today = timezone.now().date()
        if self.value() == 'vigente':
            return queryset.filter(prescripcion_fecha_limite__gt=today)
        if self.value() == 'proximo':
            return queryset.filter(
                prescripcion_fecha_limite__gt=today,
                prescripcion_fecha_limite__lte=today + timedelta(days=30)
            )
        if self.value() == 'prescrito':
            return queryset.filter(prescripcion_fecha_limite__lte=today)

# =============================================================================
# USUARIO PERSONALIZADO
# =============================================================================
@admin.register(Abogado)
class AbogadoAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'telefono', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Información Legal', {'fields': ('telefono',)}),
    )

# =============================================================================
# CATÁLOGOS CON SEARCH_FIELDS (CRÍTICO PARA AUTOCOMPLETE)
# =============================================================================
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Provincia)
class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'region')
    search_fields = ('nombre',)
    list_filter = ('region',)

@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'provincia')
    search_fields = ('nombre',)
    list_filter = ('provincia__region',)

@admin.register(TipoDelito)
class TipoDelitoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'articulo_coip', 'plazo_instruccion_dias')
    search_fields = ('nombre', 'articulo_coip')
    ordering = ('articulo_coip',)

@admin.register(RolProcesal)
class RolProcesalAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(CategoriaEvidencia)
class CategoriaEvidenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(TipoProcedimiento)
class TipoProcedimientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_accion')
    search_fields = ('nombre',)

@admin.register(EtapaProcesal)
class EtapaProcesalAdmin(admin.ModelAdmin):
    list_display = ('expediente', 'tipo_etapa', 'estado', 'fecha_inicio', 'fecha_limite')
    search_fields = ('expediente__numero_juicio', 'tipo_etapa')
    list_filter = ('tipo_etapa', 'estado')
    autocomplete_fields = ['expediente']
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-fecha_inicio',)

# =============================================================================
# INLINES (Tablas relacionadas dentro del Expediente)
# =============================================================================
class SujetoProcesalInline(admin.TabularInline):
    model = SujetoProcesal
    extra = 1
    fields = ('rolprocesal', 'cedula', 'nombre', 'apellido', 'telefono')
    autocomplete_fields = ['rolprocesal']

class EtapaProcesalInline(admin.TabularInline):
    model = EtapaProcesal
    extra = 0
    fields = ('tipo_etapa', 'estado', 'fecha_inicio', 'fecha_limite', 'fecha_cierre')
    readonly_fields = ('created_at',)

class EvidenciaDocumentoInline(admin.TabularInline):
    model = EvidenciaDocumento
    extra = 1
    fields = ('categoria', 'titulo', 'archivo')
    autocomplete_fields = ['categoria']

class ExpedienteAbogadoInline(admin.TabularInline):
    model = ExpedienteAbogado
    extra = 1
    fields = ('abogado', 'rol', 'activo')
    autocomplete_fields = ['abogado']

# =============================================================================
# MODELOS PRINCIPALES
# =============================================================================
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre', 'apellido', 'ciudad', 'telefono', 'created_at')
    search_fields = ('cedula', 'nombre', 'apellido', 'email')
    list_filter = ('ciudad__provincia__region', 'ciudad')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(ExpedientePenal)
class ExpedientePenalAdmin(admin.ModelAdmin):
    list_display = ('numero_juicio', 'cliente', 'tipodelito', 'estado', 'fecha_apertura', 'dias_transcurridos')
    list_filter = ('estado', EstadoPrescripcionFilter, 'tipodelito', 'ciudad__provincia__region', 'fecha_apertura')
    search_fields = ('numero_juicio', 'cliente__cedula', 'cliente__nombre', 'cliente__apellido', 'unidad_judicial')
    date_hierarchy = 'fecha_apertura'
    autocomplete_fields = ['cliente', 'tipodelito', 'ciudad']
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-fecha_apertura',)
    
    actions = ['marcar_archivado']
    inlines = [ExpedienteAbogadoInline, SujetoProcesalInline, EtapaProcesalInline, EvidenciaDocumentoInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('cliente', 'numero_juicio', 'unidad_judicial', 'ciudad')
        }),
        ('Clasificación Legal (COIP)', {
            'fields': ('tipodelito', 'tipoprocedimiento', 'estado')
        }),
        ('Tiempos Procesales', {
            'fields': ('fecha_apertura', 'fecha_cierre', 'prescripcion_fecha_limite')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Días Transcurridos')
    def dias_transcurridos(self, obj):
        if obj.fecha_cierre:
            return (obj.fecha_cierre - obj.fecha_apertura).days
        return (timezone.now().date() - obj.fecha_apertura).days

    @admin.action(description='Marcar como Archivado (Cerrar caso)')
    def marcar_archivado(self, request, queryset):
        updated = queryset.update(estado='archivado', fecha_cierre=timezone.now().date())
        self.message_user(request, f'{updated} expediente(s) marcado(s) como archivados exitosamente.')

@admin.register(Escrito)
class EscritoAdmin(admin.ModelAdmin):
    list_display = ('tipo_escrito', 'expedientepenal', 'etapaprocesal', 'abogado', 'fecha')
    search_fields = ('tipo_escrito', 'expedientepenal__numero_juicio', 'descripcion')
    list_filter = ('fecha', 'abogado', 'etapaprocesal__tipo_etapa')
    autocomplete_fields = ['expedientepenal', 'abogado', 'etapaprocesal']
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-fecha',)
    date_hierarchy = 'fecha'

@admin.register(SujetoProcesal)
class SujetoProcesalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cedula', 'rolprocesal', 'expediente')
    search_fields = ('nombre', 'apellido', 'cedula', 'expediente__numero_juicio')
    list_filter = ('rolprocesal',)
    autocomplete_fields = ['expediente', 'rolprocesal']
    readonly_fields = ('created_at', 'updated_at')

@admin.register(EvidenciaDocumento)
class EvidenciaDocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'expediente', 'categoria', 'tiene_archivo', 'preview_archivo', 'created_at')
    search_fields = ('titulo', 'expediente__numero_juicio')
    list_filter = ('categoria', 'created_at')
    autocomplete_fields = ['expediente', 'escrito', 'categoria']
    readonly_fields = ('created_at', 'preview_archivo')
    
    @admin.display(description='¿Adjunto?', boolean=True)
    def tiene_archivo(self, obj):
        return bool(obj.archivo)
    
    @admin.display(description='Enlace')
    def preview_archivo(self, obj):
        if obj.archivo:
            return format_html('<a href="{}" target="_blank">📄 Descargar</a>', obj.archivo.url)
        return "-"

# =============================================================================
# CONFIGURACIÓN VISUAL DEL PANEL
# =============================================================================
admin.site.site_header = "LegalTech Ecuador — Gestión COIP"
admin.site.site_title = "Portal Legal"
admin.site.index_title = "Panel de Control de Juicios y Expedientes"