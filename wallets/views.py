from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView

from decimal import Decimal

from wallets.models import Wallet, Profit, Ticker
from assets.models import Asset
from assets.backend import get_refresh_info, update_prices
# Create your views here.


def wallets(request):
    u = request.user
    user_wallets = Wallet.objects.filter(user=u)
    if user_wallets:
        current_wallet = user_wallets.order_by("lastviewed").last()
        assets = Asset.objects.filter(wallet=current_wallet)
        profits = Profit.objects.filter(transaction_bought__wallet=current_wallet)
        total_profits = Decimal(profits.aggregate(Sum('profit', default=0))['profit__sum']
                                ).quantize(Decimal("1.00"))
        update_prices(assets)
        total_balance = u.total_balance
    else:
        current_wallet = None
        assets = None
        total_balance = 0
        total_profits = 0

    context = {'wallets': user_wallets,
               'total_balance': total_balance,
               'wallet': current_wallet,
               'asset_list': assets,
               # 'profit_list': profits,
               'total_profits': total_profits,
               **get_refresh_info()
               }
    return render(request, 'wallets/wallets.html', context)


class WalletDeleteView(LoginRequiredMixin, DeleteView):
    model = Wallet
    success_url = reverse_lazy('wallets:wallets')

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect(self.get_success_url())


# TODO add details
class TickerDetailView(DetailView):
    model = Ticker

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Ticker-detail'
        return context
