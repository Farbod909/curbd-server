from django.shortcuts import render
from django.views.decorators.http import require_safe


@require_safe
def add_host_view(request):
    return render(request, 'parking/add_host.html')
