from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView, DetailView

from .forms import AssetForm, AssetUpdateForm
from .models import Asset  #, Ticker, Trader

# Create your views here.


# def create_asset(request):
#     form = AssetForm(request.POST or None)
#     if request.method == 'POST':
#         # symbol = request.POST.get('ticker-input')
#         ticker_id = request.POST.get('ticker-input')
#         trader_id = request.POST.get('trader-input')
#         if ticker_id and trader_id:
#             if form.is_valid():
#                 instance = form.save(commit=False)
#                 # ticker = Ticker.objects.get(pk=ticker_id)
#                 # instance.ticker = ticker
#                 # trader = Trader.objects.get(pk=trader_id)
#                 # instance.trader = trader
#                 instance.user = request.user
#                 # instance.current = current_price(ticker.symbol)
#                 instance.save()
#                 messages.success(request, 'Asset created!')
#         else:
#             messages.error(request, 'Please enter a valid ticker and a symbol.')
#
#     context = {
#         "title": "new-asset",
#         'asset_form': form,
#     }
#     return render(request, 'assets/new-asset.html', context)


# class AssetListView(LoginRequiredMixin, ListView):
#     model = Asset
#     template_name = 'assets/assets.html'
#
#     def get_queryset(self):
#         qs = Asset.objects.filter(user=self.request.user)  # .filter(transaction=None)  # show only old way
#         update_prices(qs)
#         return qs
#
#     def get_context_data(self, *args, **kwargs):
#         context = super().get_context_data()
#         context['title'] = 'assets'
#         context = {**context, **get_refresh_info()}
#         return context


# TODO add details
class AssetDetailView(DetailView):
    model = Asset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Asset-detail'
        return context


class AssetDeleteView(LoginRequiredMixin, DeleteView):
    model = Asset

    def get_success_url(self):
        if self.object.has_transaction:
            success_url = reverse_lazy('wallets:wallets')
        else:
            success_url = reverse_lazy('assets:assets')
        return success_url

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        self.get_success_url()
        self.object.delete()
        return redirect(self.get_success_url())


class AssetUpdateView(LoginRequiredMixin, UpdateView):
    model = Asset
    form_class = AssetUpdateForm

    def get_success_url(self):
        success_url = reverse_lazy('wallets:wallets')
        return success_url

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['title'] = 'update-asset'
        return context

    def get_form_kwargs(self):
        kwargs = super(AssetUpdateView, self).get_form_kwargs()
        kwargs['is_crypto'] = self.object.transaction.is_crypto
        return kwargs


# # TODO add details
# class TickerDetailView(DetailView):
#     model = Ticker
#
#     def get_context_data(self, *args, **kwargs):
#         context = super().get_context_data()
#         context['title'] = 'Ticker-detail'
#         return context
