
from accounting.models import DisnatBook, CryptoBook
from wallets.models import Wallet, Ticker

from decimal import Decimal

import datetime
import numpy as np
import pandas as pd


def csv_to_db(file, wallet, wallet_type, headers):
    """
    Import data from a csv file to the db
    """
    file_data = file.read().decode("utf-8-sig")
    lines = file_data.split("\r\n")
    file_headers = lines.pop(0)
    # loop over the lines and save them in db. If error , store as string and then display
    if wallet_type == 'equity':
        last = DisnatBook.objects.last()
    elif wallet_type == 'crypto':
        last = CryptoBook.objects.last()
    else:
        return False, f"Wallet type '{wallet.trader.type}' not supported"
    last_stored_element_date = None if not last else last.last()
    valid, mess = validate_headers(file_headers, headers)
    if not valid:
        return False, mess
    valid, mess = validate_ovelaps(lines[0], last_stored_element_date)
    if not valid:
        return False, mess

    if wallet_type == 'equity':
        mess = "New data was added to the database."
        try:
            for line in lines:
                fields = line.split(",")
                date_de_transaction = None if fields[0] == '' else datetime.datetime.strptime(fields[0], '%Y-%m-%d').date()
                date_de_reglement = datetime.datetime.strptime(fields[1], '%Y-%m-%d').date()
                type_de_transaction = fields[2]
                symbole = get_symbol(fields[4], wallet_type)
                if symbole is None and type_de_transaction in ['ACHAT','VENTE']:
                    mess = mess + f' Symbol {fields[4]} not found;'
                prix = None if fields[8] == "" else Decimal(float(fields[8])).quantize(Decimal("1.0000"))
                commission_payee = Decimal(float(fields[10])).quantize(Decimal("1.00"))
                montant_de_l_operation = Decimal(float(fields[11])).quantize(Decimal("1.00"))
                numero_id = None if fields[13] == '' else int(fields[13])
                newdata = DisnatBook(
                    wallet=wallet,
                    date_de_transaction=date_de_transaction,
                    date_de_reglement=date_de_reglement,
                    type_de_transaction=fields[2],
                    classe_d_actif=fields[3],
                    symbole=symbole,
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
                newdata.save()
        except Exception as e:
            return False, f"A problem occured while importing data: {e}. Check the line: {fields}"
    elif wallet_type == 'crypto':
        for line in lines:
            fields = line.split(",")
            newdata = CryptoBook(
            )
    return True, mess


def validate_headers(file_headers, headers):
    fields = file_headers.split(",")
    for i in range(len(headers)):
        if fields[i] != headers[i]:
            return False, f"Invalid file: column '{fields[i] }' found instead of '{headers[i]}'"
    return True, 'valid'


def validate_ovelaps(line, last_stored_element_date):
    fields = line.split(",")
    try:
        frst_new_element_date = datetime.datetime.strptime(fields[1], '%Y-%m-%d').date()
    except:
        return False, f"Expecting a date in the second column, first row. Got '{fields[1]}' instead."
    if last_stored_element_date and last_stored_element_date >= frst_new_element_date:
        return False, f"The last element stored in the datase is from {last_stored_element_date} and the first element in the csv file is from {frst_new_element_date}. Data should not overlap to prevent duplicates."
    return True, 'valid'


def get_symbol(s, type):
    symbol = None
    if s != '':
        if type == 'equity':
            to_query = s.split('-')[0]
        elif type == 'crypto':
            to_query = s.split('/')[0]
        else:
            to_query = s
        qs = Ticker.objects.filter(symbol__startswith=to_query)
        if len(qs) != 0:
            symbol = qs[0]
    return symbol


def get_books(wallet, wallet_type, mindate_filter=None, maxdate_filter=None, headers=None):
    book = []
    if wallet_type == 'crypto':
        book = CryptoBook.objects.filter(wallet=wallet)
    elif wallet_type == 'equity':
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
