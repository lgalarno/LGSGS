from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, HttpResponse
from django.http import HttpResponseBadRequest

import datetime

from accounting.models import DisnatBook, CryptoBook
from accounting.backend import csv_to_db, get_books
from wallets.models import Wallet


DISNAT_HEADERS = settings.DISNAT_HEADERS
CRYPTO_HEADERS = settings.CRYPTO_HEADERS

# Create your views here.


# TODO show the overview with balance,  profits, % etc
# TODO Crypto part
# TODO Crypto veiew/export for taxes
def book(request, pk):
    wallet = Wallet.objects.get(pk=pk)
    wallet_type = wallet.trader.type
    headers = CRYPTO_HEADERS if wallet_type == 'crypto' else DISNAT_HEADERS
    if request.method == 'POST':
        task = request.POST.get('task')
        print(task)
        print(request.POST)
        if task == 'upload':
            file = request.FILES.get('formFile')
            if not file.name.endswith('.csv'):
                messages.error(request, f"Error: This is not a csv file")
            else:
                valid, mess = csv_to_db(file, wallet, wallet_type, headers)
                if valid:
                    messages.success(request, mess)
                else:
                    messages.error(request, mess)
            book, mindate, maxdate = get_books(wallet, wallet_type, mindate_filter=None,
                                               maxdate_filter=None, headers=headers)
            if book:
                mindate_filter = mindate
                maxdate_filter = maxdate
            else:
                mindate_filter, maxdate_filter = None, None
        elif task == 'export':
            pass
        elif task == 'refresh':
            mindate_filter = datetime.datetime.strptime(request.POST.get('start'), '%Y-%m-%d').date()
            maxdate_filter = datetime.datetime.strptime(request.POST.get('end'), '%Y-%m-%d').date()
            book, mindate, maxdate = get_books(wallet, wallet_type, mindate_filter=mindate_filter,
                                               maxdate_filter=maxdate_filter, headers=headers)
    else:
        book, mindate, maxdate = get_books(wallet, wallet_type, mindate_filter=None,
                                           maxdate_filter=None, headers=headers)
        if book:
            mindate_filter = mindate
            maxdate_filter = maxdate
        else:
            mindate_filter, maxdate_filter = None, None
    context = {'wallet': wallet,
               'book': book,
               'headers': headers,
               'mindate': mindate,
               'maxdate': maxdate,
               'maxdate_filter': maxdate_filter,
               'mindate_filter': mindate_filter,
               }
    return render(request, 'accounting/book.html', context)


def export(request):
    return HttpResponse("export")



