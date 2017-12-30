from django.shortcuts import render, redirect
from django.views.generic import View
from accounts.admin import UserCreationForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse


class UserRegistrationView(View):
    form_class = UserCreationForm
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
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return HttpResponse('User registration failed. Please try again.')
