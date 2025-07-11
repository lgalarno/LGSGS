from django.conf import settings

from accounting.models import DisnatBook, CryptoBook

from decimal import Decimal

import datetime
import numpy as np
import pandas as pd

DISNAT_HEADERS = settings.DISNAT_HEADERS
CRYPTO_HEADERS = settings.CRYPTO_HEADERS


def csv_to_crypto_book(file, wallet):
    obj = CryptoBook.objects.filter(wallet=wallet)
    last_stored_element_date = None if not obj else obj.last().date
    return csv_to_book(file, wallet=wallet, headers=CRYPTO_HEADERS, last_stored_element_date=last_stored_element_date)


def csv_to_disnat_book(file, wallet):
    """
    Import data from a csv file to the db
    """
    obj = DisnatBook.objects.filter(wallet=wallet)
    last_stored_element_date = None if not obj else obj.last().date_de_reglement
    return csv_to_book(file, wallet=wallet, headers=DISNAT_HEADERS, last_stored_element_date=last_stored_element_date)


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
        # if mindate_filter and maxdate_filter:
        #     book = book.filter(date__gte=mindate_filter,
        #                        date__lte=maxdate_filter)
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
                                  classes="table table-striped",
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
            # for v in range(len(ventes)):
            #     date_vente_item = ventes.at[ventes.index[v], 'date']
            #     if date_vente_item > mindate_filter:
            #         quantity_item = float(ventes.at[ventes.index[v], 'quantity'])
            #         prix_vente_item = float(ventes.at[ventes.index[v], 'avg_price'])
            #         produit_vente_item = Decimal(quantity_item * prix_vente_item).quantize(Decimal("1.00"))
            #         cout_item = Decimal(quantity_item * prix_achat_item).quantize(Decimal("1.00"))
            #         profit_item = produit_vente_item - cout_item
            #         profit_net_item = (quantity_item * (prix_vente_item - prix_achat_item) -
            #                            ventes.at[ventes.index[v], 'fees'] - frais_achat_item)
            #         crypto.append(crypto_item)
            #         quantity_sold.append(quantity_item)
            #         date_achat.append(date_achat_item)
            #         date_vente.append(date_vente_item)
            #         produit_vente.append(produit_vente_item)
            #         cout.append(cout_item)
            #         profit.append(profit_item)
            #         profit_net.append(profit_net_item)
            #         frais_vente.append(ventes.at[ventes.index[v], 'fees'])
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
                                          classes="table table-striped",
                                          justify="left",
                                          table_id="table_book",
                                          na_rep='',
                                          float_format=lambda x: f'{x:10.6g}'
                                          )
    else:
        mindate, maxdate, net_profits = None, None, None
        final_df = "<p>Rien à afficher.</p>"
    return final_df, mindate, maxdate, net_profits


def disnat_books(wallet, mindate_filter=None, maxdate_filter=None, export=False):
    summary = {}
    book = DisnatBook.objects.filter(wallet=wallet)
    if book:
        mindate = book.first().date_de_reglement
        maxdate = book.last().date_de_reglement

        # get summary using the full book
        if export:
            summary = {}
        else:
            summary = summary_disnat(book, mindate_filter=mindate_filter, maxdate_filter=maxdate_filter)

        if mindate_filter and maxdate_filter:
            book = book.filter(date_de_reglement__gte=mindate_filter,
                               date_de_reglement__lte=maxdate_filter)

        book_values = book.values()
        df = pd.DataFrame.from_records(book_values, exclude=['id', 'wallet_id'])
        df = df.fillna(value=np.nan)
        df.columns = DISNAT_HEADERS
        if not export:
            df = df.to_html(index=False,
                                  #border=0,
                                  classes="table table-striped mt-3",
                                  justify="left",
                                  table_id="table_book",
                                  na_rep='')
    else:
        mindate, maxdate = None, None
        df = ""

    return df, summary, mindate, maxdate


