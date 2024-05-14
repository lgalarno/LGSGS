from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView, DetailView

from .backend import update_prices, current_price, get_refresh_info
from .forms import AssetForm, AssetUpdateForm
from .models import Asset, Ticker, Trader

# Create your views here.


def create_asset(request):
    form = AssetForm(request.POST or None)
    if request.method == 'POST':
        symbol = request.POST.get('ticker-input')
        if symbol:

            if form.is_valid():
                instance = form.save(commit=False)
                q = Ticker.objects.get(pk=request.POST.get('ticker-input'))
                instance.ticker = q
                q = Trader.objects.get(pk=request.POST.get('trader-input'))
                instance.trader = q
                instance.user = request.user
                instance.current = current_price(symbol)
                instance.save()
                messages.success(request, 'Asset created!')
        else:
            messages.error(request, 'Please enter a valid ticker or create a new one.')

    context = {
        "title": "new-asset",
        'asset_form': form,
    }
    return render(request, 'assets/new-asset.html', context)


class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'assets/assets.html'

    def get_queryset(self):
        qs = Asset.objects.filter(user=self.request.user)
        update_prices(qs)
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        # pt = PeriodicTask.objects.get(name='update_prices-30-minutes')  # name in celery.py
        # min = 240 - settings.UPDT_INTERVAL
        # context['update_at'] = pt.last_run_at + relativedelta(minutes=-min)  # -240 min for ETC then + 30min
        # context['last_updated'] = timezone.now() + relativedelta(minutes=-240)
        context['title'] = 'assets'
        context = {**context, **get_refresh_info()}
        return context


# TODO add details
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
