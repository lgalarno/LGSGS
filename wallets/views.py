from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from decimal import Decimal

from wallets.models import Wallet, Profit
from assets.models import Asset

# Create your views here.


def wallets(request):
    user_wallets = Wallet.objects.filter(user=request.user)
    if user_wallets:
        current_wallet = user_wallets.order_by("lastviewed").last()
        assets = Asset.objects.filter(transaction__wallet=current_wallet)
        profits = Profit.objects.filter(transaction_bought__wallet=current_wallet)
        total_profits = Decimal(profits.aggregate(Sum('profit', default=0))['profit__sum']
                                ).quantize(Decimal("1.00"))
        print(total_profits)
        u = request.user
        total_balance = u.total_balance
    else:
        current_wallet = None
        assets = None
        profits = None
        total_balance = 0
        total_profits = 0

    context = {'wallets': user_wallets,
               'total_balance': total_balance,
               'wallet': current_wallet,
               'asset_list': assets,
               'profit_list': profits,
               'total_profits': total_profits
               }
    return render(request, 'wallets/wallets.html', context)


#TODO in change / edit view?
class WalletDeleteView(LoginRequiredMixin, DeleteView):
    model = Wallet
    success_url = reverse_lazy('wallets:wallets')

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect(self.get_success_url())