def summary_disnat(book, mindate_filter=None, maxdate_filter=None) -> dict:
    today = datetime.datetime.now().date()
    book_values = book.values()
    df = pd.DataFrame.from_records(book_values, exclude=['id', 'wallet_id'])
    df = df.fillna(value=np.nan)
    first_date = df.date_de_reglement[0]
    maxdate = df.date_de_reglement[len(df)-1]
    mindate = df.date_de_reglement[0]

    # a request update may be the full period. When maxdate_filter is None, then full
    full = ((mindate == mindate_filter) and (maxdate == maxdate_filter)) or maxdate_filter is None
    if maxdate_filter and not full:
        df_to_maxdate = df[df.date_de_reglement.between(mindate, maxdate_filter)].reset_index()
        df_filtered = df[df.date_de_reglement.between(mindate_filter, maxdate_filter)].reset_index()
        first_date = df_filtered.date_de_reglement[0]
        last_date = df_to_maxdate.date_de_reglement[len(df_to_maxdate) - 1]
        # to calculate cotisation, interets, dividendes,retenue_impots
        type_agg = df_filtered.groupby('type_de_transaction').agg(montant_de_l_operation=
                                                                  ('montant_de_l_operation', 'sum'))
        balance = None  # set to None, so that % not shown in the view in disnat-summary-table.html
        #######################################
        # Calculate profits
        #######################################
        df_numero_id = df_to_maxdate.groupby('numero_id').filter(lambda x: len(x) > 1)
        profits_agg_temp = df_numero_id.groupby('numero_id', as_index=False).agg(
            montant_total=('montant_de_l_operation', 'sum'),
            date=('date_de_reglement', 'last')
        )
        profits_agg = profits_agg_temp[profits_agg_temp.date.between(mindate_filter, maxdate_filter)].reset_index()
        profits = profits_agg['montant_total'].sum()
    else:
        balance = df['montant_de_l_operation'].sum()
        last_date = df['date_de_reglement'][len(df) - 1]
        # to calculate cotisation, interets, dividendes,retenue_impots
        type_agg = df.groupby('type_de_transaction').agg(montant_total=('montant_de_l_operation', 'sum'))
        #######################################
        # Calculate profits
        #######################################
        # filter for items with numero_id appearing more than once - should be at least 1 ACHAT
        filtered_df = df.groupby('numero_id').filter(lambda x: len(x) > 1)

        profits_agg = filtered_df.groupby('numero_id').agg(montant_total=('montant_de_l_operation', 'sum'))
        profits = profits_agg['montant_total'].sum()

    type_de_transaction = list(type_agg.index)
    cotisation = type_agg.loc['COTISATION'].item() if 'COTISATION' in type_de_transaction else 0
    interets = type_agg.loc['INTÉRÊTS'].item() if 'INTÉRÊTS' in type_de_transaction else 0
    index_dividendes = [i for i in range(len(type_de_transaction)) if
                        type_de_transaction[i].startswith('DIVIDENDE')]
    dividendes = type_agg.iloc[index_dividendes].sum().item()
    retenue_impots = type_agg.loc["RETENUE D'IMPÔT"].item() if "RETENUE D'IMPÔT" in type_de_transaction else 0

    total_revenue = profits + retenue_impots + dividendes + interets

    # Calculate % profits if full table, not for partial
    days_total = today - first_date

    days_book = last_date - first_date
    if full:
        if days_total.days > 0 and cotisation > 0:
            percent_profits_today = Decimal((profits + retenue_impots + dividendes + interets) * 100 * 365 / (days_total.days * cotisation)).quantize(Decimal("1.00"))
        else:
            percent_profits_today = Decimal(0).quantize(Decimal("1.00"))
        if days_book.days > 0 and cotisation > 0:
            percent_profits_book = Decimal((profits + retenue_impots + dividendes + interets) * 100 * 365 / (
                    days_book.days * cotisation)).quantize(Decimal("1.00"))
        else:
            percent_profits_book = Decimal(0).quantize(Decimal("1.00"))
    else:
        percent_profits_book = None
        percent_profits_today = None

    summary = {
        'first_date': first_date,
        'last_date': last_date,
        "today": today,
        "days_book": days_book.days,
        "days_total": days_total.days,
        'balance': balance,
        'cotisation': cotisation,
        'interets': interets,
        'dividendes':dividendes,
        'retenue_impots': retenue_impots,
        'profits': profits,
        'percent_profits_today': percent_profits_today,
        'percent_profits_book': percent_profits_book,
        'total_revenue': total_revenue
    }
    return summary
