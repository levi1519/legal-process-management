from django.db import models
from django.contrib.auth.models import AbstractUser, Group

class User(AbstractUser):
    """
    Modelo de usuario personalizado que hereda de AbstractUser.
    Añade campos adicionales y configuraciones específicas del sistema.
    """
    email = models.EmailField(
        'Correo Electrónico',
        unique=True,
        blank=False,
        null=False,
        help_text="Correo electrónico único del usuario"
    )
    telefono = models.CharField(
        'Teléfono',
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )
    direccion = models.CharField(
        'Dirección',
        max_length=255,
        blank=True,
        null=True
    )
    ci = models.CharField(
        'Cédula de Identidad',
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        help_text="Cédula de identidad única del usuario"
    )
    is_active = models.BooleanField(
        'Activo',
        default=True,
        help_text='Indica si el usuario puede iniciar sesión'
    )
    is_staff = models.BooleanField(
        'Staff',
        default=False,
        help_text='Indica si el usuario puede acceder al admin'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    groups = models.ManyToManyField(Group, related_name='security_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='security_user_set', blank=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']
        indexes = [
            models.Index(fields=['username'], name='idx_user_username'),
            models.Index(fields=['email'], name='idx_user_email'),
            models.Index(fields=['ci'], name='idx_user_ci'),
        ]

    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_groups(self):
        return self.groups.all()

    def __str__(self):
        return f'{self.username} - {self.get_full_name or self.email}'

    def save(self, *args, **kwargs):
        # Django ya maneja el hashing en create_user, createsuperuser 
        # y en los formularios AuthenticationForm/UserCreationForm.
        super().save(*args, **kwargs)