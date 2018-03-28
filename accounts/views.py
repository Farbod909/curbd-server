from django.contrib.auth import authenticate, login
from django.contrib.auth import logout, get_user_model
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from rest_framework import viewsets

from .forms import UserLoginForm, UserRegistrationForm
from .models import Host, Customer
from .serializers import UserSerializer


def logout_view(request):
    logout(request)
    return redirect('login')


class UserRegistrationView(View):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save(commit=True)  # register user to database

            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            is_host = form.cleaned_data['is_host']

            user = authenticate(request, email=email, password=password)

            if user is not None:

                new_customer = Customer(user=user)
                new_customer.save()

                if is_host:
                    new_host = Host(user=user)
                    new_host.save()

                logout(request)
                login(request, user)
                return redirect('home')
            else:
                return HttpResponse('User registration failed. Please try again.')


class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return render(request, self.template_name, {'form': form, 'error_msg': 'Invalid login attempt.'})


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = get_user_model().objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
