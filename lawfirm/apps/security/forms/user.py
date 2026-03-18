from django import forms
from apps.security.models import User

class PersonalDataForm(forms.ModelForm):
    """Formulario para editar los datos personales del abogado."""
 
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'ci', 'telefono', 'direccion']
        labels = {
            'first_name': 'Nombres',
            'last_name':  'Apellidos',
            'email':      'Correo electrónico',
            'ci':         'Cédula de identidad',
            'telefono':   'Teléfono',
            'direccion':  'Dirección',
        }
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required  = True
        self.fields['email'].required      = True
 
    def clean_email(self):
        email = self.cleaned_data['email']
        qs = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un usuario registrado con este correo electrónico.')
        return email
 
    def clean_ci(self):
        ci = self.cleaned_data.get('ci')
        if ci:
            qs = User.objects.filter(ci=ci).exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Esta cédula ya está registrada en el sistema.')
        return ci