from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils import timezone


class PenalcodeMenuView(LoginRequiredMixin, TemplateView):
    """Menú del módulo penal: acceso rápido a submódulos y métricas."""
    template_name = 'penalcode/menu.html'
    login_url = '/security/login/'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            from apps.penalcode.models import (
                ExpedientePenal, Cliente, Escrito,
                TipoDelito, TipoProcedimiento, SujetoProcesal,
                CategoriaEvidencia
            )
            from apps.security.models import User

            today = timezone.now().date()

            context['stats'] = {
                'expedientes': ExpedientePenal.objects.count(),
                'clientes': Cliente.objects.count(),
                'escritos': Escrito.objects.count(),
                'delitos': TipoDelito.objects.count(),
                'procedimientos': TipoProcedimiento.objects.count(),
                'sujetos': SujetoProcesal.objects.count(),
                'evidencias': CategoriaEvidencia.objects.count(),
                'abogados': User.objects.filter(is_active=True).count(),
                'expedientes_abiertos': ExpedientePenal.objects.exclude(estado__in=['archivado', 'abandonado', 'prescrito']).count(),
                'vencimientos_30d': ExpedientePenal.objects.filter(
                    prescripcion_fecha_limite__gte=today,
                    prescripcion_fecha_limite__lt=today + timezone.timedelta(days=30),
                ).count(),
            }
        except Exception:
            context['stats'] = {}

        return context
