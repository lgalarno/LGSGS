from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, HttpResponse, reverse
from django.views.decorators.http import require_http_methods

import datetime

from accounting.classes import DisnatLedger, CryptoLedger
from accounting.models import DisnatBook, CryptoBook
from accounting.backend import csv_to_book
from wallets.models import Wallet

DISNAT_HEADERS = settings.DISNAT_HEADERS
CRYPTO_HEADERS = settings.CRYPTO_HEADERS


@require_http_methods(["POST"])
def upload(request, pk):
    file = request.FILES.get('formFile')
    wallet = Wallet.objects.get(pk=pk)
    if file:
        if not file.name.endswith('.csv'):
            messages.error(request, f"Erreur: Ce n'est pas un fichier csv")
        else:
            if wallet.is_crypto:
                obj = CryptoBook.objects.filter(wallet=wallet)
                last_stored_element_date = None if not obj else obj.last().date
                valid, mess = csv_to_book(file, wallet=wallet, headers=CRYPTO_HEADERS,
                                   last_stored_element_date=last_stored_element_date)
            else:
                obj = DisnatBook.objects.filter(wallet=wallet)
                last_stored_element_date = None if not obj else obj.last().date_de_reglement
                valid, mess = csv_to_book(file, wallet=wallet, headers=DISNAT_HEADERS,
                                   last_stored_element_date=last_stored_element_date)
            if valid:
                messages.success(request, "Nouvelles données entrées dans la base de données.")
                for m in mess:
                    messages.warning(request, m)
            else:
                messages.error(request, mess)
    response = HttpResponse()
    response["HX-Redirect"] = reverse("wallets:wallets")
    return response


def book_disnat(request, pk):
    wallet = Wallet.objects.get(pk=pk)
    request.session["last_view"][f'{wallet.pk}'] = 'book_disnat'
    request.session["update"] = 'true'  # mock to update session because of using dict
    if request.method == 'POST':
        mindate_filter = datetime.datetime.strptime(request.POST.get('start'), '%Y-%m-%d').date()
        maxdate_filter = datetime.datetime.strptime(request.POST.get('end'), '%Y-%m-%d').date()
    else:
        mindate_filter, maxdate_filter = None, None

    book = DisnatBook.objects.filter(wallet=wallet)
    if book:
        df = DisnatLedger(book_values=book.values(), date_min_filter=mindate_filter, date_max_filter=maxdate_filter)
        summary = df.summary()
        html_book = df.html_table()
        mindate = df.first_date
        maxdate = df.last_date
        if request.method == 'GET':
            mindate_filter = mindate
            maxdate_filter = maxdate
    else:
        html_book = []
        summary = {}
        mindate, maxdate = None, None

    context = {'wallet': wallet,
               'book': html_book,
               'mindate': mindate,
               'maxdate': maxdate,
               'maxdate_filter': maxdate_filter,
               'mindate_filter': mindate_filter,
               'summary': summary,
               'csvfilename': wallet.name,
               }
    return render(request, 'accounting/book-disnat.html', context)


# TODO total (profits)?
def book_crypto(request, pk):
    wallet = Wallet.objects.get(pk=pk)
    request.session["last_view"][f'{wallet.pk}'] = 'book_crypto'
    request.session["update"] = 'true'  # mock to update session because of using dict
    if request.method == 'POST':
        mindate_filter = datetime.datetime.strptime(request.POST.get('start'), '%Y-%m-%d').date()
        maxdate_filter = datetime.datetime.strptime(request.POST.get('end'), '%Y-%m-%d').date()
        book = CryptoBook.objects.filter(wallet=wallet, date__gte=mindate_filter, date__lte=maxdate_filter)
    else:
        book = CryptoBook.objects.filter(wallet=wallet)

    if book:
        df = CryptoLedger(book_values=book.values())
        html_book = df.html_table()
        mindate = book.first().date
        maxdate = book.last().date
    else:
        html_book = None
        mindate, maxdate = None, None
        mindate_filter, maxdate_filter = None, None

    if request.method == 'GET':
        mindate_filter = mindate
        maxdate_filter = maxdate

    context = {'wallet': wallet,
               'book': html_book,
               'mindate': mindate,
               'maxdate': maxdate,
               'maxdate_filter': maxdate_filter,
               'mindate_filter': mindate_filter,
               'csvfilename': wallet.name,
               }
    return render(request, 'accounting/book-crypto.html', context)


def crypto_for_taxes_view(request, pk):
    wallet = Wallet.objects.get(pk=pk)
    request.session["last_view"][f'{wallet.pk}'] = 'crypto_taxes'
    request.session["update"] = 'true'  # mock to update session because of using dict
    book = CryptoBook.objects.filter(wallet=wallet)
    if book:
        maxdate = book.last().date
        mindate = book.first().date
        if request.method == 'POST':
            mindate_filter = datetime.datetime.strptime(request.POST.get('start'), '%Y-%m-%d').date()
            maxdate_filter = datetime.datetime.strptime(request.POST.get('end'), '%Y-%m-%d').date()
            book = book.filter(date__lte=maxdate_filter)
        else:
            mindate_filter = mindate
            maxdate_filter = maxdate
        df = CryptoLedger(book_values=book.values(), date_min_filter=mindate_filter, date_max_filter=maxdate_filter, taxes=True)
        html_book = df.table_taxes()
        net_profits = df.net_profits

    else:
        html_book = None
        mindate, maxdate = None, None
        mindate_filter, maxdate_filter = None, None
        net_profits = None

    context = {'wallet': wallet,
               'book': html_book,
               'mindate': mindate,
               'maxdate': maxdate,
               'maxdate_filter': maxdate_filter,
               'mindate_filter': mindate_filter,
               'net_profits': net_profits,
               'csvfilename': f'{wallet.name}-impôts',
               }
    return render(request, 'accounting/crypto-for-taxes.html', context)
