from django.urls import path
from apps.core.views import home

app_name = 'core'

urlpatterns = []

# ── Páginas principales ──────────────────────────────────────────────────────
urlpatterns += [
    path('',         home.HomeView.as_view(),    name='home'),
    path('menu/',    home.MenuView.as_view(),    name='menu'),
    path('acerca/',  home.AboutView.as_view(),   name='about'),
    path('contacto/', home.ContactView.as_view(), name='contact'),
]