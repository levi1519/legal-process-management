from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from apps.core.forms.contact import ContactForm

class HomeView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('security:login')
    redirect_field_name = 'next'
    """
    Panel principal del sistema.
    Expone estadísticas de resumen y expedientes recientes al contexto.
    """
    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Import inside method to avoid circular imports at module level
        try:
            from apps.penalcode.models import ExpedientePenal, Cliente, Escrito

            today      = timezone.now().date()
            limite_prox = today + timezone.timedelta(days=30)

            context['stats'] = {
                'expedientes_activos': ExpedientePenal.objects.exclude(
                    estado__in=['archivado', 'abandonado', 'prescrito']
                ).count(),
                'por_prescribir': ExpedientePenal.objects.filter(
                    prescripcion_fecha_limite__gte=today,
                    prescripcion_fecha_limite__lte=limite_prox,
                ).count(),
                'clientes':     Cliente.objects.count(),
                'escritos_mes': Escrito.objects.filter(
                    fecha__year=today.year,
                    fecha__month=today.month,
                ).count(),
            }
 
            context['expedientes_recientes'] = (
                ExpedientePenal.objects
                .select_related('cliente', 'tipodelito')
                .order_by('-created_at')[:8]
            )
 
            # Próximos vencimientos — ordenados por urgencia
            deadlines_qs = (
                ExpedientePenal.objects
                .filter(
                    prescripcion_fecha_limite__gte=today,
                    prescripcion_fecha_limite__lte=limite_prox,
                )
                .exclude(estado__in=['archivado', 'abandonado', 'prescrito'])
                .order_by('prescripcion_fecha_limite')[:8]
            )
            context['deadlines'] = [
                {
                    'numero_juicio':           exp.numero_juicio or f'#{exp.id}',
                    'prescripcion_fecha_limite': exp.prescripcion_fecha_limite,
                    'days_left':               (exp.prescripcion_fecha_limite - today).days,
                }
                for exp in deadlines_qs
            ]
        except Exception:
            # Graceful fallback — models not yet migrated or DB unavailable
            context['stats']                = {}
            context['expedientes_recientes'] = []
            context['deadlines']             = []
        
        return context
    
class AboutView(LoginRequiredMixin, TemplateView):
    """Página de información del sistema."""
    login_url = reverse_lazy('security:login')
    redirect_field_name = 'next'
    template_name = 'main/about.html'

class ContactView(FormView):
    """
    Formulario de contacto / soporte técnico.
    TODO: Reemplazar el stub por envío real con django.core.mail.send_mail
          o integración con servicio de notificaciones externo.
    """
    template_name = 'main/contact.html'
    form_class    = ContactForm
    success_url   = reverse_lazy('core:contact')

    def form_valid(self, form):
        messages.success(
            self.request,
            'Su mensaje fue enviado correctamente. '
            'Nos comunicaremos con usted en un plazo de 24 a 48 horas hábiles.'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'Por favor corrija los errores señalados en el formulario antes de continuar.'
        )
        return super().form_invalid(form)

class MenuView(LoginRequiredMixin, TemplateView):
    """
    Panel de módulos del sistema.
    Expone estadísticas globales para los contadores de cada tarjeta de módulo.
    """
    login_url = reverse_lazy('security:login')
    redirect_field_name = 'next'
    template_name = 'main/menu.html'
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
 
        try:
            from apps.penalcode.models import (
                ExpedientePenal, Cliente, Escrito,
                EtapaProcesal, EvidenciaDocumento, SujetoProcesal,
            )
            from apps.security.models import User
 
            context['stats'] = {
                'expedientes_total': ExpedientePenal.objects.count(),
                'clientes':          Cliente.objects.count(),
                'escritos_total':    Escrito.objects.count(),
                'etapas_total':      EtapaProcesal.objects.count(),
                'evidencias_total':  EvidenciaDocumento.objects.count(),
                'sujetos_total':     SujetoProcesal.objects.count(),
                'abogados_total':    User.objects.filter(is_active=True).count(),
            }
        except Exception:
            context['stats'] = {}
 
        return context