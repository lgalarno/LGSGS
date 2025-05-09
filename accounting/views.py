from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, HttpResponse, reverse
from django.utils.encoding import smart_str
from django.views.decorators.http import require_http_methods

import datetime
import os

from accounting.backend import csv_to_disnat_book,csv_to_crypto_book, disnat_books, crypto_book, crypto_for_taxes
from wallets.models import Wallet


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
                valid, mess = csv_to_crypto_book(file, wallet=wallet)
            else:
                valid, mess = csv_to_disnat_book(file, wallet=wallet)
            if valid:
                messages.success(request, "Nouvelles données entrées dans la base de données.")
                for m in mess:
                    messages.warning(request, m)
            else:
                messages.error(request, mess)
    if link_from == 'book-disnat':
        book, summary, mindate, maxdate = disnat_books(wallet, mindate_filter=None,
                                                       maxdate_filter=None)
        if book:
            mindate_filter = mindate
            maxdate_filter = maxdate
        else:
            mindate_filter, maxdate_filter = None, None
        context = {'wallet': wallet,
                   'book': book,
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
                                             maxdate_filter=None)
        if book:
            mindate_filter = mindate
            maxdate_filter = maxdate
        else:
            mindate_filter, maxdate_filter = None, None
        context = {'wallet': wallet,
                   'book': book,
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
    wallet.last_view = 'book_disnat'
    wallet.save()
    book = []
    if request.method == 'POST':
        task = request.POST.get('task')
        if task == 'refresh':
            mindate_filter = datetime.datetime.strptime(request.POST.get('start'), '%Y-%m-%d').date()
            maxdate_filter = datetime.datetime.strptime(request.POST.get('end'), '%Y-%m-%d').date()
            book, summary, mindate, maxdate = disnat_books(wallet, mindate_filter=mindate_filter,
                                               maxdate_filter=maxdate_filter)
        elif task == 'export':
            mindate_filter = datetime.datetime.strptime(request.POST.get('start'), '%Y-%m-%d').date()
            maxdate_filter = datetime.datetime.strptime(request.POST.get('end'), '%Y-%m-%d').date()
            book, summary, mindate, maxdate = disnat_books(wallet, mindate_filter=mindate_filter,
                                               maxdate_filter=maxdate_filter, export=True)

            path = os.path.join(settings.MEDIA_ROOT, 'files_temp', request.user.username)
            url_path = f'{settings.MEDIA_URL}/files_temp/'
            datesuffix = datetime.datetime.now().strftime('%Y-%m-%d')
            filename = f'{wallet.name}-{datesuffix}.csv'
            filepath = smart_str(f'{path}/{filename}')
            book.to_csv(filepath, index=False, header=True)
            response = HttpResponse(
                open(filepath, 'rb').read(),
                content_type='text/csv',
                headers={'Content-Disposition': f"attachment; filename = {filename.split(sep='/')[-1]}"},
            )
            response["HX-Redirect"] = smart_str(f'{url_path}{filename}')
            # if os.path.isfile(filepath):
            #     os.remove(filepath)
            return response

    else:
        book, summary, mindate, maxdate = disnat_books(wallet, mindate_filter=None,
                                           maxdate_filter=None)
        if book:
            mindate_filter = mindate
            maxdate_filter = maxdate
        else:
            mindate_filter, maxdate_filter = None, None
    context = {'wallet': wallet,
               'book': book,
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
    wallet.last_view = 'book_crypto'
    wallet.save()
    book = []
    if request.method == 'POST':
        task = request.POST.get('task')
        if task == 'refresh':
            mindate_filter = datetime.datetime.strptime(request.POST.get('start'), '%Y-%m-%d').date()
            maxdate_filter = datetime.datetime.strptime(request.POST.get('end'), '%Y-%m-%d').date()
            book, mindate, maxdate = crypto_book(wallet, mindate_filter=mindate_filter,
                                               maxdate_filter=maxdate_filter)
        elif task == 'export':
            mindate_filter = datetime.datetime.strptime(request.POST.get('start'), '%Y-%m-%d').date()
            maxdate_filter = datetime.datetime.strptime(request.POST.get('end'), '%Y-%m-%d').date()
            book, mindate, maxdate = crypto_book(wallet, mindate_filter=mindate_filter,
                                               maxdate_filter=maxdate_filter, export=True)

            path = os.path.join(settings.MEDIA_ROOT, 'files_temp')
            url_path = f'{settings.MEDIA_URL}/files_temp/'
            datesuffix = datetime.datetime.now().strftime('%Y-%m-%d')
            filename = f'{wallet.name}-{datesuffix}.csv'
            filepath = smart_str(f'{path}/{filename}')
            book.to_csv(filepath, index=False, header=True)
            response = HttpResponse(
                open(filepath, 'rb').read(),
                content_type='text/csv',
                headers={'Content-Disposition': f"attachment; filename = {filename.split(sep='/')[-1]}"},
            )
            response["HX-Redirect"] = smart_str(f'{url_path}{filename}')
            return response

    else:
        book, mindate, maxdate = crypto_book(wallet, mindate_filter=None,
                                             maxdate_filter=None)
        if book:
            mindate_filter = mindate
            maxdate_filter = maxdate
        else:
            mindate_filter, maxdate_filter = None, None

    context = {'wallet': wallet,
               'book': book,
               'mindate': mindate,
               'maxdate': maxdate,
               'maxdate_filter': maxdate_filter,
               'mindate_filter': mindate_filter,
               'link_from': "book-crypto"
               }
    return render(request, 'accounting/book-crypto.html', context)


def crypto_for_taxes_view(request, pk):
    wallet = Wallet.objects.get(pk=pk)
    wallet.last_view = 'crypto_taxes'
    wallet.save()
    if request.method == 'POST':
        task = request.POST.get('task')
        if task == 'refresh':
            mindate_filter = datetime.datetime.strptime(request.POST.get('start'), '%Y-%m-%d').date()
            maxdate_filter = datetime.datetime.strptime(request.POST.get('end'), '%Y-%m-%d').date()
            book, mindate, maxdate = crypto_for_taxes(wallet, mindate_filter=mindate_filter,
                                                      maxdate_filter=maxdate_filter)
        elif task == 'export':
            mindate_filter = datetime.datetime.strptime(request.POST.get('start'), '%Y-%m-%d').date()
            maxdate_filter = datetime.datetime.strptime(request.POST.get('end'), '%Y-%m-%d').date()
            book, mindate, maxdate = crypto_for_taxes(wallet, mindate_filter=mindate_filter,
                                                      maxdate_filter=maxdate_filter, export=True)
            path = os.path.join(settings.MEDIA_ROOT, 'files_temp')
            url_path = f'{settings.MEDIA_URL}/files_temp/'
            datesuffix = datetime.datetime.now().strftime('%Y-%m-%d')
            filename = f'{wallet.name}-impôts-{datesuffix}.csv'
            filepath = smart_str(f'{path}/{filename}')
            book.to_csv(filepath, index=False, header=True)
            response = HttpResponse(
                open(filepath, 'rb').read(),
                content_type='text/csv',
                headers={'Content-Disposition': f"attachment; filename = {filename.split(sep='/')[-1]}"},
            )
            response["HX-Redirect"] = smart_str(f'{url_path}{filename}')
            return response
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
