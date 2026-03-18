from django import forms

# =============================================================================
# CONTACT FORM
# =============================================================================
 
class ContactForm(forms.Form):
    nombre      = forms.CharField(max_length=200, label='Nombre completo')
    email       = forms.EmailField(label='Correo electrónico')
    telefono    = forms.CharField(max_length=30, required=False, label='Teléfono')
    institucion = forms.CharField(max_length=200, required=False, label='Institución / Despacho')
    asunto      = forms.ChoiceField(
        label='Asunto',
        choices=[
            ('soporte_acceso',      'Problemas de acceso o autenticación'),
            ('soporte_error',       'Reporte de error en el sistema'),
            ('soporte_rendimiento', 'Problemas de rendimiento'),
            ('consulta_legal',      'Consulta sobre funcionalidades legales'),
            ('consulta_datos',      'Consulta sobre gestión de datos'),
            ('capacitacion',        'Solicitud de capacitación'),
            ('mejora',              'Sugerencia de mejora'),
            ('integracion',         'Solicitud de integración'),
            ('otro',                'Otro'),
        ]
    )
    mensaje = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        min_length=20,
        label='Mensaje'
    )