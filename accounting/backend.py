from django.db.models import Sum

from accounting.models import DisnatBook, CryptoBook

from decimal import Decimal

import datetime


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
