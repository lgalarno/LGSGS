from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import render, HttpResponse, redirect, reverse, get_object_or_404
from django.utils import timezone

from decimal import Decimal

from wallets.forms import WalletForm, TransferForm, TransactionForm
from wallets.models import Wallet, Profit, Transaction, Transfer

from assets.backend import current_price, get_refresh_info, update_prices
from assets.models import Ticker, Trader, Asset


def wallet_create(request):
    form = WalletForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            instance = form.save(commit=False)
            instance.balance = 0
            instance.user = request.user
            instance.lastviewed = timezone.now()
            instance.save()
            response = HttpResponse()
            response["HX-Redirect"] = reverse("wallets:wallets")
            return response
    context = {
        "title": "create-wallet",
        'form_wallet': form,
    }
    return render(request, 'wallets/partials/wallet-form.html', context)


# TODO update creates new wallet. To fix.
def wallet_update(request, pk):
    wallet = get_object_or_404(Wallet, pk=pk)
    form = WalletForm(request.POST or None, instance=wallet)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            response = HttpResponse()
            response["HX-Redirect"] = reverse("wallets:wallets")
            return response
    context = {
        "title": "update-wallet",
        'wallet': wallet,
        'form_wallet': form,
    }
    return render(request, 'wallets/partials/wallet-update-form.html', context)


def wallet_detail(request, pk):
    wallet = get_object_or_404(Wallet, pk=pk)
    assets = Asset.objects.filter(transaction__wallet=wallet)
    profits = Profit.objects.filter(transaction_bought__wallet=wallet)
    total_profits = Decimal(profits.aggregate(Sum('profit', default=0))['profit__sum']
                            ).quantize(Decimal("1.00"))
    wallet.lastviewed = timezone.now()
    wallet.save()
    context = {
        "title": "wallet-detail",
        'wallet': wallet,
        'asset_list': assets,
        'profit_list': profits,
        'total_profits': total_profits,
        **get_refresh_info()
    }
    return render(request, 'wallets/partials/wallet-detail.html', context)


def transfer(request, pk):
    wallet = get_object_or_404(Wallet, pk=pk)
    form = TransferForm(request.POST or None, initial={'wallet': wallet})
    context = {
        "title": "transfer",
        'wallet': wallet
    }
    if request.method == "POST":
        if form.is_valid():
            instance = form.save(commit=False)
            w = instance.wallet
            w.balance = w.balance + instance.amount
            w.save()
            instance.save()
            context["wallet"] = w
            response = HttpResponse()
            response["HX-Redirect"] = reverse("wallets:wallets")
            return response
    context["form"] = form
    return render(request, 'wallets/partials/transfer-form-modal.html', context)


def buy(request, pk):
    wallet = get_object_or_404(Wallet, pk=pk)
    context = {
        "title": "buy",
        'wallet': wallet
    }
    form = TransactionForm(request.POST or None, initial={'wallet': wallet})
    if request.method == 'POST':
        ticker_id = request.POST.get('ticker-input')  # ticker_id not in TransactionForm
        trader_id = request.POST.get('trader-input')  # trader_id not in TransactionForm
        if ticker_id and trader_id:
            if form.is_valid():
                instance = form.save(commit=False)
                ticker = Ticker.objects.get(pk=ticker_id)
                # check if wallet has enough money.
                cost = Decimal(
                        instance.quantity * float(instance.price) + float(instance.change)).quantize(
                        Decimal("1.00"))
                trader = Trader.objects.get(pk=trader_id)
                if trader.fees_buy == 'money':
                    cost = cost + instance.fees  # fees in $ adds to
                    quantity = instance.quantity
                    fees_per_unit = Decimal(float(instance.fees) / quantity).quantize(
                        Decimal("1.000000"))
                elif trader.fees_buy == 'crypto':
                    quantity = instance.quantity - float(instance.fees)  # fees in crypto, thus deduct fees from amount
                    fees_per_unit = Decimal(float(instance.fees) * float(instance.price) / quantity).quantize(
                        Decimal("1.000000"))
                else:
                    form.add_error(None, "Trader improperly configured.")
                    # if ticker.type == 'equity':  # # fees per transaction
                    #     cost = cost + instance.fees  # may be fees in $ for equities
                    #     quantity = instance.quantity
                    # else:
                    #     quantity = instance.quantity - float(instance.fees)  # fees for crypto are in crypto
                if cost > wallet.balance:
                    form.add_error(None, "Not enough money in the wallet.")
                if not form.errors:
                    instance.ticker = ticker
                    # trader = Trader.objects.get(pk=trader_id)
                    instance.trader = trader
                    monitor = request.POST.get('monitor') == 'on'  # monitor not in TransactionForm
                    staking = request.POST.get('staking') == 'on'  # staking not in TransactionForm
                    # create an asset.
                    a = Asset(
                        user=request.user,
                        ticker=ticker,
                        trader=trader,
                        date=instance.date,
                        description=instance.description,
                        quantity=quantity,
                        price=instance.price,
                        fees_per_unit=fees_per_unit,
                        current=current_price(ticker.symbol, ticker.type),  # get the current price
                        margin=Decimal(request.POST.get('margin')),  # margin not in TransactionForm
                        monitor=monitor,
                        staking=staking
                    )
                    a.save()
                    # update wallet balance
                    wallet.balance = wallet.balance - cost
                    wallet.asset.add(a)
                    wallet.save()
                    # complete instance info
                    instance.type = 'buy'
                    instance.asset = a
                    instance.save()
                    response = HttpResponse()
                    response["HX-Redirect"] = reverse("wallets:wallets")
                    return response
        else:
            form.add_error(None, "Please enter a valid ticker and a symbol.")

    context["form"] = form
    return render(request, 'wallets/partials/buy-form.html', context)


