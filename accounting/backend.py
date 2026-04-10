from django.conf import settings
from django.db.models import Sum

from accounting.models import DisnatBook, CryptoBook

from decimal import Decimal

import datetime
import numpy as np
import pandas as pd

DISNAT_HEADERS = settings.DISNAT_HEADERS
CRYPTO_HEADERS = settings.CRYPTO_HEADERS


def csv_to_book(file, wallet=None, headers=None, last_stored_element_date=None):
    file_data = file.read().decode("utf-8-sig")
    lines = file_data.split("\r\n")
    file_headers = lines.pop(0)
    # loop over the lines and save them in db. If error , store as string and then display
    valid, mess = validate_headers(file_headers, headers)
    if not valid:
        return False, mess
    valid, mess = validate_overlap(lines[0], last_stored_element_date)
    if not valid:
        return False, mess
    mess = []
    wallet_type = wallet.trader.type
    try:
        for line in lines:
            fields = line.split(",")
            if fields == ['']:  # last line empty
                break
            if wallet_type == "equity":
                fields = ['' if f == '-' else f for f in fields]  # in Disnat, sometimes '-' is used instead of empty
                date_de_transaction = None if fields[0] == '' else datetime.datetime.strptime(fields[0], '%Y-%m-%d').date()
                date_de_reglement = datetime.datetime.strptime(fields[1], '%Y-%m-%d').date()
                type_de_transaction = fields[2]
                prix = None if fields[8] == "" else Decimal(float(fields[8])).quantize(Decimal("1.0000"))
                commission_payee = Decimal(float(fields[10])).quantize(Decimal("1.00"))
                montant_de_l_operation = Decimal(float(fields[11])).quantize(Decimal("1.00"))
                numero_id = None if fields[13] == '' else int(fields[13])
                if (type_de_transaction in ['ACHAT', 'VENTE']) and (numero_id is None):
                    mess.append(f'Le numéro id est manquant pour la transaction du {date_de_reglement}')
                newdata = DisnatBook(
                    wallet=wallet,
                    date_de_transaction=date_de_transaction,
                    date_de_reglement=date_de_reglement,
                    type_de_transaction=fields[2],
                    classe_d_actif=fields[3],
                    symbole=fields[4],
                    description=fields[5],
                    marche=fields[6],
                    quantite=int(fields[7]),
                    prix=prix,
                    devise_du_prix=fields[9],
                    commission_payee=commission_payee,
                    montant_de_l_operation=montant_de_l_operation,
                    devise_du_compte=fields[12],
                    numero_id=numero_id,
                )
            elif wallet_type == "crypto":
                date = datetime.datetime.strptime(fields[1], '%Y-%m-%d').date()
                newdata = CryptoBook(
                    wallet=wallet,
                    date=date,
                    type=fields[0],
                    crypto=fields[3],
                    number_id=int(fields[2]),
                    quantity=float(fields[4]),
                    price=float(fields[5]),
                    fees=float(fields[6]),  # Transformed in $ in the model
                )
            newdata.save()
        # update wallet balance from the new data if wallet_type == "equity"
        if wallet_type == "equity":
            book = DisnatBook.objects.filter(wallet=wallet)
            wallet.balance = Decimal(book.aggregate(Sum('montant_de_l_operation', default=0))['montant_de_l_operation__sum']
                    ).quantize(Decimal("1.00"))
            wallet.balance_date = book.order_by('-date_de_reglement').first().date_de_reglement
            wallet.save()
    except Exception as e:
        return False, f"Un problème est survenu: {e}. Voir la ligne: {fields}"
    return True, mess


def validate_headers(file_headers, headers):
    fields = file_headers.split(",")
    for i in range(len(headers)):
        if fields[i] != headers[i]:
            return False, f"Fichier invalide: colonne '{fields[i] }' trouvée à la place de '{headers[i]}'"
    return True, 'valid'


def validate_overlap(line, last_stored_element_date):
    fields = line.split(",")
    try:
        frst_new_element_date = datetime.datetime.strptime(fields[1], '%Y-%m-%d').date()
    except:
        return False, f"Une date est attendue dans la deuxième colunne de la première rangée. '{fields[1]}' à la place."
    if last_stored_element_date and (last_stored_element_date >= frst_new_element_date):
        return False, f"Le dernier élément de la base de données est du {last_stored_element_date} et le premier élément du fichier csv file est du {frst_new_element_date}. Les données ne doivent pas se chevaucher pour éviter les duplicata"
    return True, 'valid'


