from django.shortcuts import render, HttpResponse
from django.utils import timezone

from assets.backend import update_prices, get_refresh_info
from assets.forms import TickerForm, TraderForm
from assets.models import Ticker, Asset, Trader


def ticker_list(request):
    context = {
        'tickers': Ticker.objects.all(),
    }
    return render(request, 'assets/partials/ticker-select.html', context)


def ticker_create(request):
    print('ticker_create')
    form = TickerForm(request.POST or None)
    if request.method == "POST":

        if form.is_valid():
            form.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'tickerListChanged'})
    context = {
        "title": "new-ticker",
        'form_ticker': form,
    }
    return render(request, 'assets/partials/ticker-form.html', context)


def trader_list(request):
    print('trader_list')
    context = {
        'traders': Trader.objects.all(),
    }
    return render(request, 'assets/partials/trader-select.html', context)


def trader_create(request):
    print('trader_create')
    form = TraderForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'traderListChanged'})
    context = {
        "title": "new-trader",
        'form_trader': form,
    }
    return render(request, 'assets/partials/trader-form.html', context)


def asset_list(request):
    print('asset_list')
    qs = Asset.objects.filter(user=request.user)
    update_prices(qs)
    context = {
        'asset_list': qs,
        **get_refresh_info()
    }
    return render(request, 'assets/partials/assets_table.html', context)

#
# def ticker_validate(request):
#     print('ticker_validate')
#     symbol = request.POST['ticker-input'].upper()
#     obj = Ticker.objects.filter(symbol=symbol).first()
#     if not obj:
#         ticker = yf.Ticker(symbol)
#         info = None
#         try:
#             info = ticker.info
#             obj = Ticker(symbol=symbol,
#                          name=info['name']
#                          )
#             obj.save()
#         except:
#             # messages.error(request, "Symbol does not exist")
#             context = {
#                 "title": "new-asset",
#                 'symbol': symbol,
#                 "tickers": Ticker.objects.all(),
#                 'error': "Symbol does not exist",
#             }
#             return render(request, 'assets/partials/asset-form.html', context)
#
#     initial_dict = {
#         "ticker": obj.id,
#     }
#     form = AssetForm(initial=initial_dict)
#     context = {
#         "title": "new-asset",
#         'asset_form': form,
#         'ticker': obj,
#     }
#     return render(request, 'assets/partials/asset-form.html', context)
