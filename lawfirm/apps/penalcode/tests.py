from datetime import timedelta
from unittest.mock import MagicMock

from django.contrib import admin
from django.db import IntegrityError
from django.test import RequestFactory, TestCase
from django.utils import timezone

from apps.core.models import Ciudad, Provincia, Region
from apps.penalcode.admin import EstadoPrescripcionFilter, ExpedientePenalAdmin, marcar_archivado
from apps.penalcode.models import (
    Cliente,
    EtapaProcesal,
    ExpedienteAbogado,
    ExpedientePenal,
    RolExpediente,
    TipoDelito,
    TipoProcedimiento,
)
from apps.security.models import User


class PenalcodeBusinessRulesTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.region = Region.objects.create(nombre='Costa')
        self.provincia = Provincia.objects.create(region=self.region, nombre='Guayas')
        self.ciudad = Ciudad.objects.create(provincia=self.provincia, nombre='Guayaquil')

        self.user = User.objects.create_user(
            username='abogado1',
            email='abogado1@example.com',
            password='Test1234!',
            first_name='Ana',
            last_name='Perez',
        )
        self.rol = RolExpediente.objects.create(nombre='Principal')

        self.tipodelito = TipoDelito.objects.create(
            nombre='Estafa',
            articulo_coip='186',
            accion_tipo='publica',
        )
        self.tipoprocedimiento = TipoProcedimiento.objects.create(
            nombre='Ordinario',
            accion='Penal',
            tipo_accion='publica',
        )
        self.cliente = Cliente.objects.create(
            ciudad=self.ciudad,
            nombre='Carlos',
            apellido='Lopez',
            cedula='0999999999',
            email='carlos@example.com',
        )

    def _create_expediente(self, numero_juicio='123-2026', prescripcion_delta_days=90):
        today = timezone.now().date()
        return ExpedientePenal.objects.create(
            cliente=self.cliente,
            tipodelito=self.tipodelito,
            tipoprocedimiento=self.tipoprocedimiento,
            ciudad=self.ciudad,
            numero_juicio=numero_juicio,
            fecha_apertura=today,
            prescripcion_fecha_limite=today + timedelta(days=prescripcion_delta_days),
        )

    def test_unique_etapa_activa_por_expediente(self):
        expediente = self._create_expediente(numero_juicio='J-001')

        EtapaProcesal.objects.create(
            expediente=expediente,
            tipo_etapa=EtapaProcesal.TipoEtapa.JUICIO,
            estado=EtapaProcesal.EstadoEtapa.ACTIVA,
            fecha_inicio=timezone.now().date(),
        )

        with self.assertRaises(IntegrityError):
            EtapaProcesal.objects.create(
                expediente=expediente,
                tipo_etapa=EtapaProcesal.TipoEtapa.JUICIO,
                estado=EtapaProcesal.EstadoEtapa.ACTIVA,
                fecha_inicio=timezone.now().date(),
            )

    def test_unique_expediente_abogado(self):
        expediente = self._create_expediente(numero_juicio='J-002')

        ExpedienteAbogado.objects.create(
            expediente=expediente,
            abogado=self.user,
            rol=self.rol,
        )

        with self.assertRaises(IntegrityError):
            ExpedienteAbogado.objects.create(
                expediente=expediente,
                abogado=self.user,
                rol=self.rol,
            )

    def test_estado_prescripcion_filter(self):
        today = timezone.now().date()
        exp_prescrito = self._create_expediente('J-003', prescripcion_delta_days=-1)
        exp_proximo = self._create_expediente('J-004', prescripcion_delta_days=10)
        exp_vigente = self._create_expediente('J-005', prescripcion_delta_days=120)

        model_admin = ExpedientePenalAdmin(ExpedientePenal, admin.site)
        request = self.factory.get('/admin/')
        base_qs = ExpedientePenal.objects.all()
        filtro = EstadoPrescripcionFilter(request, {}, ExpedientePenal, model_admin)

        filtro.value = lambda: 'prescrito'
        self.assertQuerySetEqual(filtro.queryset(request, base_qs), [exp_prescrito], transform=lambda x: x)

        filtro.value = lambda: 'proximo'
        self.assertQuerySetEqual(filtro.queryset(request, base_qs), [exp_proximo], transform=lambda x: x)

        filtro.value = lambda: 'vigente'
        vigente_qs = list(filtro.queryset(request, base_qs))
        self.assertCountEqual(vigente_qs, [exp_vigente, exp_proximo])

        # Sanity check to ensure test dates are where expected.
        self.assertLess(exp_prescrito.prescripcion_fecha_limite, today)

    def test_marcar_archivado_action(self):
        expediente = self._create_expediente(numero_juicio='J-006')
        request = self.factory.get('/admin/')
        modeladmin = MagicMock()

        marcar_archivado(modeladmin, request, ExpedientePenal.objects.filter(pk=expediente.pk))
        expediente.refresh_from_db()

        self.assertEqual(expediente.estado, ExpedientePenal.EstadoExpediente.ARCHIVADO)
        modeladmin.message_user.assert_called_once()