def sell(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    wallet = asset.transaction.wallet
    context = {
        "title": "sell",
        'asset': asset
    }
    form = TransactionForm(request.POST or None,
                           initial={'wallet': wallet},
                           max_quantity=asset.quantity
                           )

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            asset_left = asset.quantity - instance.quantity   # update asset quantity
            # quantity_sold = float(request.POST.get('quantity'))
            if asset_left < 0:  # quantity_sold > asset.quantity:
                form.add_error(None, "Not enough units to sell.")
            else:
                # revenue = Decimal(instance.quantity * float(instance.price) + float(instance.change) - float(instance.fees)).quantize(Decimal("1.00"))
                # profit = revenue - Decimal(float(asset.price) * instance.quantity - float(asset.transaction.change)).quantize(Decimal("1.00"))
                # update Transaction instance
                instance.type = 'sell'
                instance.ticker = asset.ticker
                instance.trader = asset.trader

                paid = Decimal(instance.quantity * float(asset.transaction.price_per_share)).quantize(Decimal("1.00"))
                revenue = instance.total_revenue
                profit = revenue - paid
                try:  # catch error before asset and wallet update
                    instance.save()
                    p = Profit(
                        transaction_bought=asset.transaction,
                        transaction_sold=instance,
                        profit=profit
                    )
                    p.save()
                    # update asset_left

                    if asset_left == 0:
                        asset.delete()
                    else:
                        asset.quantity = asset_left
                        asset.save()

                    # update wallet balance
                    wallet.balance += instance.total_revenue
                    wallet.save()
                except:
                    print('error')
                    # if error and instance was saved, delete instance
                    # error while saving Profit
                    if instance.pk:
                        instance.delete()
                    messages.error(request, "Something went wrong")
                    response = HttpResponse()
                    response["HX-Redirect"] = reverse("wallets:wallets")
                    return response

            response = HttpResponse()
            response["HX-Redirect"] = reverse("wallets:wallets")
            return response
    context["form"] = form
    return render(request, 'wallets/partials/sell-form.html', context)


def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    context = {
        "title": "transaction",
        'transaction': transaction
    }
    return render(request, 'wallets/partials/transaction-detail.html', context)


def transaction_list(request, pk):
    wallet = get_object_or_404(Wallet, pk=pk)
    transactions = Transaction.objects.filter(wallet=wallet)
    context = {
        "title": "transaction-list",
        'transaction_list': transactions
    }
    return render(request, 'wallets/partials/transaction-list.html', context)


def asset_list(request, pk):
    wallet = get_object_or_404(Wallet, pk=pk)
    assets = Asset.objects.filter(wallet=wallet)
    update_prices(assets)
    context = {
        "title": "asset-list",
        'wallet': wallet,
        'asset_list': assets,
        **get_refresh_info()
    }
    return render(request, 'assets/partials/assets_table.html', context)


def transfer_list(request, pk):
    wallet = get_object_or_404(Wallet, pk=pk)
    transfers = Transfer.objects.filter(wallet=wallet)
    context = {
        "title": "asset-list",
        'transfer_list': transfers,
    }
    return render(request, 'wallets/partials/transfer-list.html', context)


def profit_list(request, pk):
    wallet = get_object_or_404(Wallet, pk=pk)
    profits = Profit.objects.filter(transaction_bought__wallet=wallet).order_by('-transaction_sold__date')
    #total_profits = Decimal(profits.aggregate(Sum('profit', default=0))['profit__sum']
    #                        ).quantize(Decimal("1.00"))
    context = {
        "title": "asset-list",
        'profit_list': profits,
        #'total_profits': total_profits,
    }
    return render(request, 'wallets/partials/profit-list.html', context)


def profit_detail(request, pk):
    profit_q = Profit.objects.get(pk=pk)
    purchased = profit_q.transaction_bought

    context = {
        "title": "transaction",
        'purchased': purchased,
        'sold': profit_q.transaction_sold,
        'marginal_cost': profit_q.marginal_cost,
        'marginal_profit': profit_q.marginal_profit
    }
    return render(request, 'wallets/partials/profit-detail.html', context)


# hidden function to update all profits when a correction was made to the code
def update(request):
    profits = Profit.objects.all()
    for p in profits:
        p.profit = p.marginal_profit
        p.save()

    return HttpResponse('done')
