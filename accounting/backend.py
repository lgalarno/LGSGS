
from accounting.models import DisnatBook, CryptoBook

from decimal import Decimal

import datetime
import numpy as np
import pandas as pd


def csv_to_crypto_book(file, wallet, headers):
    obj = CryptoBook.objects.filter(wallet=wallet)
    last_stored_element_date = None if not obj else obj.last().date
    return csv_to_book(file, wallet=wallet, headers=headers, last_stored_element_date=last_stored_element_date)


def csv_to_disnat_book(file, wallet, headers):
    """
    Import data from a csv file to the db
    """
    obj = DisnatBook.objects.filter(wallet=wallet)
    last_stored_element_date = None if not obj else obj.last().date_de_reglement
    return csv_to_book(file, wallet=wallet, headers=headers, last_stored_element_date=last_stored_element_date)


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
            print(fields)
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
                    fees=float(fields[6]),
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


def get_crypto_book(wallet, mindate_filter=None, maxdate_filter=None, headers=None):
    book = CryptoBook.objects.filter(wallet=wallet)
    if book:
        mindate = book.first().date
        maxdate = book.last().date
        if mindate_filter and maxdate_filter:
            book = book.filter(date__gte=mindate_filter,
                               date__lte=maxdate_filter)
        book_values = book.values()
        df = pd.DataFrame.from_records(book_values, exclude=['id', 'wallet_id'])
        df = df.fillna(value=np.nan)
        df.columns = headers
        final_df = df.to_html(index=False,
                              #border=0,
                              classes="table table-striped",
                              justify="left",
                              table_id="table_book",
                              na_rep='')
    else:
        mindate, maxdate = None, None
        final_df = ""
    return final_df, mindate, maxdate


def get_disnat_books(wallet, mindate_filter=None, maxdate_filter=None, headers=None):
    summary = {}
    book = DisnatBook.objects.filter(wallet=wallet)
    if book:
        mindate = book.first().date_de_reglement
        maxdate = book.last().date_de_reglement
        if mindate_filter and maxdate_filter:
            book = book.filter(date_de_reglement__gte=mindate_filter,
                               date_de_reglement__lte=maxdate_filter)

        book_values = book.values()
        df = pd.DataFrame.from_records(book_values, exclude=['id', 'wallet_id'])
        df = df.fillna(value=np.nan)

        # get summary
        summary = get_summary_disnat(df, mindate=mindate, maxdate=maxdate)

        df.columns = headers
        final_df = df.to_html(index=False,
                              #border=0,
                              classes="table table-striped",
                              justify="left",
                              table_id="table_book",
                              na_rep='')
    else:
        mindate, maxdate = None, None
        final_df = ""

    return final_df, summary, mindate, maxdate


# TODO profits
def get_summary_disnat(df, mindate=None, maxdate=None):
    summary = {}
    balance = df['montant_de_l_operation'].sum()
    type_agg = df.groupby('type_de_transaction').agg({'montant_de_l_operation': ['sum']})
    type_de_transaction = list(type_agg.index)
    cotisation = type_agg.loc['COTISATION'].item() if 'COTISATION' in type_de_transaction else 0
    interets = type_agg.loc['INTÉRÊTS'].item() if 'INTÉRÊTS' in type_de_transaction else 0
    index_dividendes = [i for i in range(len(type_de_transaction)) if
                        type_de_transaction[i].startswith('DIVIDENDE')]
    dividendes = type_agg.iloc[index_dividendes].sum().item()
    retenue_impots = type_agg.loc["RETENUE D'IMPÔT"].item() if "RETENUE D'IMPÔT" in type_de_transaction else 0
    filtered_df = df.groupby('numero_id').filter(lambda x: len(x) > 1)
    profits_agg = filtered_df.groupby('numero_id').agg({'montant_de_l_operation': ['sum']})
    profits = profits_agg['montant_de_l_operation'].sum().item()
    today = datetime.datetime.now().date()
    first_date = df['date_de_reglement'][0]
    diff_total = today - first_date
    if diff_total.days > 0 and cotisation > 0:
        percent_profits_today = Decimal((profits + retenue_impots + dividendes + interets) * 100 * 365 / (diff_total.days * cotisation)).quantize(Decimal("1.00"))
    else:
        percent_profits_today = Decimal(0).quantize(Decimal("1.00"))
    last_date = df['date_de_reglement'][len(df) - 1]
    diff_book = last_date - first_date
    if diff_book.days > 0 and cotisation > 0:
        percent_profits_book = Decimal((profits + retenue_impots + dividendes + interets) * 100 * 365 / (
                diff_book.days * cotisation)).quantize(Decimal("1.00"))
    else:
        percent_profits_book = Decimal(0).quantize(Decimal("1.00"))

    total_revenue = profits + retenue_impots + dividendes + interets
    summary = {
        'cols': [''],
        'first_date': first_date,
        'last_date': last_date,
        "today": today,
        "days_book": diff_book.days,
        "days_total": diff_total.days,
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
