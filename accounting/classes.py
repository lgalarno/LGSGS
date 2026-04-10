from django.db.models import QuerySet
from django.utils.datetime_safe import date

from decimal import Decimal

import datetime
import numpy as np
import pandas as pd


class DisnatLedger:
    col_headers = ["Date de transaction", "Date de règlement", "Type de transaction", "Classe d'actif",
     "Symbole", "Description", "Marché", "Quantité", "Prix", "Devise du prix", "Commission payée",
     "Montant de l'opération", "Devise du compte", "Id"]

    def __init__(self, book_values:QuerySet = None, date_min_filter:date = None, date_max_filter:date = None):
        self.df = pd.DataFrame.from_records(book_values, exclude=['id', 'wallet_id'])
        self.df = self.df.fillna(value=np.nan)
        self.first_date = self.df.date_de_reglement[0]
        self.last_date = self.df.date_de_reglement[len(self.df) - 1]
        self.date_min_filter = date_min_filter
        self.date_max_filter = date_max_filter
        self.full = ((self.first_date == date_min_filter) and (self.last_date == date_max_filter)) or date_max_filter is None

    def html_table(self):
        if self.date_min_filter and self.date_max_filter:
            df = self.df[self.df.date_de_reglement.between(self.date_min_filter, self.date_max_filter)]
        else:
            df = self.df
        df.columns = self.col_headers
        return df.to_html(index=False,
                          #border=0,
                          classes="table table-striped mt-3 table_book",
                          justify="left",
                          table_id="table_book",
                          na_rep='')

    def summary(self):
        today = datetime.datetime.now().date()
        if self.date_max_filter and not self.full:
            df_to_date_max = self.df[self.df.date_de_reglement.between(self.first_date, self.date_max_filter)].reset_index()
            df_filtered = self.df[self.df.date_de_reglement.between(self.date_min_filter , self.date_max_filter)].reset_index()
            # to calculate cotisation, interets, dividendes,retenue_impots
            type_agg = df_filtered.groupby('type_de_transaction').agg(montant_de_l_operation=
                                                                      ('montant_de_l_operation', 'sum'))
            balance = None  # set to None, so that % not shown in the view with disnat-summary-table.html
            #######################################
            # Calculate profits
            #######################################
            df_numero_id = df_to_date_max.groupby('numero_id').filter(lambda x: len(x) > 1)
            profits_agg_temp = df_numero_id.groupby('numero_id', as_index=False).agg(
                montant_total=('montant_de_l_operation', 'sum'),
                date=('date_de_reglement', 'last')
            )
            profits_agg = profits_agg_temp[profits_agg_temp.date.between(self.date_min_filter , self.date_max_filter)].reset_index()
            profits = profits_agg['montant_total'].sum()
        else:
            balance = self.df['montant_de_l_operation'].sum()
            # to calculate cotisation, interets, dividendes,retenue_impots
            type_agg = self.df.groupby('type_de_transaction').agg(montant_total=('montant_de_l_operation', 'sum'))
            #######################################
            # Calculate profits
            #######################################
            # filter for items with numero_id appearing more than once - should be at least 1 ACHAT
            filtered_df = self.df.groupby('numero_id').filter(lambda x: len(x) > 1)

            profits_agg = filtered_df.groupby('numero_id').agg(montant_total=('montant_de_l_operation', 'sum'))
            profits = profits_agg['montant_total'].sum()
        type_de_transaction = list(type_agg.index)
        cotisations = type_agg.loc['COTISATION'].item() if 'COTISATION' in type_de_transaction else 0
        retraits = type_agg.loc['RÉSILIATION'].item() if 'RÉSILIATION' in type_de_transaction else 0
        investissement = cotisations + retraits
        interets = type_agg.loc['INTÉRÊTS'].item() if 'INTÉRÊTS' in type_de_transaction else 0
        index_dividendes = [i for i in range(len(type_de_transaction)) if
                            type_de_transaction[i].startswith('DIVIDENDE')]
        dividendes = type_agg.iloc[index_dividendes].sum().item()
        retenue_impots = type_agg.loc["RETENUE D'IMPÔT"].item() if "RETENUE D'IMPÔT" in type_de_transaction else 0

        total_revenue = profits + retenue_impots + dividendes + interets

        # Calculate % profits if full table, not for partial
        days_total = today - self.first_date
        days_book = self.last_date - self.first_date
        if self.full:
            if days_total.days > 0 and cotisations > 0:
                percent_profits_today = Decimal((profits + retenue_impots + dividendes + interets) * 100 * 365 / (
                            days_total.days * cotisations)).quantize(Decimal("1.00"))
            else:
                percent_profits_today = Decimal(0).quantize(Decimal("1.00"))
            if days_book.days > 0 and cotisations > 0:
                percent_profits_book = Decimal((profits + retenue_impots + dividendes + interets) * 100 * 365 / (
                        days_book.days * cotisations)).quantize(Decimal("1.00"))
            else:
                percent_profits_book = Decimal(0).quantize(Decimal("1.00"))
        else:
            percent_profits_book = None
            percent_profits_today = None

        summary = {
            'first_date': self.first_date,
            'last_date': self.last_date,
            "today": today,
            "days_book": days_book.days,
            "days_total": days_total.days,
            'balance': balance,
            'cotisations': cotisations,
            'retraits': retraits,
            'investissement': investissement,
            'interets': interets,
            'dividendes': dividendes,
            'retenue_impots': retenue_impots,
            'profits': profits,
            'percent_profits_today': percent_profits_today,
            'percent_profits_book': percent_profits_book,
            'total_revenue': total_revenue
        }
        return summary