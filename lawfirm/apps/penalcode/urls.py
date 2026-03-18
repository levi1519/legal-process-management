from django.urls import path
from apps.penalcode.views.home import PenalcodeMenuView

app_name = 'penalcode'

urlpatterns = [
    path('', PenalcodeMenuView.as_view(), name='menu'),
]
