from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, HttpResponse

import datetime

from accounting.models import DisnatBook, CryptoBook
from accounting.backend import csv_to_disnat_book, csv_to_crypto_book, get_disnat_books, get_crypto_book
from wallets.models import Wallet


DISNAT_HEADERS = settings.DISNAT_HEADERS
CRYPTO_HEADERS = settings.CRYPTO_HEADERS

# Create your views here.


def book_disnat(request, pk):
    wallet = Wallet.objects.get(pk=pk)
    headers = DISNAT_HEADERS
    if request.method == 'POST':
        task = request.POST.get('task')
        print(task)
        print(request.POST)
        if task == 'upload':
            file = request.FILES.get('formFile')
            if not file.name.endswith('.csv'):
                messages.error(request, f"Error: This is not a csv file")
            else:
                valid, mess = csv_to_disnat_book(file, wallet, headers)
                if valid:
                    messages.success(request, "New data was added to the database.")
                    for m in mess:
                        messages.warning(request, m)
                else:
                    messages.error(request, mess)
            book, summary, mindate, maxdate = get_disnat_books(wallet, mindate_filter=None,
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
            book, summary, mindate, maxdate = get_disnat_books(wallet, mindate_filter=mindate_filter,
                                               maxdate_filter=maxdate_filter, headers=headers)
    else:
        book, summary, mindate, maxdate = get_disnat_books(wallet, mindate_filter=None,
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
               'summary': summary
               }
    return render(request, 'accounting/book-disnat.html', context)


# TODO Crypto part
# TODO Crypto veiew/export for taxes
def book_crypto(request, pk):
    wallet = Wallet.objects.get(pk=pk)
    headers = DISNAT_HEADERS
    if request.method == 'POST':
        task = request.POST.get('task')
        print(task)
        print(request.POST)
        if task == 'upload':
            file = request.FILES.get('formFile')
            if not file.name.endswith('.csv'):
                messages.error(request, f"Error: This is not a csv file")
            else:
                valid, mess = csv_to_crypto_book(file, wallet, headers)
                if valid:
                    messages.success(request, "New data was added to the database.")
                    for m in mess:
                        messages.warning(request, m)
                else:
                    messages.error(request, mess)
            book, summary, mindate, maxdate = get_disnat_books(wallet, mindate_filter=None,
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
            book, summary, mindate, maxdate = get_crypto_book(wallet, mindate_filter=mindate_filter,
                                               maxdate_filter=maxdate_filter, headers=headers)
    else:
        book, summary, mindate, maxdate = get_crypto_book(wallet, mindate_filter=None,
                                           maxdate_filter=None, headers=headers)
        if book:
            mindate_filter = mindate
            maxdate_filter = maxdate
        else:
            mindate_filter, maxdate_filter = None, None

    print(summary)
    context = {'wallet': wallet,
               'book': book,
               'headers': headers,
               'mindate': mindate,
               'maxdate': maxdate,
               'maxdate_filter': maxdate_filter,
               'mindate_filter': mindate_filter,
               'summary': summary
               }
    return render(request, 'accounting/book-crypto.html', context)


def export(request):
    return HttpResponse("export")

