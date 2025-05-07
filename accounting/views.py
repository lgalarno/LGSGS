from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, HttpResponse, reverse
from django.views.decorators.http import require_http_methods

import datetime

from accounting.backend import csv_to_disnat_book,csv_to_crypto_book, disnat_books, crypto_book, crypto_for_taxes
from wallets.models import Wallet


DISNAT_HEADERS = settings.DISNAT_HEADERS
CRYPTO_HEADERS = settings.CRYPTO_HEADERS

# Create your views here.


@require_http_methods(["POST"])
def upload(request, pk):
    file = request.FILES.get('formFile')
    link_from = request.POST.get('link_from')
    wallet = Wallet.objects.get(pk=pk)
    if file:
        if not file.name.endswith('.csv'):
            messages.error(request, f"Erreur: Ce n'est pas un fichier csv")
        else:
            if wallet.is_crypto:
                valid, mess = csv_to_crypto_book(file, wallet=wallet, headers=CRYPTO_HEADERS)
            else:
                valid, mess = csv_to_disnat_book(file, wallet=wallet, headers=DISNAT_HEADERS)
            if valid:
                messages.success(request, "Nouvelles données entrées dans la base de données.")
                for m in mess:
                    messages.warning(request, m)
            else:
                messages.error(request, mess)
    if link_from == 'book-disnat':
        book, summary, mindate, maxdate = disnat_books(wallet, mindate_filter=None,
                                                       maxdate_filter=None, headers=DISNAT_HEADERS)
        if book:
            mindate_filter = mindate
            maxdate_filter = maxdate
        else:
            mindate_filter, maxdate_filter = None, None
        context = {'wallet': wallet,
                   'book': book,
                   'headers': DISNAT_HEADERS,
                   'mindate': mindate,
                   'maxdate': maxdate,
                   'maxdate_filter': maxdate_filter,
                   'mindate_filter': mindate_filter,
                   'summary': summary,
                   'link_from': "book-disnat"
                   }
        return render(request, 'accounting/book-disnat.html', context)

    elif link_from == 'book-crypto':
        book, mindate, maxdate = crypto_book(wallet, mindate_filter=None,
                                             maxdate_filter=None, headers=CRYPTO_HEADERS)
        if book:
            mindate_filter = mindate
            maxdate_filter = maxdate
        else:
            mindate_filter, maxdate_filter = None, None
        context = {'wallet': wallet,
                   'book': book,
                   'headers': CRYPTO_HEADERS,
                   'mindate': mindate,
                   'maxdate': maxdate,
                   'maxdate_filter': maxdate_filter,
                   'mindate_filter': mindate_filter,
                   'link_from': "book-crypto"
                   }
        return render(request, 'accounting/book-crypto.html', context)
    elif link_from == 'crypto-for-taxes':
        book, mindate, maxdate = crypto_for_taxes(wallet, mindate_filter=None,
                                                  maxdate_filter=None)
        mindate_filter = mindate
        maxdate_filter = maxdate
        context = {'wallet': wallet,
                   'book': book,
                   'mindate': mindate,
                   'maxdate': maxdate,
                   'maxdate_filter': maxdate_filter,
                   'mindate_filter': mindate_filter,
                   'link_from': "crypto-for-taxes"
                   }
        return render(request, 'accounting/crypto-for-taxes.html', context)
    messages.error(request, "Un problême est survenu: la page de téléchargement n'est pas configurée correctement.")
    response = HttpResponse()
    response["HX-Redirect"] = reverse("wallets:wallets")
    return response


def book_disnat(request, pk):
    wallet = Wallet.objects.get(pk=pk)
    book = []
    if request.method == 'POST':
        task = request.POST.get('task')
        if task == 'refresh':
            mindate_filter = datetime.datetime.strptime(request.POST.get('start'), '%Y-%m-%d').date()
            maxdate_filter = datetime.datetime.strptime(request.POST.get('end'), '%Y-%m-%d').date()
            print(mindate_filter, maxdate_filter)
            book, summary, mindate, maxdate = disnat_books(wallet, mindate_filter=mindate_filter,
                                               maxdate_filter=maxdate_filter, headers=DISNAT_HEADERS)
    else:
        book, summary, mindate, maxdate = disnat_books(wallet, mindate_filter=None,
                                           maxdate_filter=None, headers=DISNAT_HEADERS)
        if book:
            mindate_filter = mindate
            maxdate_filter = maxdate
        else:
            mindate_filter, maxdate_filter = None, None
    context = {'wallet': wallet,
               'book': book,
               'headers': DISNAT_HEADERS,
               'mindate': mindate,
               'maxdate': maxdate,
               'maxdate_filter': maxdate_filter,
               'mindate_filter': mindate_filter,
               'summary': summary,
               'link_from': "book-disnat"
               }
    return render(request, 'accounting/book-disnat.html', context)


# TODO Crypto view/export for taxes
def book_crypto(request, pk):
    wallet = Wallet.objects.get(pk=pk)
    book = []
    if request.method == 'POST':
        task = request.POST.get('task')
        if task == 'refresh':
            mindate_filter = datetime.datetime.strptime(request.POST.get('start'), '%Y-%m-%d').date()
            maxdate_filter = datetime.datetime.strptime(request.POST.get('end'), '%Y-%m-%d').date()
            book, mindate, maxdate = crypto_book(wallet, mindate_filter=mindate_filter,
                                               maxdate_filter=maxdate_filter, headers=CRYPTO_HEADERS)
    else:
        book, mindate, maxdate = crypto_book(wallet, mindate_filter=None,
                                             maxdate_filter=None, headers=CRYPTO_HEADERS)
        if book:
            mindate_filter = mindate
            maxdate_filter = maxdate
        else:
            mindate_filter, maxdate_filter = None, None

    context = {'wallet': wallet,
               'book': book,
               'headers': CRYPTO_HEADERS,
               'mindate': mindate,
               'maxdate': maxdate,
               'maxdate_filter': maxdate_filter,
               'mindate_filter': mindate_filter,
               'link_from': "book-crypto"
               }
    return render(request, 'accounting/book-crypto.html', context)


def crypto_for_taxes_view(request, pk):
    wallet = Wallet.objects.get(pk=pk)
    if request.method == 'POST':
        mindate_filter = datetime.datetime.strptime(request.POST.get('start'), '%Y-%m-%d').date()
        maxdate_filter = datetime.datetime.strptime(request.POST.get('end'), '%Y-%m-%d').date()
        book, mindate, maxdate = crypto_for_taxes(wallet, mindate_filter=mindate_filter,
                                                  maxdate_filter=maxdate_filter)
    else:
        book, mindate, maxdate = crypto_for_taxes(wallet, mindate_filter=None,
                                                  maxdate_filter=None)
        mindate_filter = mindate
        maxdate_filter = maxdate

    context = {'wallet': wallet,
               'book': book,
               'mindate': mindate,
               'maxdate': maxdate,
               'maxdate_filter': maxdate_filter,
               'mindate_filter': mindate_filter,
               'link_from': "crypto-for-taxes"
               }
    return render(request, 'accounting/crypto-for-taxes.html', context)


def export(request):
    return HttpResponse("export")
