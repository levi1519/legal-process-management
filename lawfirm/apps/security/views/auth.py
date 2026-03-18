from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView
from apps.security.forms.user import PersonalDataForm

# =============================================================================
# VIEWS
# =============================================================================

class LoginView(FormView):
    """
    Vista de autenticación del abogado.
    Usa AuthenticationForm de Django para manejar las credenciales.
    """
    template_name = 'auth/login.html'
    form_class    = AuthenticationForm
    success_url   = reverse_lazy('core:home')

    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users away from login
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(
            self.request,
            f'Bienvenido, {user.get_full_name() or user.username}.'
        )
        # Respect ?next= param
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect(self.success_url)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class LogoutView(View):
    """
    Cierre de sesión mediante POST (protegido por CSRF).
    Redirige al login después del logout.
    """
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, 'Ha cerrado sesión correctamente.')
        return redirect('security:login')

    # Allow GET as fallback (not recommended for production)
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Perfil del abogado autenticado.
    Maneja dos formularios independientes en el mismo POST mediante
    un campo oculto `form_type` (personal | password).
    """
    template_name  = 'auth/profile.html'
    login_url      = reverse_lazy('security:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user    = self.request.user

        context['personal_form'] = kwargs.get(
            'personal_form',
            PersonalDataForm(instance=user)
        )
        context['password_form'] = kwargs.get(
            'password_form',
            PasswordChangeForm(user=user)
        )

        # Stats for identity card
        try:
            from apps.penalcode.models import ExpedientePenal, Escrito
            context['expedientes_count'] = (
                ExpedientePenal.objects
                .filter(abogados=user)
                .count()
            )
            context['escritos_count'] = (
                Escrito.objects
                .filter(abogado=user)
                .count()
            )
        except Exception:
            context['expedientes_count'] = 0
            context['escritos_count']    = 0

        # Recent activity placeholder — extend with real audit log if available
        context['recent_activity'] = []

        return context

    def post(self, request, *args, **kwargs):
        form_type = request.POST.get('form_type')

        if form_type == 'personal':
            return self._handle_personal(request)
        elif form_type == 'password':
            return self._handle_password(request)

        messages.error(request, 'Solicitud no válida.')
        return redirect('security:profile')

    # ── Personal data handler ──────────────────────────────────────────────

    def _handle_personal(self, request):
        form = PersonalDataForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sus datos personales fueron actualizados correctamente.')
            return redirect('security:profile')

        messages.error(request, 'Por favor corrija los errores en el formulario.')
        return self.render_to_response(
            self.get_context_data(personal_form=form)
        )

    # ── Password change handler ────────────────────────────────────────────

    def _handle_password(self, request):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Su contraseña fue actualizada correctamente.')
            return redirect('security:profile')

        messages.error(request, 'Por favor corrija los errores en el formulario de contraseña.')
        return self.render_to_response(
            self.get_context_data(password_form=form)
        )