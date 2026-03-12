from django.contrib import admin
from .models import (
    TipoDelito, TipoProcedimiento, RolProcesal, CategoriaEvidencia,
    RolExpediente, TipoEscrito, Cliente, ExpedientePenal, ExpedienteAbogado,
    EtapaProcesal, Escrito, SujetoProcesal, EvidenciaDocumento
)


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


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'cedula', 'ciudad', 'email', 'telefono')
    search_fields = ('nombre', 'apellido', 'cedula', 'email')
    list_filter = ('ciudad',)
    ordering = ('nombre', 'apellido')


@admin.register(ExpedientePenal)
class ExpedientePenalAdmin(admin.ModelAdmin):
    list_display = ('numero_juicio', 'cliente', 'tipodelito', 'estado', 'fecha_apertura', 'ciudad')
    search_fields = ('numero_juicio', 'cliente__nombre', 'cliente__apellido')
    list_filter = ('estado', 'tipodelito', 'ciudad')
    ordering = ('-numero_juicio', '-created_at')
    date_hierarchy = 'fecha_apertura'


@admin.register(ExpedienteAbogado)
class ExpedienteAbogadoAdmin(admin.ModelAdmin):
    list_display = ('expediente', 'abogado', 'rol', 'fecha_asignacion', 'activo')
    search_fields = ('expediente__numero_juicio', 'abogado__username')
    list_filter = ('rol', 'activo')
    ordering = ('-fecha_asignacion',)


@admin.register(EtapaProcesal)
class EtapaProcesalAdmin(admin.ModelAdmin):
    list_display = ('expediente', 'tipo_etapa', 'estado', 'fecha_inicio', 'fecha_limite')
    search_fields = ('expediente__numero_juicio',)
    list_filter = ('tipo_etapa', 'estado')
    ordering = ('-fecha_inicio',)


@admin.register(Escrito)
class EscritoAdmin(admin.ModelAdmin):
    list_display = ('expedientepenal', 'tipo_escrito', 'abogado', 'fecha')
    search_fields = ('expedientepenal__numero_juicio', 'descripcion')
    list_filter = ('tipo_escrito', 'fecha')
    ordering = ('-fecha',)
    date_hierarchy = 'fecha'


@admin.register(SujetoProcesal)
class SujetoProcesalAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'cedula', 'expediente', 'rolprocesal')
    search_fields = ('nombre', 'apellido', 'cedula')
    list_filter = ('rolprocesal',)
    ordering = ('apellido', 'nombre')


@admin.register(EvidenciaDocumento)
class EvidenciaDocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'expediente', 'categoria', 'archivo')
    search_fields = ('titulo', 'expediente__numero_juicio')
    list_filter = ('categoria',)
    ordering = ('-created_at',)
