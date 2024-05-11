from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView, DetailView

from .forms import AssetForm, AssetUpdateForm
from .models import Asset, Ticker

# Create your views here.


def create_asset(request):
    form = AssetForm(request.POST or None)
    if request.method == 'POST':
        symbol = request.POST.get('ticker-input')
        if symbol:
            t = Ticker.objects.get(symbol=request.POST.get('ticker-input'))
            if form.is_valid():
                instance = form.save(commit=False)
                instance.ticker = t
                instance.user = request.user
                instance.save()
                messages.success(request, 'Asset created!')
        else:
            messages.error(request, 'Please enter a valid ticker or create a new one.')

    context = {
        "title": "new-asset",
        # "tickers": Ticker.objects.all(),
        'asset_form': form,
    }
    return render(request, 'assets/new-asset.html', context)


class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'assets/assets.html'

    def get_queryset(self):
        return Asset.objects.filter(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['title'] = 'dashboard'
        return context


class AssetDetailView(DetailView):
    model = Asset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Asset-detail'
        return context


class AssetDeleteView(LoginRequiredMixin, DeleteView):
    model = Asset
    success_url = reverse_lazy('assets:assets')

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect(self.get_success_url())


class AssetUpdateView(LoginRequiredMixin, UpdateView):
    model = Asset
    form_class = AssetUpdateForm
    success_url = reverse_lazy('assets:assets')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['title'] = 'update-asset'
        return context
