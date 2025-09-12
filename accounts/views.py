from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import  UpdateView

from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomAuthenticationForm
from .models import User

# Create your views here.


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre compte a été créé avec succès. Vous devez vous identifier pour voir votre profil.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    context = {"form": form}
    return render(request, "accounts/register.html", context)


def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("wallets:wallets")
    else:
        form = CustomAuthenticationForm(request)
    context = {
        "form": form
    }
    return render(request, "accounts/login.html", context)


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("accounts:login")
    return render(request, "accounts/logout.html", {})


class EditProfile(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'accounts/edit_profile.html'
    success_url = reverse_lazy('accounts:EditProfile')

    def get_object(self):
        obj = get_object_or_404(User, pk=self.request.user.pk)
        return obj

    def form_valid(self, form):
        messages.success(self.request, f"Votre profil a été changé.")  # {m}")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'edit profile'
        return context