def crypto_book(wallet, mindate_filter=None, maxdate_filter=None, export=False):
    book = CryptoBook.objects.filter(wallet=wallet)
    if book:
        mindate = book.first().date
        maxdate = book.last().date
        book_values = book.values()
        df = pd.DataFrame.from_records(book_values, exclude=['id', 'wallet_id'])
        df = df.fillna(value=np.nan)
        if mindate_filter and maxdate_filter:
            df = df[df.date.between(mindate_filter, maxdate_filter)]  #.reset_index()
        df.columns = CRYPTO_HEADERS
        if export:
            final_df = df
        else:
            final_df = df.to_html(index=False,
                                  #border=0,
                                  classes="table table-striped table_book",
                                  justify="left",
                                  table_id="table_book",
                                  na_rep='',
                                  float_format=lambda x: f'{x:10.6g}')
    else:
        mindate, maxdate = None, None
        final_df = "<p>Rien à afficher.</p>"
    return final_df, mindate, maxdate


def crypto_for_taxes(wallet, mindate_filter=None, maxdate_filter=None, export=False):
    book = CryptoBook.objects.filter(wallet=wallet)
    if book:
        mindate = book.first().date
        maxdate = book.last().date
        if mindate_filter and maxdate_filter:
            book = book.filter(date__lte=maxdate_filter)
        else:
            mindate_filter = mindate  # si pas inclu, set pour filtrer dans 'if date_vente_item > mindate_filter:'
        book_values = book.values()
        df = pd.DataFrame.from_records(book_values, exclude=['id', 'wallet_id'])
        df = df.fillna(value=np.nan)

        tbl = df.groupby(['type', 'number_id', 'date'], as_index=False).agg(avg_price=('price', 'mean'),
                                                                            quantity=('quantity', 'sum'),
                                                                            crypto=('crypto', 'first'),
                                                                            fees=('fees', 'first'))
        n_ids = tbl.loc[tbl['type'] == "VENTE", "number_id"].unique()
        crypto = []
        quantity_sold = []
        date_achat = []
        date_vente = []
        produit_vente = []
        cout = []
        frais_achat = []
        frais_vente = []
        profit = []
        profit_net = []
        for n in n_ids:
            ventes = tbl.loc[
                (tbl['number_id'] == n) & (tbl['type'] == "VENTE"), ['avg_price', 'quantity', 'date', 'fees']]
            achats = tbl.loc[
                (tbl['number_id'] == n) & (tbl['type'] == "ACHAT"), ['avg_price', 'date', 'crypto', 'fees']]
            crypto_item = achats['crypto'].item()
            date_achat_item = achats['date'].item()
            prix_achat_item = achats['avg_price'].item()
            frais_achat_item = achats['fees'].item()
            date_vente_item = ventes['date'].item()
            if date_vente_item > mindate_filter:
                quantity_item = ventes['quantity'].item()
                prix_vente_item = ventes['avg_price'].item()
                frais_vente_item = ventes['fees'].item()
                produit_vente_item = Decimal(quantity_item * prix_vente_item).quantize(Decimal("1.00"))
                cout_item = Decimal(quantity_item * prix_achat_item).quantize(Decimal("1.00"))
                profit_item = produit_vente_item - cout_item
                profit_net_item = (quantity_item * (prix_vente_item - prix_achat_item) -
                                   frais_vente_item - frais_achat_item)
                profit_net_item = Decimal(profit_net_item).quantize(Decimal("1.00"))
                crypto.append(crypto_item)
                quantity_sold.append(quantity_item)
                date_achat.append(date_achat_item)
                date_vente.append(date_vente_item)
                produit_vente.append(produit_vente_item)
                cout.append(cout_item)
                profit.append(profit_item)
                frais_achat.append(frais_achat_item)
                frais_vente.append(frais_vente_item)
                profit_net.append(profit_net_item)
        summary = {
            'Nom': crypto,
            'Quantité vendue': quantity_sold,
            "Date d'acquisition": date_achat,
            'Date de disposition': date_vente,
            'Produit de la disposition ': produit_vente,
            'Prix de base rajusté': cout,
            'Profit': profit,
            "Frais d'achat": frais_achat,
            'Frais de vente': frais_vente,
            'Profit net': profit_net
        }
        df_summary = pd.DataFrame(summary)
        df_summary.sort_values(by=['Date de disposition'], inplace=True)
        total_profits = df_summary.Profit.sum()  # not used
        net_profits = df_summary['Profit net'].sum()  # not used
        if export:  # export to csv
            final_df = df_summary
            net_profits = None
        else:
            final_df = df_summary.to_html(index=False,
                                          #border=0,
                                          classes="table table-striped table_book",
                                          justify="left",
                                          table_id="table_book",
                                          na_rep='',
                                          float_format=lambda x: f'{x:10.6g}'
                                          )
    else:
        mindate, maxdate, net_profits = None, None, None
        final_df = "<p>Rien à afficher.</p>"
    return final_df, mindate, maxdate, net_profits
