from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DeleteView, DetailView

from decimal import Decimal

from wallets.models import Wallet, Profit, Ticker
from assets.backend import get_refresh_info

# Create your views here.


def wallets(request):
    u = request.user
    user_wallets = Wallet.objects.filter(user=u)
    # last_view = {}
    # for w in user_wallets:
    #     if w.last_view:
    #         last_view[f'{w.pk}'] = w.last_view
    #     else:
    #         last_view[f'{w.pk}'] = 'asset'

        # last_view = {}
        # request.session["last_view"] = {f'{w.pk}': last_view}
    if user_wallets:
        current_wallet = user_wallets.order_by("last_viewed").last()
        if not current_wallet.last_view:
            current_wallet.last_view = 'assets'
        if not request.session.get("last_view"):
            last_view = {}
            for w in user_wallets:
                last_view[f'{w.pk}'] = 'assets'
                # last_view[f'{w.pk}'] = w.last_view if w.last_view else 'assets'
            request.session["last_view"] = last_view
        current_wallet.last_viewed = timezone.now()
        current_wallet.save()
        profits = Profit.objects.filter(transaction_bought__wallet=current_wallet)
        total_profits = Decimal(profits.aggregate(Sum('profit', default=0))['profit__sum']
                                ).quantize(Decimal("1.00"))
    else:
        current_wallet = None
        # total_balance = 0
        total_profits = 0

    context = {'wallets': user_wallets,
               # 'total_balance': total_balance,
               'wallet': current_wallet,
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
