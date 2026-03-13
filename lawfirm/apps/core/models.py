from django.db import models
from django.utils import timezone

class ModelBase(models.Model):
    """
    Modelo base abstracto para auditoría de entidades.
    Incluye campos para tracking de creación, actualización y eliminación.
    """
    created_at = models.DateTimeField(
        verbose_name="fecha de creación",
        auto_now_add=True,
        help_text="Fecha y hora en que se creó el registro"
    )
    updated_at = models.DateTimeField(
        verbose_name="fecha de actualización",
        auto_now=True,
        help_text="Fecha y hora de la última modificación"
    )
    deleted_at = models.DateTimeField(
        verbose_name="fecha de eliminación",
        null=True,
        blank=True,
        help_text="Fecha y hora de eliminación (soft delete)"
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete: marca el registro como eliminado en lugar de borrarlo.
        """
        self.deleted_at = timezone.now()
        self.save(using=using)

    def hard_delete(self):
        """
        Eliminación real de la base de datos.
        """
        super().delete()

    def restore(self):
        """
        Restaura un registro previamente eliminado (soft delete).
        """
        self.deleted_at = None
        self.save()

# =============================================================================
# GEOGRAFÍA
# =============================================================================

class Region(ModelBase):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField('Nombre', max_length=100, unique=True)

    def __str__(self):
        return f'Región: {self.nombre}'
    
    class Meta:
        verbose_name = 'Region'
        verbose_name_plural = 'Regiones'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre'], name='idx_region_nombre'),
        ]

class Provincia(ModelBase):
    id = models.AutoField(primary_key=True)
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        db_column='region_id',
        related_name='provincias',
        verbose_name='Región'
    )
    nombre = models.CharField('Nombre', max_length=100, unique=True)

    def __str__(self):
        return f'Provincia: {self.nombre}'

    class Meta:
        verbose_name = 'Provincia'
        verbose_name_plural = 'Provincias'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre'], name='idx_provincia_nombre'),
            models.Index(fields=['region'], name='idx_provincia_region'),
        ]

class Ciudad(ModelBase):
    id = models.AutoField(primary_key=True)
    provincia = models.ForeignKey(
        Provincia,
        on_delete=models.CASCADE,
        db_column='provincia_id',
        related_name='ciudades',
        verbose_name='Provincia'
    )
    nombre = models.CharField('Nombre', max_length=100, unique=True)

    def __str__(self):
        return f'Ciudad: {self.nombre}'

    class Meta:
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre'], name='idx_ciudad_nombre'),
            models.Index(fields=['provincia'], name='idx_ciudad_provincia'),
        ]