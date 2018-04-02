from django.shortcuts import render
from django.views.decorators.http import require_safe
from django.contrib.auth.decorators import login_required

from .forms import ReservationCreationForm


@require_safe
def add_host_view(request):
    return render(request, 'parking/add_host.html')


@login_required
def add_reservation_view(request):
    form = ReservationCreationForm(request)
    return render(request, 'parking/add_reservation.html', {'form': form})
